#!/usr/bin/env bash
# Demo (caso Shai-Hulud): npm ejecuta código de terceros al instalar, y por defecto en silencio.
# Todo corre dentro de un contenedor desechable SIN RED, con tokens falsos.
set -u
cd "$(dirname "$0")"
IMG="node:22-slim"
NPM="npm install --install-links --no-audit --no-fund"
EVIDENCIA='echo; if [ -f /tmp/postinstall-ejecutado.txt ]; then echo "EVIDENCIA: $(cat /tmp/postinstall-ejecutado.txt)"; else echo "Sin evidencia: ningún script se ejecutó."; fi'

pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }

correr() {
  docker run --rm --network none \
    -e NPM_TOKEN="npm_FALSO_DE_DEMO" -e GITHUB_TOKEN="FALSO_DE_DEMO" \
    -v "$PWD":/demo -w /demo/proyecto "$IMG" \
    sh -c "rm -rf node_modules package-lock.json; $1; $EVIDENCIA; rm -rf node_modules package-lock.json"
}

pausa "1. Instalación normal. Miren la salida: ¿se ejecutó algo?"
correr "$NPM"

pausa "2. Lo mismo, pero pidiendo a npm que muestre los scripts (--foreground-scripts)"
correr "$NPM --foreground-scripts"

pausa "3. Control: instalar sin ejecutar scripts (--ignore-scripts)"
correr "$NPM --ignore-scripts"

pausa "4. Control como política del proyecto"
cat <<'EOF'
# .npmrc del proyecto
ignore-scripts=true

# En CI: npm ci (instala exactamente el package-lock.json y verifica los hashes de integridad)
# Para auditar qué paquetes tienen scripts de instalación:
#   npm query ':attr(scripts, [postinstall])'
EOF

pausa "Fin. Otras medidas: tokens de corta vida y mínimo privilegio, trusted publishing, esperar días antes de adoptar versiones nuevas."
