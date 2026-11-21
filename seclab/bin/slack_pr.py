#!/usr/bin/env python3
"""slack_pr.py — avisa a Slack cuando el Security Gate BLOQUEA un PR.

Lo llama el workflow gate.yml. Todo llega por variables de entorno:
  SLACK_WEBHOOK_URL   (secret)  Incoming Webhook del canal de alertas
  GRAFANA_URL         (var)     link al tablero de PRs (opcional)
  SLACK_CHANNEL_URL   (var)     link al canal de Slack (opcional)
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


def main():
    hook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not hook:
        print("Sin SLACK_WEBHOOK_URL: se omite el aviso a Slack.")
        return
    env = os.environ.get
    report = {}
    try:
        with open(env("REPORT", "")) as f:
            report = json.load(f)
    except Exception:
        pass
    fs = report.get("findings", [])
    total = report.get("total", len(fs))
    sev = {}
    for f in fs:
        s = str(f.get("severity", "?")).upper()
        sev[s] = sev.get(s, 0) + 1
    resumen = " · ".join("%s %d" % (k, v) for k, v in sorted(sev.items(), key=lambda x: ORDER.get(x[0], 9)))
    top = sorted(fs, key=lambda f: ORDER.get(str(f.get("severity", "")).upper(), 9))[:3]
    top_txt = "\n".join("• `%s` — %s (%s)" % (esc(f.get("rule", "?")), esc(f.get("loc", "?")), esc(f.get("severity", "?"))) for f in top)

    links = ["<%s|🔗 Pull Request>" % env("PR_URL", ""), "<%s|⚙️ Run del gate>" % env("RUN_URL", "")]
    if env("GRAFANA_URL"):
        links.append("<%s|📊 Tablero Grafana>" % env("GRAFANA_URL"))
    if env("SLACK_CHANNEL_URL"):
        links.append("<%s|💬 Canal>" % env("SLACK_CHANNEL_URL"))

    head = "🚫 PR #%s bloqueado por el Security Gate" % env("PR_NUM", "?")
    body = "*%s*\n👤 Alumno: *%s*\n🔎 Hallazgos: *%s*%s" % (
        esc(env("PR_TITLE", "")), esc(env("PR_AUTHOR", "?")), total, ("  (%s)" % resumen) if resumen else "")
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": head, "emoji": True}},
        {"type": "section", "text": {"type": "mrkdwn", "text": body}},
    ]
    if top_txt:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Más graves:*\n" + top_txt}})
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "   |   ".join(links)}})
    blocks.append({"type": "divider"})

    data = json.dumps({"text": head, "blocks": blocks}).encode("utf-8")
    req = urllib.request.Request(hook, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        print("Slack:", r.status)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # el aviso nunca debe tumbar el gate
        print("::warning::No se pudo avisar a Slack: %s" % type(e).__name__)
    sys.exit(0)
