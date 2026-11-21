#!/usr/bin/env bash
# heisenberg.sh — Heisenberg "cocina" el escaneo con una barra de progreso.
#
#   heisenberg.sh "Cocinando el escaneo…" -- <comando...>
#       corre <comando> en segundo plano, muestra a Heisenberg + una barra que
#       avanza y cambia de color (rojo→amarillo→verde) hasta 100%, y devuelve
#       el mismo exit code del comando.
#   heisenberg.sh --demo
#       solo muestra la animación unos segundos (para probarla).
#
# Sin dependencias: bash + tput. Degrada a texto plano si no hay TTY.
set -u

GREEN=$'\033[38;5;46m'; YEL=$'\033[38;5;226m'; CYAN=$'\033[38;5;51m'
DIM=$'\033[2m'; BOLD=$'\033[1m'; RED=$'\033[38;5;196m'; WHT=$'\033[38;5;255m'; GRY=$'\033[38;5;240m'; RST=$'\033[0m'
HIDE=$'\033[?25l'; SHOW=$'\033[?25h'

msg="${1:-Cocinando…}"

# --- retrato de Heisenberg (estatico, se ve igual en Ubuntu y macOS) ---
portrait() {
cat <<ART
            ${GRY}▄▄▄▄▄▄▄▄▄▄▄▄${RST}
            ${GRY}████████████${RST}
        ${GRY}▄▄▄████████████▄▄▄${RST}
        ${GRY}▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀${RST}
        ${CYAN}┌──────────────────┐${RST}
        ${CYAN}│${RST}   ${WHT}▄▄▄${RST}      ${WHT}▄▄▄${RST}    ${CYAN}│${RST}
        ${CYAN}│${RST}  ${WHT}█${DIM}▓▓▓${RST}${WHT}█${RST}    ${WHT}█${DIM}▓▓▓${RST}${WHT}█${RST}   ${CYAN}│${RST}
        ${CYAN}│${RST}   ${WHT}▀▀▀${RST}      ${WHT}▀▀▀${RST}    ${CYAN}│${RST}
        ${CYAN}│${RST}         ${YEL}▟▙${RST}        ${CYAN}│${RST}
        ${CYAN}│${RST}      ${DIM}▗▄▄▄▄▄▄▖${RST}     ${CYAN}│${RST}
        ${CYAN}└──────────────────┘${RST}
        ${DIM}"No half measures."${RST}
ART
}

# --- barra de progreso: $1 = pct (0..100), $2 = ancho ---
bar() {
  local pct=$1 w=${2:-26} filled i out="" col lbl
  [ "$pct" -gt 100 ] && pct=100
  filled=$(( pct * w / 100 ))
  if   [ "$pct" -lt 34 ]; then col=$RED
  elif [ "$pct" -lt 67 ]; then col=$YEL
  else col=$GREEN; fi
  for ((i=0; i<w; i++)); do
    if [ "$i" -lt "$filled" ]; then out+="█"; else out+="░"; fi
  done
  if [ "$pct" -ge 100 ]; then lbl="${GREEN}100% puro${RST}"; else lbl="${BOLD}${pct}%${RST}"; fi
  printf "   %s%s%s  %s\n" "$col" "$out" "$RST" "$lbl"
}

spinner='|/-\'
animate_until() { # $1 = archivo-centinela; anima hasta que exista
  local done_file="$1" i=0 sp=0 pct=0 step
  tput civis 2>/dev/null; printf '%s' "$HIDE"
  tput clear 2>/dev/null
  while [ ! -f "$done_file" ]; do
    tput cup 0 0 2>/dev/null || printf '\033[H'
    echo; portrait
    echo
    printf "   ${BOLD}${CYAN}%s${RST} ${YEL}%s${RST}  ${DIM}(%ss)${RST}\n\n" \
      "${spinner:$((sp%4)):1}" "$msg" "$((i/5))"
    bar "$pct" 26
    printf "   ${DIM}gitleaks · semgrep · osv · trivy${RST}\n"
    # avanza desacelerando hacia 95% (el escaneo no reporta % real)
    step=$(( (95 - pct) / 10 )); [ "$step" -lt 1 ] && step=1
    pct=$(( pct + step )); [ "$pct" -gt 95 ] && pct=95
    i=$((i+1)); sp=$((sp+1)); sleep 0.2
  done
  # remate: llena a 100% en verde antes de salir
  tput cup 0 0 2>/dev/null || printf '\033[H'
  echo; portrait; echo
  printf "   ${BOLD}${GREEN}✔${RST} ${YEL}%s${RST}\n\n" "$msg"
  bar 100 26
  printf "   ${DIM}gitleaks · semgrep · osv · trivy${RST}\n"
  sleep 0.4
  printf '%s' "$SHOW"; tput cnorm 2>/dev/null
}

if [ "${1:-}" = "--demo" ]; then
  d=$(mktemp -u); ( sleep 4; : > "$d" ) &
  animate_until "$d"; rm -f "$d"
  printf "\n   ${GREEN}✔ receta lista.${RST}\n"; exit 0
fi

# Modo wrapper:  heisenberg.sh "msg" -- comando...
cmd=(); seen=0
for a in "$@"; do
  if [ "$seen" = 1 ]; then cmd+=("$a"); fi
  if [ "$a" = "--" ]; then seen=1; fi
done

if [ "${#cmd[@]}" -eq 0 ]; then
  d=$(mktemp -u); ( sleep 3; : > "$d" ) & animate_until "$d"; rm -f "$d"; exit 0
fi

# Si no hay TTY, corre el comando sin animación
if [ ! -t 1 ]; then
  printf '>> %s\n' "$msg"; "${cmd[@]}"; exit $?
fi

done_file=$(mktemp -u); log_file=$(mktemp)
( "${cmd[@]}" >"$log_file" 2>&1; echo $? >"${done_file}.rc"; : > "$done_file" ) &
animate_until "$done_file"
rc=$(cat "${done_file}.rc" 2>/dev/null || echo 1)
tput clear 2>/dev/null || printf '\033[2J\033[H'
if [ "$rc" = "0" ]; then
  printf "   ${GREEN}✔ %s — listo.${RST}\n\n" "$msg"
else
  printf "   ${RED}✖ %s — exit %s.${RST}\n\n" "$msg" "$rc"
fi
tail -n 40 "$log_file"
rm -f "$done_file" "${done_file}.rc" "$log_file"
exit "$rc"
