#!/usr/bin/env bash
# Demo: un secreto borrado del archivo sigue en el historial de Git.
# Crea un repositorio temporal; no toca ningún repositorio real.
# Requiere: git y gitleaks (v8.19 o superior).
set -u

pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }

DIR=$(mktemp -d)
cd "$DIR" || exit 1
git init -q -b main
git config user.email "demo@ucp.local"
git config user.name "Demo UCP"

# Token FALSO con el formato de un token clásico de GitHub. Se arma en tiempo de
# ejecución para que este script no contenga un patrón de secreto.
TOKEN_FALSO="ghp""_$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 36)"

pausa "1. Un desarrollador sube la configuración con un token"
cat > config.py <<EOF
GITHUB_TOKEN = "$TOKEN_FALSO"
API_URL = "https://api.ejemplo.co"
EOF
git add config.py && git commit -q -m "configuración inicial"
git log --oneline

pausa "2. Se da cuenta y lo borra en el siguiente commit"
cat > config.py <<'EOF'
import os
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
API_URL = "https://api.ejemplo.co"
EOF
git commit -q -am "quitar token del código"
git log --oneline
echo; echo "Archivo actual:"; cat config.py

pausa "3. ¿Hay secretos en los archivos actuales? (gitleaks dir)"
gitleaks dir . --no-banner; echo "código de salida: $?"

pausa "4. ¿Y en el historial? (gitleaks git)"
gitleaks git . --no-banner -v; echo "código de salida: $?"

pausa "5. Cualquiera que clone el repo lo recupera"
git show HEAD~1:config.py

pausa "6. Control: hook pre-commit que bloquea el commit"
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
gitleaks git --pre-commit --staged --no-banner --redact || {
  echo "Commit bloqueado: gitleaks encontró un posible secreto."; exit 1; }
EOF
chmod +x .git/hooks/pre-commit
echo "OTRO_TOKEN = \"$TOKEN_FALSO\"" >> config.py
git add config.py
git commit -m "intento de subir otro token"; echo "código de salida: $?"

pausa "Fin. Lección: rotar el token (revocarlo) siempre; borrar el commit no basta."
echo "Repositorio temporal: $DIR (se puede borrar)"
