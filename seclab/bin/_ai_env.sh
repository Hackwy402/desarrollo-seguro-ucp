# _ai_env.sh — carga la API key de IA de forma SEGURA para el lab.
# Se SOURCEA desde scan.sh / lab.sh (no se ejecuta solo).
#
# Orden de resolucion de GATE_AI_API_KEY:
#   1) variable de entorno ya definida (p. ej. secret de CI)  -> se respeta
#   2) archivo seclab/.env  (ignorado por git, chmod 600)
#   3) prompt interactivo OCULTO (no se ve al teclear)
#
# Blindajes para estudiantes:
#   - SANITIZA la key pegada (quita espacios, saltos y comillas envolventes).
#   - DETECTA el proveedor por prefijo (sk-ms- -> Kimi, gsk_ -> Groq) y pone
#     base_url/modelo solos si no vienen definidos.
#   - VALIDA la key contra el endpoint antes de guardarla; si la rechazan
#     (401/403) no guarda basura y vuelve a pedirla.
#
# NUNCA imprime la key. El archivo .env esta en .gitignore (y gitleaks lo caza).

_AIENV_SECLAB="${SECLAB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
_AIENV_FILE="$_AIENV_SECLAB/.env"
_AI_LASTCODE=""

# cargar .env si existe (exporta GATE_AI_* sin eco)
if [ -f "$_AIENV_FILE" ]; then
  set -a; . "$_AIENV_FILE"; set +a
fi

# quita espacios/tab/CR/LF y comillas envolventes de una key pegada
_ai_sanitize() {
  local k="$1"
  k="${k//[$'\t\r\n ']/}"
  k="${k#\'}"; k="${k%\'}"
  k="${k#\"}"; k="${k%\"}"
  printf '%s' "$k"
}

# deduce proveedor por prefijo; respeta base/model ya definidos (:=)
_ai_provider_from_key() {
  case "$1" in
    sk-ms-*)
      : "${GATE_AI_BASE_URL:=https://api.moonshot.ai/v1}"
      : "${GATE_AI_MODEL:=kimi-k3}" ;;
    gsk_*)
      : "${GATE_AI_BASE_URL:=https://api.groq.com/openai/v1}"
      : "${GATE_AI_MODEL:=llama-3.3-70b-versatile}" ;;
    *)
      : "${GATE_AI_BASE_URL:=https://api.groq.com/openai/v1}"
      : "${GATE_AI_MODEL:=llama-3.3-70b-versatile}" ;;
  esac
  export GATE_AI_BASE_URL GATE_AI_MODEL
}

# valida la key contra <base>/models. 0 = ok o no se pudo validar; 1 = auth-fail
_ai_validate() {
  command -v curl >/dev/null 2>&1 || return 0   # sin curl no validamos (no bloquear)
  _AI_LASTCODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
     -H "Authorization: Bearer $2" "$1/models" 2>/dev/null)
  case "$_AI_LASTCODE" in
    401|403) return 1;;   # auth definitivamente mala
    *)       return 0;;   # 2xx ok; 000/404/etc -> no bloquear
  esac
}

# Pide la key de forma oculta si aun no hay. Devuelve 0 si quedo lista, 1 si no.
ai_ensure_key() {
  # ya hay key (env o .env): sanitiza, fija proveedor y sale
  if [ -n "${GATE_AI_API_KEY:-}" ]; then
    GATE_AI_API_KEY="$(_ai_sanitize "$GATE_AI_API_KEY")"; export GATE_AI_API_KEY
    _ai_provider_from_key "$GATE_AI_API_KEY"
    return 0
  fi
  # sin terminal (CI, pipe) no se puede pedir: se omite el triage, no se rompe
  [ -t 0 ] || return 1

  local tries=0 raw key
  while [ "$tries" -lt 2 ]; do
    tries=$((tries + 1))
    printf "\n  🔑 Pega tu API key de IA (Groq gsk_… o Kimi sk-ms-…), no se vera: " >&2
    IFS= read -rs raw; printf "\n" >&2
    key="$(_ai_sanitize "$raw")"
    if [ -z "$key" ]; then
      printf "  (sin key: se omite el triage con IA; el gate igual escanea)\n" >&2
      return 1
    fi
    GATE_AI_API_KEY="$key"; export GATE_AI_API_KEY
    _ai_provider_from_key "$key"
    printf "  Validando contra %s … " "$GATE_AI_BASE_URL" >&2
    if _ai_validate "$GATE_AI_BASE_URL" "$key"; then
      printf "ok ✔\n" >&2
      break
    fi
    printf "rechazada (HTTP %s). ¿Copiaste la key completa, sin espacios?\n" "$_AI_LASTCODE" >&2
    unset GATE_AI_API_KEY
    if [ "$tries" -ge 2 ]; then
      printf "  Se omite el triage con IA por ahora (el gate igual bloquea).\n" >&2
      return 1
    fi
  done

  [ -n "${GATE_AI_API_KEY:-}" ] || return 1
  printf "  ¿Guardarla en %s para no volver a pedirla? [y/N] " "$_AIENV_FILE" >&2
  local ans; read -r ans
  case "$ans" in
    y|Y|s|S)
      ( umask 177   # nace solo-lectura del dueño (600)
        {
          printf '# Key de IA del lab. NO se sube a git (seclab/.gitignore).\n'
          printf 'GATE_AI_API_KEY=%s\n'  "$GATE_AI_API_KEY"
          printf 'GATE_AI_BASE_URL=%s\n' "$GATE_AI_BASE_URL"
          printf 'GATE_AI_MODEL=%s\n'    "$GATE_AI_MODEL"
        } > "$_AIENV_FILE" )
      chmod 600 "$_AIENV_FILE" 2>/dev/null || true
      printf "  ✔ Guardada en %s (chmod 600, ignorada por git).\n" "$_AIENV_FILE" >&2 ;;
    *)
      printf "  (no se guardo; solo para esta corrida)\n" >&2 ;;
  esac
  return 0
}
