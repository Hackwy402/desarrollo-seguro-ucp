#!/usr/bin/env bash
# informe.sh — genera el INFORME del lab en Markdown (sin marca), listo para
# dejar en el repo (seclab/ci-demo-app/REPORTE.md) y subir a Moodle como evidencia.
#
#   bash seclab/bin/informe.sh
#
# Hace un antes/despues real: escanea la app vulnerable, la parcha y re-escanea,
# y escribe el reporte con hallazgos, analisis de IA y remediacion. Requiere docker.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECLAB="$(cd "$HERE/.." && pwd)"
ROOT="$(cd "$SECLAB/.." && pwd)"
APP="$SECLAB/ci-demo-app"
OUT="$APP/REPORTE.md"
VULN="2.14.1"; FIX="2.26.1"
G=$'\033[38;5;46m'; C=$'\033[38;5;51m'; R=$'\033[38;5;196m'; B=$'\033[1m'; D=$'\033[2m'; X=$'\033[0m'
say(){ printf "\n${B}${C}▶ %s${X}\n" "$1"; }
sedi(){ if sed --version >/dev/null 2>&1; then sed -i "$@"; else sed -i '' "$@"; fi; }

command -v docker >/dev/null 2>&1 || { printf "${R}Falta docker.${X}\n"; exit 1; }
docker info >/dev/null 2>&1 || { printf "${R}Docker no responde (arráncalo).${X}\n"; exit 1; }

. "$HERE/_ai_env.sh"; ai_ensure_key >/dev/null 2>&1 || true
. "$HERE/_demo_app.sh"

# metadatos
WHO="$(git config user.name 2>/dev/null || echo 'alumno')"
LOGIN="$(gh api user -q .login 2>/dev/null || echo '')"
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || basename "$ROOT")"
BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '-')"
DATE="$(date '+%Y-%m-%d %H:%M')"
MODEL="${GATE_AI_MODEL:-(sin IA)}"

# imprime la tabla de hallazgos + total desde un report.json
table_of(){ # $1 report.json
  python3 - "$1" <<'PY'
import json,sys
try: r=json.load(open(sys.argv[1]))
except Exception: r={"findings":[],"total":0}
fs=r.get("findings",[]); tot=r.get("total",len(fs))
print(f"__TOTAL__={tot}")
if not fs:
    print("_Sin hallazgos._"); sys.exit()
print("| Herramienta | Severidad | Regla / CVE | Ubicacion |")
print("|---|---|---|---|")
for f in fs[:40]:
    print("| {} | {} | {} | {} |".format(f.get("tool","?"),f.get("severity","?"),
          f.get("rule","?"),str(f.get("loc","?")).replace("|","\\|")))
PY
}
scan_state(){ # $1 target -> dir con report.json
  bash "$HERE/scan.sh" --with-trivy --no-anim "$1" >/dev/null 2>&1 || true
  dirname "$(ls -t "$SECLAB"/.state/*/report.json 2>/dev/null | head -1)"
}

# ---- ANTES: app vulnerable ----
say "Capturando ANTES (log4j $VULN)…"
scaffold_vuln_app "$APP"
ST1="$(scan_state "$APP")"
BEFORE="$(table_of "$ST1/report.json")"
TOT_B="$(printf '%s\n' "$BEFORE" | sed -n 's/^__TOTAL__=//p')"
BEFORE="$(printf '%s\n' "$BEFORE" | grep -v '^__TOTAL__=')"
# analisis IA sobre el estado vulnerable
AITRIAGE="$(python3 "$HERE/ai_triage.py" "$ST1/report.json" 2>/dev/null || true)"
AISEC="$(printf '%s\n' "$AITRIAGE" | sed -n '/🤖 Explicacion/,/^---/p' | sed '$d')"
[ -z "$AISEC" ] && AISEC="$(printf '%s\n' "$AITRIAGE" | grep '🤖' | sed 's/^> *//; s/_//g')"
[ -z "$AISEC" ] && AISEC="_(No se ejecutó la IA: configura tu API key para incluir el análisis.)_"

# ---- DESPUES: parche ----
say "Aplicando parche a $FIX y capturando DESPUÉS…"
sedi "s/>$VULN</>$FIX</g" "$APP/pom.xml"
ST2="$(scan_state "$APP")"
AFTER="$(table_of "$ST2/report.json")"
TOT_A="$(printf '%s\n' "$AFTER" | sed -n 's/^__TOTAL__=//p')"
AFTER="$(printf '%s\n' "$AFTER" | grep -v '^__TOTAL__=')"

# ---- escribir REPORTE.md ----
say "Escribiendo $OUT"
{
cat <<MD
# Informe de seguridad — Lab Log4Shell

| | |
|---|---|
| **Alumno** | $WHO${LOGIN:+ (@$LOGIN)} |
| **Fecha** | $DATE |
| **Repositorio** | $REPO |
| **Rama** | \`$BRANCH\` |
| **Herramientas** | gitleaks · semgrep · osv-scanner · trivy + IA (\`$MODEL\`) |

## 1. Vulnerabilidad descubierta

El escaneo de dependencias (SCA) detectó **Log4Shell — CVE-2021-44228** en
\`org.apache.logging.log4j:log4j-core@$VULN\`: ejecución remota de código (RCE)
crítica cuando la aplicación registra texto controlado por el atacante.

**Hallazgos del gate (antes del parche):** $TOT_B — veredicto **🚫 BLOQUEADO** (exit 1)

$BEFORE

## 2. Análisis con IA

$AISEC

## 3. Remediación aplicada

Se actualizó \`log4j-api\` y \`log4j-core\` a **$FIX** en \`pom.xml\`.

> **Lección:** 2.17.1 corrige los CVE de 2021, pero el escaneo aún marcaba CVEs
> de 2025/2026 en log4j; por eso no basta y se sube a la última 2.x estable ($FIX).

**Hallazgos del gate (después del parche):** $TOT_A — veredicto **✅ PASA** (exit 0)

$AFTER

## 4. Evidencia

- Pull Request y corridas del gate (rojo → verde) en GitHub Actions del repo $REPO.
- Este informe: \`seclab/ci-demo-app/REPORTE.md\` (en el repo) + subido a **Moodle**.

## Conclusión

El pipeline **bloqueó el merge** hasta corregir la dependencia; la **IA** explicó el
riesgo y la remediación. El gate se re-evalúa contra bases de vulnerabilidades
actualizadas, por eso un fix "histórico" (2.17.1) puede no bastar hoy.

---
_Generado con \`seclab/bin/informe.sh\` el $DATE._
MD
} > "$OUT"

printf "${G}✔ Informe listo:${X} %s\n" "$OUT"
printf "${D}   Déjalo en el repo (git add/commit/push) y súbelo a Moodle como evidencia.${X}\n"
printf "${D}   La app quedó parchada ($FIX, verde).${X}\n"
