#!/usr/bin/env python3
"""notify_pr.py — avisa a Discord y/o Slack cuando el Security Gate BLOQUEA un PR.

Lo llama el workflow gate.yml. Todo llega por variables de entorno:
  DISCORD_WEBHOOK_URL (secret)  webhook del canal de Discord
  SLACK_WEBHOOK_URL   (secret)  Incoming Webhook de Slack (opcional)
  GRAFANA_URL         (var)     link al tablero de PRs (opcional)
  CHANNEL_URL         (var)     link al canal de alertas (opcional)
  PR_URL, PR_NUM, PR_TITLE, PR_AUTHOR, RUN_URL, REPORT
Nunca rompe el gate: ante cualquier error avisa y sale con 0.
"""
import json
import os
import sys
import urllib.request

ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "User-Agent": "seclab-gate/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status


def main():
    env = os.environ.get
    discord = env("DISCORD_WEBHOOK_URL", "").strip()
    slack = env("SLACK_WEBHOOK_URL", "").strip()
    if not (discord or slack):
        print("Sin DISCORD_WEBHOOK_URL ni SLACK_WEBHOOK_URL: se omite el aviso.")
        return
    report = {}
    try:
        with open(env("REPORT", "")) as f:
            report = json.load(f)
    except Exception:
        pass
    fs = report.get("findings", [])
    total = report.get("total", len(fs)) if report else "escaneo incompleto"
    sev = {}
    for f in fs:
        s = str(f.get("severity", "?")).upper()
        sev[s] = sev.get(s, 0) + 1
    resumen = " · ".join("%s %d" % (k, v) for k, v in sorted(sev.items(), key=lambda x: ORDER.get(x[0], 9)))
    top = sorted(fs, key=lambda f: ORDER.get(str(f.get("severity", "")).upper(), 9))[:3]
    head = "🚫 PR #%s bloqueado por el Security Gate" % env("PR_NUM", "?")
    links = [("🔗 Pull Request", env("PR_URL", "")), ("⚙️ Run del gate", env("RUN_URL", "")),
             ("📊 Tablero Grafana", env("GRAFANA_URL", "")), ("💬 Canal", env("CHANNEL_URL", ""))]
    links = [(t, u) for t, u in links if u]

    if discord:
        fields = [
            {"name": "👤 Alumno", "value": str(env("PR_AUTHOR", "?")), "inline": True},
            {"name": "🔎 Hallazgos", "value": "%s%s" % (total, ("\n%s" % resumen) if resumen else ""), "inline": True},
        ]
        if top:
            fields.append({"name": "Más graves", "value": "\n".join(
                "• `%s` — %s (%s)" % (f.get("rule", "?"), f.get("loc", "?"), f.get("severity", "?")) for f in top)[:1000]})
        fields.append({"name": "Enlaces", "value": "  |  ".join("[%s](%s)" % (t, u) for t, u in links)})
        payload = {"username": "Security Gate", "allowed_mentions": {"parse": []}, "embeds": [{
            "title": head, "url": env("PR_URL", ""), "description": str(env("PR_TITLE", ""))[:300],
            "color": 0xE01E5A, "fields": fields}]}
        print("Discord:", post(discord + ("&" if "?" in discord else "?") + "wait=true", payload))

    if slack:
        top_txt = "\n".join("• `%s` — %s (%s)" % (esc(f.get("rule", "?")), esc(f.get("loc", "?")), esc(f.get("severity", "?"))) for f in top)
        body = "*%s*\n👤 Alumno: *%s*\n🔎 Hallazgos: *%s*%s" % (
            esc(env("PR_TITLE", "")), esc(env("PR_AUTHOR", "?")), total, ("  (%s)" % resumen) if resumen else "")
        blocks = [{"type": "header", "text": {"type": "plain_text", "text": head, "emoji": True}},
                  {"type": "section", "text": {"type": "mrkdwn", "text": body}}]
        if top_txt:
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Más graves:*\n" + top_txt}})
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "   |   ".join("<%s|%s>" % (u, t) for t, u in links)}})
        print("Slack:", post(slack, {"text": head, "blocks": blocks}))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # el aviso nunca debe tumbar el gate
        print("::warning::No se pudo enviar el aviso: %s" % type(e).__name__)
    sys.exit(0)
