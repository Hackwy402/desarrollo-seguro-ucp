#!/usr/bin/env bash
# Levanta el tablero de PRs: colector (seclab-data) + Grafana (seclab-grafana).
# Opcional en .env:  GITHUB_TOKEN=<token de solo lectura>  -> refresco cada 30 s.
set -euo pipefail
cd "$(dirname "$0")"
GRAFANA_IMAGE="${GRAFANA_IMAGE:-grafana/grafana:12.4.15}"
[ -f .env ] || { umask 077; echo "GF_SECURITY_ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 28)" > .env; }
sudo docker network create seclab >/dev/null 2>&1 || true
sudo docker rm -f seclab-grafana seclab-data >/dev/null 2>&1 || true
sudo docker volume create seclab-grafana-data >/dev/null
sudo docker run -d --name seclab-data --restart unless-stopped --memory 128m --network seclab \
  --env-file .env -e REPO="${REPO:-Hackwy402/desarrollo-seguro-ucp}" -e PYTHONUNBUFFERED=1 \
  -v "$PWD/collector:/app:ro,z" -v seclab-pr-data:/data \
  python:3.12-alpine python /app/collector.py
sudo docker run -d --name seclab-grafana --restart unless-stopped --memory 512m --network seclab \
  -p 3000:3000 --env-file .env \
  -e GF_INSTALL_PLUGINS=yesoreyeram-infinity-datasource \
  -e GF_AUTH_ANONYMOUS_ENABLED=true -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \
  -e GF_USERS_ALLOW_SIGN_UP=false -e GF_ANALYTICS_REPORTING_ENABLED=false \
  -e GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/var/lib/grafana/dashboards/pr-gate.json \
  -v seclab-grafana-data:/var/lib/grafana \
  -v "$PWD/provisioning:/etc/grafana/provisioning:ro,z" \
  -v "$PWD/dashboards:/var/lib/grafana/dashboards:ro,z" \
  "$GRAFANA_IMAGE"
