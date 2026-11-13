#!/usr/bin/env bash
# Corre las pruebas de las katas en un contenedor sin red.
# Uso:  bash katas.sh              todas las katas
#       bash katas.sh a05_sql      solo una (a01_acceso, a02_config, a05_sql, a05_xss,
#                                   a05_comandos, a06_diseno, a10_excepciones)
#       APP_FILE=/app/.soluciones/app.py bash katas.sh    (docente: verificar la solución)
set -u
cd "$(dirname "$0")" || exit 1
docker image inspect ucp-tienda >/dev/null 2>&1 || docker build -q -t ucp-tienda . >/dev/null
FILTRO=()
[ $# -gt 0 ] && FILTRO=(tests/test_"$1".py)
docker run --rm --network none -v "$PWD":/app:ro -e APP_FILE="${APP_FILE:-/app/app.py}" \
  -e PYTHONDONTWRITEBYTECODE=1 ucp-tienda \
  python -m pytest -p no:cacheprovider -q --no-header -rN --tb=line "${FILTRO[@]:-tests}" 2>&1 \
  | sed -E 's#^/app/tests/##'
