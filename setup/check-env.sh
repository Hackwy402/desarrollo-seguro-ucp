#!/usr/bin/env bash
# Verifica el entorno de laboratorio del curso Desarrollo Seguro – UCP.
# Uso: bash setup/check-env.sh

fail=0

ok()   { printf '  [OK]    %-14s %s\n' "$1" "$2"; }
bad()  { printf '  [FALTA] %-14s %s\n' "$1" "$2"; fail=1; }
warn() { printf '  [AVISO] %-14s %s\n' "$1" "$2"; }

check_cmd() {
  local name="$1" cmd="$2" ver_cmd="$3"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "$name" "$($ver_cmd 2>/dev/null | head -n 1)"
  else
    bad "$name" "no se encontró '$cmd'"
  fi
}

echo "== Sistema =="
if [ -r /etc/os-release ]; then
  . /etc/os-release
  ok "SO" "$PRETTY_NAME ($(uname -m))"
else
  warn "SO" "$(uname -s) $(uname -m)"
fi
mem_gb=$(awk '/MemTotal/ {printf "%.1f", $2/1024/1024}' /proc/meminfo 2>/dev/null)
[ -n "$mem_gb" ] && ok "RAM" "${mem_gb} GB"

echo "== Herramientas base =="
check_cmd "git"      git      "git --version"
check_cmd "python3"  python3  "python3 --version"
check_cmd "node"     node     "node --version"
check_cmd "vscode"   code     "code --version"
check_cmd "docker"   docker   "docker --version"

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    ok "docker daemon" "en ejecución y accesible sin sudo"
  else
    bad "docker daemon" "no responde o el usuario no está en el grupo docker"
  fi
  if docker compose version >/dev/null 2>&1; then
    ok "compose" "$(docker compose version | head -n 1)"
  else
    bad "compose" "falta el plugin docker compose"
  fi
fi

echo "== Herramientas de seguridad =="
check_cmd "semgrep"  semgrep  "semgrep --version"
check_cmd "gitleaks" gitleaks "gitleaks version"
check_cmd "trivy"    trivy    "trivy --version"
if command -v zaproxy >/dev/null 2>&1 || command -v zap.sh >/dev/null 2>&1; then
  ok "zap" "instalado"
else
  bad "zap" "no se encontró zaproxy"
fi
if command -v threat-dragon >/dev/null 2>&1 || ls /opt/Threat* >/dev/null 2>&1; then
  ok "threat-dragon" "instalado"
else
  warn "threat-dragon" "no se encontró la app de escritorio (válido si usan la versión web)"
fi

echo "== Entorno de práctica =="
if command -v curl >/dev/null 2>&1 && curl -fs -o /dev/null --max-time 5 http://127.0.0.1:3000; then
  ok "juice-shop" "responde en http://127.0.0.1:3000"
else
  bad "juice-shop" "no responde en 127.0.0.1:3000 (¿docker compose up -d?)"
fi
if command -v ss >/dev/null 2>&1 && ss -ltn 2>/dev/null | grep -Eq '(0\.0\.0\.0|\*|\[::\]):3000 '; then
  warn "exposición" "el puerto 3000 escucha en todas las interfaces; debe ser solo 127.0.0.1"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "Resultado: entorno listo."
else
  echo "Resultado: hay elementos en FALTA. Revisen setup/GUIA_INSTALACION.md."
fi
exit "$fail"
