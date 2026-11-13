#!/usr/bin/env bash
# Escaneo dinámico (DAST) de la API con OWASP ZAP, dentro de la red de Docker del laboratorio.
# Solo contra la billetera local. Uso: bash demos/sesion-3/02-billetera/zap/zap-api.sh [insegura|segura]
set -u
cd "$(dirname "$0")/.." || exit 1
OBJ=${1:-insegura}
docker compose up -d "$OBJ" >/dev/null 2>&1
for _ in $(seq 30); do docker compose exec -T "$OBJ" python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:5000/salud")' 2>/dev/null && break; sleep 1; done
TOKEN=$(docker compose exec -T "$OBJ" python -c 'import urllib.request,json
r=urllib.request.Request("http://127.0.0.1:5000/api/login", json.dumps({"usuario":"ana","clave":"Cafetal-de-Risaralda-2026"}).encode(), {"Content-Type":"application/json"})
print(json.load(urllib.request.urlopen(r))["token"])')
mkdir -p zap/reportes && chmod 777 zap/reportes
sed "s#http://insegura:5000#http://$OBJ:5000#" zap/openapi.yaml > zap/reportes/openapi.yaml
docker run --rm --network billetera-ucp_default -v "$PWD/zap/reportes":/zap/wrk:rw \
  -e ZAP_AUTH_HEADER=Authorization -e ZAP_AUTH_HEADER_VALUE="Bearer $TOKEN" \
  ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py -t /zap/wrk/openapi.yaml -f openapi \
  -r "zap-$OBJ.html" -J "zap-$OBJ.json" -I -l WARN
echo "Reporte: demos/sesion-3/02-billetera/zap/reportes/zap-$OBJ.html"
