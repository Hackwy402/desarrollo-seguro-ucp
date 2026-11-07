#!/usr/bin/env bash
# Demo: tres principios violados en una API real y su control, con Docker, curl, Semgrep y Trivy.
# Uso: bash demos/app/demo-app.sh  (requiere docker, semgrep y trivy)
set -u
cd "$(dirname "$0")" || exit 1
export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
DC="docker compose -f docker-compose.yml"
INS=http://127.0.0.1:5001
SEG=http://127.0.0.1:5002

pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }
pedir() { # pedir METODO URL TOKEN
  printf '   %-6s %-38s -> ' "$1" "$2"
  curl -s -o /tmp/demo-resp -w '%{http_code}  ' -X "$1" -H "Authorization: Bearer $3" "$2"; tr -s '\n ' ' ' </tmp/demo-resp | sed 's/<[^>]*>//g' | head -c 90; echo
}

pausa "0. Levantar las dos versiones de la API (insegura :5001, segura :5002)"
$DC up -d --build --quiet-pull 2>&1 | grep -vE "^\s*$" | tail -3
sleep 3; $DC ps --format 'table {{.Service}}\t{{.Ports}}'

pausa "A. MEDIACIÓN COMPLETA (A01). Ana pide su factura (1) y luego la de Luis (2)"
for u in $INS $SEG; do pedir GET "$u/facturas/1" token-ana; pedir GET "$u/facturas/2" token-ana; done
echo "   Insegura: estar autenticado bastó para leer la factura ajena. Segura: 404."

pausa "B. FALLAR DE FORMA SEGURA (A10). Luis intenta editar el documento 10 (no es editor)"
for u in $INS $SEG; do pedir POST "$u/documentos/10/editar" token-luis; done
pausa "   Ahora el servicio de permisos se cae..."
$DC stop permisos 2>&1 | tail -1
for u in $INS $SEG; do pedir POST "$u/documentos/10/editar" token-luis; done
echo "   Insegura: con el servicio caído, todos son editores. Segura: niega y registra."
$DC start permisos >/dev/null 2>&1

pausa "C. SEGURO POR DEFECTO (A02). Provocar un error"
curl -s $INS/error > /tmp/demo-error.html
echo "   Insegura: página de depuración de $(wc -l < /tmp/demo-error.html | tr -d ' ') líneas con la traza completa. Revela, entre otros:"
grep -oE '/app/[a-z_]+\.py|/usr/local/lib/python[0-9.]+|ZeroDivisionError: [a-z ]+|Werkzeug Debugger' /tmp/demo-error.html | sort -u | sed 's/^/     /'
echo "   (Ábranla en el navegador: $INS/error)"
echo "   Segura:";   curl -s $SEG/error | sed 's/^/     /'; echo

pausa "D. MÍNIMO PRIVILEGIO. ¿Con qué usuario corre cada contenedor?"
printf '   insegura: '; $DC exec -T insegura whoami
printf '   segura:   '; $DC exec -T segura whoami
printf '   segura, escribir en disco: '; $DC exec -T segura sh -c 'touch /app/x 2>&1 || true'

pausa "E. Los mismos problemas, encontrados por herramientas: Semgrep sobre el código"
semgrep scan --config ../semgrep/reglas-sesion1.yml --metrics=off app_insegura.py app_segura.py

pausa "F. Trivy sobre los Dockerfile"
trivy config --quiet .

pausa "Fin. Apagar el entorno"
$DC down 2>&1 | tail -1
