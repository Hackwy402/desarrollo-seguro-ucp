#!/usr/bin/env bash
# Sesión 3: Semgrep con reglas propias sobre la API de la sesión 1.
set -u
cd "$(dirname "$0")" || exit 1
API=../../sesion-1/03-api
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }

pausa "1. Una regla de Semgrep: el patrón de la falla abierta"
sed -n '/id: falla-abierta/,/return True/p' reglas-principios.yml

pausa "2. Escanear la versión insegura"
semgrep scan --config reglas-principios.yml --metrics=off "$API/app_insegura.py"

pausa "3. Escanear la versión segura"
semgrep scan --config reglas-principios.yml --metrics=off "$API/app_segura.py"

pausa "Fin. Con --error, el código de salida permite bloquear un pull request (sesión 4)."
