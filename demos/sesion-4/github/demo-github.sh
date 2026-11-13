#!/usr/bin/env bash
# Demo: el pipeline de seguridad bloquea un pull request inseguro en GitHub.
# Crea un repositorio PRIVADO en la cuenta del docente (requiere gh autenticado).
# Uso: bash demos/sesion-4/github/demo-github.sh [nombre-del-repo]
set -u
REPO="${1:-demo-facturas-ucp}"
DEMOS="$(cd "$(dirname "$0")/../.." && pwd)"
API="$DEMOS/sesion-1/03-api"
GH="$DEMOS/sesion-4/github"
REGLAS="$DEMOS/sesion-3/01-semgrep/reglas-principios.yml"
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }

DIR=$(mktemp -d); cd "$DIR" || exit 1
git init -q -b main

pausa "1. Repositorio con la versión SEGURA de la API y el pipeline de seguridad"
cp "$API/app_segura.py" app.py
cp "$API/permisos.py" "$API/requirements.txt" "$API/Dockerfile" .
sed -i.bak 's/app_segura.py permisos.py/app.py permisos.py/; s/"app_segura.py"/"app.py"/' Dockerfile && rm Dockerfile.bak
mkdir -p .github/workflows .semgrep
cp "$GH/seguridad.yml" .github/workflows/
cp "$GH/dependabot.yml" .github/
cp "$REGLAS" .semgrep/
git add -A && git commit -q -m "API de facturas con pipeline de seguridad"
ls -R . | grep -v "^$" | head -20

pausa "2. Crear el repositorio privado en GitHub y subir main"
gh repo create "$REPO" --private --source . --push

pausa "3. Proteger main: exigir que los tres controles pasen antes de fusionar"
echo "En GitHub: Settings > Branches > Add rule > main > Require status checks:"
echo "  - Secretos en el historial (gitleaks)"
echo "  - Análisis estático (Semgrep)"
echo "  - Configuración del Dockerfile (Trivy)"
echo "(Se hace desde la interfaz para que los estudiantes lo vean.)"

pausa "4. Un desarrollador abre un PR «rápido» con la versión insegura"
git checkout -q -b arreglo-rapido
cp "$API/app_insegura.py" app.py
cp "$API/Dockerfile.inseguro" Dockerfile
sed -i.bak 's/app_insegura.py/app.py/' Dockerfile && rm Dockerfile.bak
# Token FALSO con formato de GitHub, armado en tiempo de ejecución.
echo "GITHUB_TOKEN = \"ghp""_$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 36)\"" > config.py
git add -A && git commit -q -m "arreglo rápido para producción"
echo "Si GitHub rechaza el push por «push protection», esa es la primera lección: la plataforma también es un control."
git push -q -u origin arreglo-rapido
gh pr create --title "Arreglo rápido" --body "Urgente, sin tiempo para revisión." --head arreglo-rapido

pausa "5. Ver cómo fallan los controles"
gh pr checks --watch || true

pausa "Fin. Abran el PR en el navegador y lean cada hallazgo con los estudiantes."
gh pr view --web
echo "Repositorio temporal local: $DIR"
echo "Para borrar el repositorio de GitHub al final: gh repo delete $REPO --yes"
