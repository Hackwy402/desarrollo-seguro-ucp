# Tablero de PRs del Security Gate (Grafana)

Dos contenedores en una red docker privada (`seclab`):

- **seclab-data** (`collector/collector.py`): cada ciclo hace 3 llamadas a la
  API de GitHub (runs del gate, PRs y comentarios del gate), arma un registro
  por PR (alumno, estado del gate, hallazgos, severidades, CVE, intentos,
  minutos hasta verde) y lo sirve como JSON. Quien mira el tablero nunca le
  pega a GitHub.
- **seclab-grafana**: Grafana (puerto 3000, lectura anonima) con el tablero
  `dashboards/pr-gate.json`: contadores, ALARMAS (PRs abiertos que no pasan),
  hallazgos por alumno, todos los PRs e historial de runs.

Levantar:  `bash run.sh`   (genera la clave de admin en `.env`, no versionado)

Sin token el colector refresca cada 5 min (limite de 60 req/h de GitHub).
Para refrescar cada 30 s agrega a `.env` un token de solo lectura:

    GITHUB_TOKEN=github_pat_...      # fine-grained, "Public repositories (read-only)"

Avisos al canal: el step "Avisar al canal" de `gate.yml` usa
`seclab/bin/notify_pr.py` y necesita:

    gh secret   set DISCORD_WEBHOOK_URL          # webhook del canal de Discord
    gh variable set GRAFANA_URL -b 'http://<host>:3000/d/seclab-pr-gate'
    gh variable set GATE_CHANNEL_URL -b 'https://discord.com/channels/<servidor>/<canal>'

(Tambien acepta `SLACK_WEBHOOK_URL` si se quiere avisar a Slack.)
