#!/usr/bin/env python3
"""Colector del tablero de PRs del Security Gate.

Cada ciclo hace 3 llamadas a la API de GitHub (runs del gate, PRs y
comentarios del gate), arma un registro por PR y lo sirve como JSON en :8080
para Grafana. Los que miran el tablero nunca le pegan a GitHub.

Entorno: REPO (owner/repo), GITHUB_TOKEN (opcional: sube el limite de 60 a
5000 req/h), INTERVAL (segundos; por defecto 300 sin token, 30 con token).
"""
import http.server
import json
import os
import re
import threading
import time
import urllib.request
from datetime import datetime, timezone

REPO = os.environ.get("REPO", "Hackwy402/desarrollo-seguro-ucp")
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
INTERVAL = int(os.environ.get("INTERVAL") or (30 if TOKEN else 300))
OUT = os.environ.get("OUT", "/data")
API = "https://api.github.com/repos/" + REPO
MARKER = "<!-- seclab-gate-ai -->"
SEVS = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


def gh(path):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "seclab-collector"})
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) if s else None


def parse_comment(body):
    """-> dict(hallazgos, sev counts, cves, incompleto) a partir del comentario del gate."""
    d = {"hallazgos": None, "incompleto": False, "cves": [], **{s: 0 for s in SEVS}}
    if "No se genero reporte" in body:
        d["incompleto"] = True
        return d
    m = re.search(r"Bloqueado:\s*(\d+)\s*hallazgo", body)
    if m:
        d["hallazgos"] = int(m.group(1))
    elif "Sin hallazgos" in body:
        d["hallazgos"] = 0
    rows = []
    for line in body.split("\n"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 4 and c[1].upper() in SEVS:
            rows.append((c[1].upper(), c[2]))
            d[c[1].upper()] += 1
    rows.sort(key=lambda r: SEVS.index(r[0]))
    seen = []
    for _, rule in rows:
        if rule not in seen:
            seen.append(rule)
    d["cves"] = seen
    return d


def build():
    runs = gh("/actions/workflows/gate.yml/runs?event=pull_request&per_page=100").get("workflow_runs", [])
    pulls = gh("/pulls?state=all&per_page=100&sort=created&direction=desc")
    comments = gh("/issues/comments?sort=updated&direction=desc&per_page=100")

    gate_comment = {}
    for c in comments:
        if MARKER in (c.get("body") or ""):
            n = int(c["issue_url"].rsplit("/", 1)[1])
            gate_comment.setdefault(n, parse_comment(c["body"]))

    by_branch = {}
    for r in runs:
        by_branch.setdefault(r["head_branch"], []).append(r)

    prs, hist = [], []
    for p in pulls:
        rs = sorted(by_branch.get(p["head"]["ref"], []), key=lambda r: r["created_at"])
        # solo runs de la vida de ESTE PR (una rama puede reutilizarse)
        lo, hi = p["created_at"], p.get("closed_at") or "9999"
        rs = [r for r in rs if lo[:16] <= r["created_at"][:16] and r["created_at"] <= hi] or \
             [r for r in rs if r["head_sha"] == p["head"]["sha"]]
        if not rs:
            continue
        last = rs[-1]
        concl = last.get("conclusion") or last.get("status")
        fails = [r for r in rs if r.get("conclusion") == "failure"]
        oks = [r for r in rs if r.get("conclusion") == "success"]
        c = gate_comment.get(p["number"], parse_comment(""))
        estado_pr = "merged" if p.get("merged_at") else p["state"]
        if concl == "failure":
            gate = "INCOMPLETO" if c["incompleto"] else "BLOQUEADO"
        elif concl == "success":
            gate = "CORREGIDO" if fails else "PASA"
        else:
            gate = "CORRIENDO"
        min_verde = None
        if fails and oks:
            first_ok = next((r for r in oks if r["created_at"] > fails[0]["created_at"]), None)
            if first_ok:
                min_verde = round((ts(first_ok["updated_at"]) - ts(fails[0]["created_at"])).total_seconds() / 60, 1)
        rojo = gate == "BLOQUEADO"
        rec = {
            "pr": p["number"], "titulo": p["title"], "alumno": p["user"]["login"],
            "rama": p["head"]["ref"], "estado_pr": estado_pr, "gate": gate,
            "hallazgos": (c["hallazgos"] or 0) if rojo else 0,
            "criticos": c["CRITICAL"] if rojo else 0, "altos": c["HIGH"] if rojo else 0,
            "medios": c["MEDIUM"] if rojo else 0, "bajos": c["LOW"] if rojo else 0,
            "cves": (", ".join(c["cves"][:4]) + (" (+%d)" % (len(c["cves"]) - 4) if len(c["cves"]) > 4 else "")) if rojo else "",
            "intentos": len(rs), "fallos": len(fails), "min_a_verde": min_verde,
            "abierto": p["created_at"], "ultimo_run": last["updated_at"],
            "pr_url": p["html_url"], "run_url": last["html_url"],
        }
        prs.append(rec)
        for r in rs:
            hist.append({"fecha": r["created_at"], "pr": p["number"], "alumno": p["user"]["login"],
                         "titulo": p["title"], "resultado": r.get("conclusion") or r.get("status"),
                         "duracion_s": int((ts(r["updated_at"]) - ts(r["created_at"])).total_seconds()),
                         "pr_url": p["html_url"], "run_url": r["html_url"]})

    prs.sort(key=lambda x: x["ultimo_run"], reverse=True)
    hist.sort(key=lambda x: x["fecha"], reverse=True)
    alarmas = [x for x in prs if x["gate"] in ("BLOQUEADO", "INCOMPLETO") and x["estado_pr"] == "open"]
    mins = [x["min_a_verde"] for x in prs if x["min_a_verde"] is not None]
    resumen = [{
        "alumnos": len({x["alumno"] for x in prs}), "prs": len(prs),
        "abiertos": sum(1 for x in prs if x["estado_pr"] == "open"),
        "bloqueados": len(alarmas),
        "corregidos": sum(1 for x in prs if x["gate"] == "CORREGIDO"),
        "hallazgos_abiertos": sum(x["hallazgos"] or 0 for x in alarmas),
        "criticos_abiertos": sum(x["criticos"] for x in alarmas),
        "runs": len(hist), "runs_fallidos": sum(1 for h in hist if h["resultado"] == "failure"),
        "min_a_verde_prom": round(sum(mins) / len(mins), 1) if mins else None,
        "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cada_s": INTERVAL, "error": "",
    }]
    return {"prs": prs, "alarmas": alarmas, "runs": hist, "resumen": resumen}


def write(name, obj):
    tmp = os.path.join(OUT, name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, os.path.join(OUT, name + ".json"))


def loop(once=False):
    while True:
        try:
            for k, v in build().items():
                write(k, v)
            print(time.strftime("%H:%M:%S"), "ok", flush=True)
        except Exception as e:
            print(time.strftime("%H:%M:%S"), "error:", repr(e)[:200], flush=True)
            try:  # conserva los datos previos, solo marca el error
                p = os.path.join(OUT, "resumen.json")
                r = json.load(open(p))
                r[0]["error"] = type(e).__name__ + ": " + str(e)[:120]
                write("resumen", r)
            except Exception:
                pass
        if once:
            return
        time.sleep(INTERVAL)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=OUT, **k)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if os.environ.get("ONCE"):
        loop(once=True)
    else:
        threading.Thread(target=loop, daemon=True).start()
        http.server.ThreadingHTTPServer(("0.0.0.0", 8080), H).serve_forever()
