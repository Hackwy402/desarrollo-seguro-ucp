#!/usr/bin/env bash
# scan.sh — "cocina" un escaneo de seguridad sobre un directorio usando solo
# Docker (cero instalaciones): secretos + SAST + SCA (+ SBOM/vulns opcional).
# Produce: resumen con gate, reporte JSON, metricas Prometheus y diff de
# alarmas (nuevas / subsanadas). Opcionalmente notifica a Slack/Discord/Telegram.
#
#   bin/scan.sh [ruta]                 escanea ruta (default: .)
#   bin/scan.sh --with-trivy [ruta]    agrega Trivy (SBOM + vulns de SO/deps)
#   bin/scan.sh --soft [ruta]          no falla aunque haya hallazgos
#   bin/scan.sh --no-anim [ruta]       sin animacion (CI)
#
# Env: SECLAB_WEBHOOK_SLACK / _DISCORD / TELEGRAM_* -> notifica (ver notify.sh)
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECLAB="$(cd "$HERE/.." && pwd)"

GREEN=$'\033[38;5;46m'; YEL=$'\033[38;5;226m'; CYAN=$'\033[38;5;51m'
RED=$'\033[38;5;196m'; DIM=$'\033[2m'; BOLD=$'\033[1m'; RST=$'\033[0m'

WITH_TRIVY=0; SOFT=0; ANIM=1; AI=0; TARGET="."
for a in "$@"; do
  case "$a" in
    --with-trivy) WITH_TRIVY=1;;
    --soft) SOFT=1;;
    --no-anim) ANIM=0;;
    --ai) AI=1;;
    __run) :;;
    *) TARGET="$a";;
  esac
done

# ---- fase interna: corre los escaneres (se invoca envuelta por heisenberg) ----
if [ "${1:-}" = "__run" ]; then
  SCANDIR="$2"; STATE="$3"; WITH_TRIVY="$4"
  mkdir -p "$STATE"
  rm -f "$STATE/scan_error"
  DR="docker run --rm -v ${SCANDIR}:/scan -v ${STATE}:/scan/.state"

  echo ">> secretos (gitleaks)"
  $DR zricethezav/gitleaks:latest detect --no-git --source=/scan \
     --report-format=json --report-path=/scan/.state/gitleaks.json >/dev/null 2>&1 || true

  echo ">> SAST (semgrep)"
  $DR semgrep/semgrep:latest semgrep scan --config=p/default --json \
     --output=/scan/.state/semgrep.json /scan >/dev/null 2>&1 || true

  echo ">> SCA (osv-scanner)"
  osv_neterr=0
  osv_out="$($DR ghcr.io/google/osv-scanner:latest --format=json \
     --output=/scan/.state/osv.json -r /scan 2>&1)"
  # osv necesita red a osv.dev; si no la alcanza, su "0 vulns" no es fiable.
  if printf '%s' "$osv_out" | grep -qiE "error during extraction|max retries|tls handshake|connection refused|no such host|i/o timeout"; then
     osv_neterr=1
  fi

  trivy_ok=0
  if [ "$WITH_TRIVY" = "1" ]; then
    echo ">> SBOM + vulns (trivy)"
    docker run --rm -v "${SCANDIR}:/scan" -v "${STATE}:/scan/.state" \
       -v trivy-db-cache:/root/.cache/ aquasec/trivy:latest fs --quiet \
       --format=json --output=/scan/.state/trivy.json /scan >/dev/null 2>&1 || true
    # trivy trae su propia base (ghcr.io) -> si produjo salida, el SCA quedo cubierto.
    [ -s "$STATE/trivy.json" ] && trivy_ok=1
  fi

  # fail-closed: el SCA solo queda SIN VERIFICAR si NINGUNA herramienta de SCA lo cubrio.
  if [ "$osv_neterr" = "1" ] && [ "$trivy_ok" = "0" ]; then
     echo "El SCA no pudo consultar ninguna base de vulnerabilidades (osv.dev sin acceso y sin Trivy). No se puede afirmar que las dependencias esten limpias. Reintenta con red, o corre con --with-trivy (base offline desde ghcr.io)." > "$STATE/scan_error"
  fi
  echo ">> escaneres terminados"
  exit 0
fi

# ---------------------------- orquestacion -----------------------------------
SCANDIR="$(cd "$TARGET" 2>/dev/null && pwd)"
[ -z "$SCANDIR" ] && { echo "${RED}Ruta no existe: $TARGET${RST}"; exit 2; }
STATE="$SECLAB/.state/$(echo "$SCANDIR" | md5 2>/dev/null || echo "$SCANDIR" | md5sum | cut -d' ' -f1)"
mkdir -p "$STATE"

printf "\n${BOLD}${YEL}  LOS POLLOS DEVSECOPS${RST} — escaneando ${CYAN}%s${RST}\n\n" "$SCANDIR"

if [ "$ANIM" = "1" ] && [ -t 1 ]; then
  "$HERE/heisenberg.sh" "Cocinando el escaneo…" -- "$0" __run "$SCANDIR" "$STATE" "$WITH_TRIVY"
else
  "$0" __run "$SCANDIR" "$STATE" "$WITH_TRIVY"
fi

# ---------------------------- parseo + gate ----------------------------------
SUMMARY="$(python3 "$HERE/_parse.py" "$STATE")"
echo "$SUMMARY"
TOTAL="$(cat "$STATE/_total" 2>/dev/null || echo 0)"

# ---------------------------- notificar --------------------------------------
if [ -x "$HERE/notify.sh" ]; then
  "$HERE/notify.sh" "$STATE" "$SCANDIR" || true
fi

# ---------------------------- triage con IA (opcional) -----------------------
if [ "$AI" = "1" ]; then
  echo
  printf "${DIM}── triage con IA ──────────────────────────────────${RST}\n"
  # carga/solicita la key de forma segura (oculta, guardada en seclab/.env)
  . "$HERE/_ai_env.sh"
  ai_ensure_key || true
  python3 "$HERE/ai_triage.py" "$STATE/report.json" || true
fi

# ---------------------------- gate -------------------------------------------
echo
# fail-closed: un escaneo que no pudo completarse NO pasa (aunque haya 0 hallazgos)
if [ -f "$STATE/scan_error" ]; then
  printf "   ${RED}${BOLD}🚫 GATE: escaneo INCOMPLETO — fail-closed.${RST}  ${DIM}(exit 2)${RST}\n"
  printf "   ${DIM}%s${RST}\n" "$(cat "$STATE/scan_error")"
  exit 2
fi
if [ "$TOTAL" -gt 0 ]; then
  if [ "$SOFT" = "1" ]; then
    printf "   ${YEL}● %s hallazgo(s). Modo --soft: no bloquea.${RST}\n" "$TOTAL"; exit 0
  fi
  printf "   ${RED}${BOLD}🚫 GATE: %s hallazgo(s) — bloquea.${RST}  ${DIM}(exit 1)${RST}\n" "$TOTAL"
  exit 1
fi
printf "   ${GREEN}${BOLD}✅ GATE: sin hallazgos — pasa.${RST}  ${DIM}(exit 0)${RST}\n"
exit 0
