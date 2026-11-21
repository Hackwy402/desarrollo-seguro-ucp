# _ai_env.sh — carga la API key de IA de forma SEGURA para el lab.
# Se SOURCEA desde scan.sh / lab.sh (no se ejecuta solo).
#
# Orden de resolucion de GATE_AI_API_KEY:
#   1) variable de entorno ya definida (p. ej. secret de CI)  -> se respeta
#   2) archivo seclab/.env  (ignorado por git, chmod 600)
#   3) prompt interactivo OCULTO (no se ve al teclear) + opcion de guardarla
#
# NUNCA imprime la key. El archivo .env esta en .gitignore, asi que no puede
# subirse por accidente (y gitleaks del propio gate lo cazaria si se intentara).

# raiz de seclab (si scan.sh ya la exporto como $SECLAB, se usa esa)
_AIENV_SECLAB="${SECLAB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
_AIENV_FILE="$_AIENV_SECLAB/.env"

# 2) cargar .env si existe (exporta GATE_AI_* sin eco)
if [ -f "$_AIENV_FILE" ]; then
  set -a; . "$_AIENV_FILE"; set +a
fi

# Pide la key de forma oculta si aun no hay. Devuelve 0 si quedo lista, 1 si no.
ai_ensure_key() {
  if [ -n "${GATE_AI_API_KEY:-}" ]; then
    return 0
  fi
  # sin terminal (CI, pipe) no se puede pedir: se omite el triage, no se rompe
  if [ ! -t 0 ]; then
    return 1
  fi
  printf "\n  🔑 Pega tu API key de IA (no se mostrara al teclear) y Enter: " >&2
  # -s: oculto  -r: no interpreta backslashes
  IFS= read -rs GATE_AI_API_KEY
  printf "\n" >&2
  if [ -z "$GATE_AI_API_KEY" ]; then
    printf "  (sin key: se omite el triage con IA; el gate igual escanea)\n" >&2
    unset GATE_AI_API_KEY
    return 1
  fi
  export GATE_AI_API_KEY
  printf "  ¿Guardarla en %s para no volver a pedirla? [y/N] " "$_AIENV_FILE" >&2
  local ans; read -r ans
  case "$ans" in
    y|Y|s|S)
      ( umask 177   # el archivo nace solo-lectura del dueño (600)
        {
          printf '# Key de IA del lab. NO se sube a git (seclab/.gitignore).\n'
          printf 'GATE_AI_API_KEY=%s\n' "$GATE_AI_API_KEY"
          printf '# Proveedor (opcional). Por defecto Groq (gratis). Para Kimi/Moonshot:\n'
          printf '# GATE_AI_BASE_URL=https://api.moonshot.ai/v1\n'
          printf '# GATE_AI_MODEL=kimi-k3\n'
        } > "$_AIENV_FILE" )
      chmod 600 "$_AIENV_FILE" 2>/dev/null || true
      printf "  ✔ Guardada en %s (chmod 600, ignorada por git).\n" "$_AIENV_FILE" >&2
      ;;
    *)
      printf "  (no se guardo; solo para esta corrida)\n" >&2
      ;;
  esac
  return 0
}
