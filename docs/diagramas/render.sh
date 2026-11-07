#!/usr/bin/env bash
# Renderiza todos los .dot de esta carpeta a PNG (200 dpi) y SVG, con Graphviz en un contenedor.
# Usa la imagen de la demo 8 (ucp-pytm), que trae graphviz y fuentes DejaVu.
set -eu
cd "$(dirname "$0")"
docker image inspect ucp-pytm >/dev/null 2>&1 || docker build -q -t ucp-pytm ../../demos/sesion-1/08-modelo-amenazas >/dev/null
docker run --rm --network none -v "$PWD":/d -w /d ucp-pytm sh -c '
  for f in *.dot; do
    n="${f%.dot}"
    dot -Tpng -Gdpi=200 "$f" -o "png/$n.png"
    dot -Tsvg "$f" -o "svg/$n.svg"
    echo "  $n"
  done'
