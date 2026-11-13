#!/usr/bin/env bash
# Sesión 3: Semgrep con reglas propias sobre la API de la sesión 1 y la Billetera UCP.
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

pausa "4. Reglas de la billetera: tokens, contraseñas, cifrado, secretos y asignación masiva"
semgrep scan --config reglas-billetera.yml --metrics=off ../02-billetera/app.py

pausa "5. La solución de la billetera"
[ -f ../02-billetera/.soluciones/app.py ] && semgrep scan --config reglas-billetera.yml --metrics=off ../02-billetera/.soluciones/app.py

pausa "6. Las reglas de la comunidad sobre su propio proyecto (Lab 2)"
echo "   semgrep scan --config p/python --config p/owasp-top-ten --config reglas-billetera.yml --metrics=off RUTA/A/SU/PROYECTO"

pausa "Fin. Con --error, el código de salida permite bloquear un pull request (sesión 4)."
