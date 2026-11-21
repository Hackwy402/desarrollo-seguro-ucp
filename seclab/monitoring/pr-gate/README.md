# Tablero de PRs del Security Gate (Grafana)

Grafana lee los runs del workflow `gate.yml` directo de la API de GitHub
(datasource Infinity): no hay que abrir puertos para que Actions empuje datos.

- `run.sh` — levanta el contenedor `seclab-grafana` en el puerto 3000
  (genera la clave de admin en `.env`, que NO se versiona).
- `dashboards/pr-gate.json` — tablero: PRs bloqueados, runs en verde,
  tabla de PRs que fallaron (con link a GitHub) e historial.
- Lectura anónima (rol Viewer); editar requiere el usuario admin.

Avisos a Slack: el step "Avisar a Slack" de `gate.yml` usa
`seclab/bin/slack_pr.py` y necesita:

    gh secret   set SLACK_WEBHOOK_URL            # Incoming Webhook del canal
    gh variable set GRAFANA_URL -b 'http://<host>:3000/d/seclab-pr-gate'
    gh variable set SLACK_CHANNEL_URL -b 'https://<workspace>.slack.com/archives/<ID>'   # opcional
