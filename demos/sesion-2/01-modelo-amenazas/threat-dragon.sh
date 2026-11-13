#!/usr/bin/env bash
# Levanta OWASP Threat Dragon 2.6 en http://127.0.0.1:8080 (solo esta máquina).
# Uso: bash demos/sesion-2/01-modelo-amenazas/threat-dragon.sh [parar]
set -u
NOMBRE=ucp-threat-dragon
if [ "${1:-}" = parar ]; then docker rm -f $NOMBRE >/dev/null && echo "Threat Dragon detenido"; exit 0; fi
docker rm -f $NOMBRE >/dev/null 2>&1
# Llaves aleatorias en cada arranque: nunca llaves fijas en un script.
docker run -d --name $NOMBRE -p 127.0.0.1:8080:3000 \
  -e NODE_ENV=production -e SERVER_API_PROTOCOL=http \
  -e ENCRYPTION_KEYS="[{\"isPrimary\": true, \"id\": 0, \"value\": \"$(openssl rand -hex 16)\"}]" \
  -e ENCRYPTION_JWT_SIGNING_KEY="$(openssl rand -hex 32)" \
  -e ENCRYPTION_JWT_REFRESH_SIGNING_KEY="$(openssl rand -hex 32)" \
  owasp/threat-dragon:stable >/dev/null || exit 1
for _ in $(seq 60); do curl -sf -o /dev/null http://127.0.0.1:8080/ && break; sleep 2; done
cat <<TXT
Threat Dragon listo: http://127.0.0.1:8080
  1. «Login to Local Session» (no pide cuenta; los modelos se guardan como archivos JSON).
  2. «Open an existing threat model» y arrastren al recuadro:
       $(cd "$(dirname "$0")" && pwd)/tienda-ucp.json
     o «Create a new, empty threat model» para el Lab 1.
  3. Guardar = descargar el JSON. Súbanlo a la carpeta del equipo en el repositorio.
Para detenerlo: bash $0 parar
TXT
