#!/usr/bin/env bash
# Demo: el entorno del curso y el principio de superficie mínima en Docker.
# Uso: bash demos/entorno/demo-entorno.sh (desde la raíz del repositorio)
set -u
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }

escuchando() {
  if command -v ss >/dev/null 2>&1; then ss -ltn | grep -E ":$1\b" || echo "(nada en :$1)"
  else lsof -nP -iTCP:"$1" -sTCP:LISTEN 2>/dev/null | awk 'NR==1 || /LISTEN/' || echo "(nada en :$1)"; fi
}

pausa "1. Versiones de la cadena de herramientas (práctica PO.3 del SSDF)"
docker version --format 'Docker cliente {{.Client.Version}} · servidor {{.Server.Version}} ({{.Server.Arch}})'
docker compose version

pausa "2. Levantar el entorno de práctica del curso"
docker compose -f "$RAIZ/lab-env/docker-compose.yml" up -d
docker compose -f "$RAIZ/lab-env/docker-compose.yml" ps --format 'table {{.Name}}\t{{.Image}}\t{{.Ports}}'

pausa "3. ¿En qué interfaz escucha? Solo 127.0.0.1"
escuchando 3000

pausa "4. El error común: publicar el puerto sin IP (-p 3001:3000)"
docker run -d --rm --name juice-expuesto -p 3001:3000 bkimminich/juice-shop:latest >/dev/null
sleep 2
docker ps --filter name=juice-expuesto --format 'table {{.Names}}\t{{.Ports}}'
escuchando 3001
echo
echo "0.0.0.0 = todas las interfaces: cualquier equipo de la red (el café, la oficina) llega a esta app vulnerable."
echo "En Linux, además, Docker escribe sus propias reglas de iptables y el puerto queda abierto aunque ufw diga lo contrario."
docker stop juice-expuesto >/dev/null

pausa "5. Verificar el entorno completo"
bash "$RAIZ/setup/check-env.sh" || true

pausa "Fin. Principios: superficie mínima y seguro por defecto. El compose del curso ya publica solo en 127.0.0.1."
