#!/usr/bin/env bash
# Demo 3: principios de seguridad en una API real. Misma API, dos versiones.
# Uso: bash demos/sesion-1/03-api/demo-api.sh   (requiere docker)
set -u
cd "$(dirname "$0")" || exit 1
export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
DC="docker compose -f docker-compose.yml"
INS=http://127.0.0.1:5001
SEG=http://127.0.0.1:5002

pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }
pedir() { # pedir METODO URL TOKEN
  printf '   %-6s %-38s -> ' "$1" "$2"
  curl -s -o /tmp/demo-resp -w '%{http_code}  ' -X "$1" -H "Authorization: Bearer $3" "$2"
  tr -s '\n ' ' ' </tmp/demo-resp | sed 's/<[^>]*>//g' | head -c 90; echo
}

pausa "0. Levantar las dos versiones de la API (insegura :5001, segura :5002)"
$DC up -d --build --quiet-pull 2>&1 | grep -vE "^\s*$" | tail -2
sleep 3; $DC ps --format 'table {{.Service}}\t{{.Ports}}'

pausa "A. MEDIACIÓN COMPLETA. Ana pide su factura (1) y luego la de Luis (2)"
for u in $INS $SEG; do pedir GET "$u/facturas/1" token-ana; pedir GET "$u/facturas/2" token-ana; done
echo "   Insegura: estar autenticado bastó para leer la factura ajena. Segura: 404."

pausa "B. FALLAR DE FORMA SEGURA. Luis intenta editar el documento 10 (no es editor)"
for u in $INS $SEG; do pedir POST "$u/documentos/10/editar" token-luis; done
pausa "   Ahora el servicio de permisos se cae..."
$DC stop permisos 2>&1 | tail -1
for u in $INS $SEG; do pedir POST "$u/documentos/10/editar" token-luis; done
echo "   Insegura: con el servicio caído, todos son editores. Segura: niega y registra."
$DC start permisos >/dev/null 2>&1

pausa "C. SEGURO POR DEFECTO. Provocar un error"
curl -s $INS/error > /tmp/demo-error.html
echo "   Insegura: página de depuración de $(wc -l < /tmp/demo-error.html | tr -d ' ') líneas con la traza completa. Revela, entre otros:"
grep -oE '/app/[a-z_]+\.py|/usr/local/lib/python[0-9.]+|ZeroDivisionError: [a-z ]+|Werkzeug Debugger' /tmp/demo-error.html | sort -u | sed 's/^/     /'
echo "   (Ábranla en el navegador: $INS/error)"
echo "   Segura:"; curl -s $SEG/error | sed 's/^/     /'; echo

pausa "Fin. El entorno queda arriba para la demo 5 (defensa en profundidad). Para apagarlo: $DC down"
