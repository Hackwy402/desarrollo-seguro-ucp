#!/usr/bin/env bash
# Corre las pruebas de las katas en un contenedor sin red.
# Uso:  bash katas.sh              todas las katas
#       bash katas.sh v9_jwt       solo una (v6_claves, v6_fuerza, v9_jwt, api1_bola,
#                                   api3_propiedades, api4_recursos, v11_cripto)
#       APP_FILE=/app/.soluciones/app.py bash katas.sh    (docente: verificar la solución)
set -u
cd "$(dirname "$0")" || exit 1
docker image inspect ucp-billetera >/dev/null 2>&1 || docker build -q -t ucp-billetera . >/dev/null
FILTRO=()
[ $# -gt 0 ] && FILTRO=(tests/test_"$1".py)
docker run --rm --network none -v "$PWD":/app:ro -e APP_FILE="${APP_FILE:-/app/app.py}" \
  -e PYTHONDONTWRITEBYTECODE=1 ucp-billetera \
  python -m pytest -p no:cacheprovider -q --no-header -rN --tb=line "${FILTRO[@]:-tests}" 2>&1 \
  | sed -E 's#^/app/tests/##'
