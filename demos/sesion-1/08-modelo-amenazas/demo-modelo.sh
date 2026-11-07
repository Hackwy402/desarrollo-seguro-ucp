#!/usr/bin/env bash
# Demo 8: modelo de amenazas como código con OWASP pytm, en un contenedor.
# Genera el diagrama de flujo de datos (dfd.png) y un resumen de amenazas STRIDE.
set -u
cd "$(dirname "$0")" || exit 1
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }
pytm() { docker run --rm --network none -v "$PWD":/modelo ucp-pytm sh -c "$1"; }

pausa "0. Construir la imagen con pytm y graphviz (una sola vez)"
docker build -q -t ucp-pytm . >/dev/null && echo "   imagen ucp-pytm lista"

pausa "1. Pregunta 1: ¿en qué estamos trabajando? El modelo es código Python versionado en git"
sed -n '/# Límites de confianza/,/^if __name__/p' modelo.py | grep -vE '^if __name__' | head -40

pausa "2. Generar el diagrama de flujo de datos desde el código"
pytm "python modelo.py --dfd | dot -Tpng -Gdpi=200 -o dfd.png" && echo "   dfd.png generado"
command -v open >/dev/null && open dfd.png || echo "   Abran demos/sesion-1/08-modelo-amenazas/dfd.png"

pausa "3. Pregunta 2: ¿qué puede salir mal? Amenazas candidatas y priorización"
pytm "python reporte.py"

pausa "Fin. Preguntas 3 y 4: qué haremos (los controles de la demo 3) y si lo hicimos bien (verificación, 14 nov)."
