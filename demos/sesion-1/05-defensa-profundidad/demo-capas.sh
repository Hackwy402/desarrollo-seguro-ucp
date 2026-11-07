#!/usr/bin/env bash
# Demo 5: defensa en profundidad. Supuesto: un atacante ya logró ejecutar comandos dentro de la API
# (lo simulamos con docker compose exec). ¿Qué puede hacer en cada versión? ¿Qué capa lo contiene?
# Requiere el entorno de la demo 3 arriba.
set -u
cd "$(dirname "$0")/../03-api" || exit 1
export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
DC="docker compose -f docker-compose.yml"

pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }
probar() { # probar DESCRIPCION COMANDO
  printf '   %-44s' "$1"
  for s in insegura segura; do
    if out=$($DC exec -T "$s" sh -c "$2" 2>&1); then r="PERMITIDO"; else r="BLOQUEADO"; fi
    printf '%-10s %-11s' "$s:" "$r"
  done; echo
}

$DC up -d --quiet-pull >/dev/null 2>&1; sleep 2

pausa "Capa 1. Usuario del proceso"
for s in insegura segura; do printf '   %-9s ' "$s:"; $DC exec -T "$s" id; done

pausa "Capas 1 y 2. Usuario sin privilegios y sistema de archivos de solo lectura"
probar "Escribir en /etc"                     'echo x > /etc/puerta'
probar "Reemplazar el código de la app"       'echo "# puerta" >> /app/app_insegura.py 2>/dev/null || echo "# puerta" >> /app/app_segura.py'
probar "Dejar un binario en /usr/local/bin"   'echo "#!/bin/sh" > /usr/local/bin/herramienta'

pausa "Capa 3. Capacidades del kernel (CapEff = 0 significa ninguna)"
for s in insegura segura; do printf '   %-9s ' "$s:"; $DC exec -T "$s" sh -c 'grep CapEff /proc/1/status'; done
probar "Cambiar el dueño de un archivo (chown)" 'touch /tmp/a 2>/dev/null || true; chown 0:0 /tmp/a 2>/dev/null || chown 0:0 /proc/self/fd/0'

pausa "Capa 4. Sin escalada de privilegios y con límites de recursos"
for s in insegura segura; do printf '   %-9s ' "$s:"; $DC exec -T "$s" sh -c 'grep NoNewPrivs /proc/1/status'; done
for s in insegura segura; do printf '   %-9s pids.max=%s  memory.max=%s\n' "$s:" \
  "$($DC exec -T "$s" cat /sys/fs/cgroup/pids.max 2>/dev/null)" "$($DC exec -T "$s" cat /sys/fs/cgroup/memory.max 2>/dev/null)"; done

pausa "Fin. Ninguna capa es perfecta; juntas convierten una intrusión en un incidente contenido."
echo "   Las capas están en el Dockerfile (USER) y en docker-compose.yml (read_only, cap_drop, no-new-privileges, límites)."
