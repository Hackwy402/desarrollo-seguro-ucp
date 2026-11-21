#!/usr/bin/env bash
# lab-pr.sh — el estudiante abre SU Pull Request para que el Security Gate
# corra en CI (con el modelo de IA del repo) y vea el ciclo rojo -> verde.
#
#   bash seclab/bin/lab-pr.sh          # crea tu rama + app vulnerable + abre el PR (ROJO)
#   bash seclab/bin/lab-pr.sh --fix    # parcha a 2.26.1 y empuja (VERDE) en tu misma rama
#
# Requisitos: git y gh (GitHub CLI) autenticado:  gh auth login
# No necesitas docker (el gate corre en GitHub Actions).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECLAB="$(cd "$HERE/.." && pwd)"
ROOT="$(cd "$SECLAB/.." && pwd)"
APP="$SECLAB/ci-demo-app"
VULN="2.14.1"; FIX="2.26.1"
G=$'\033[38;5;46m'; Y=$'\033[38;5;226m'; C=$'\033[38;5;51m'; R=$'\033[38;5;196m'; B=$'\033[1m'; D=$'\033[2m'; X=$'\033[0m'
say(){ printf "\n${B}${C}▶ %s${X}\n" "$1"; }
die(){ printf "${R}%s${X}\n" "$1"; exit 1; }

sedi(){ if sed --version >/dev/null 2>&1; then sed -i "$@"; else sed -i '' "$@"; fi; }

command -v git >/dev/null || die "Falta git."
command -v gh  >/dev/null || die "Falta gh (GitHub CLI). Instala y corre: gh auth login"
gh auth status >/dev/null 2>&1 || die "No estás autenticado. Corre: gh auth login"
cd "$ROOT"

REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)"
[ -n "$REPO" ] || die "No pude detectar el repo (¿estás dentro del clon?)."
USER_LOGIN="$(gh api user -q .login 2>/dev/null || echo alumno)"
SAFE="$(printf '%s' "$USER_LOGIN" | tr -cd '[:alnum:]-_' | tr '[:upper:]' '[:lower:]')"
BRANCH="lab/${SAFE}-log4shell"

# ---------------- modo --fix: parchar y empujar (VERDE) ----------------
if [ "${1:-}" = "--fix" ]; then
  git rev-parse --abbrev-ref HEAD | grep -qx "$BRANCH" || git checkout "$BRANCH" 2>/dev/null \
    || die "No estás en tu rama $BRANCH. Corre primero: bash seclab/bin/lab-pr.sh"
  [ -f "$APP/pom.xml" ] || die "No encuentro $APP/pom.xml en tu rama."
  say "Parcheando log4j $VULN -> $FIX"
  sedi "s/>$VULN</>$FIX</g" "$APP/pom.xml"
  git add "$APP/pom.xml"
  git commit -q -m "fix(app-pedidos): sube log4j a $FIX (cierra Log4Shell y CVEs 2025/2026)"
  git push -q origin "$BRANCH"
  printf "${G}✔ Parche empujado. El gate re-corre y debe pasar a VERDE.${X}\n"
  gh pr view "$BRANCH" --json url -q .url 2>/dev/null
  exit 0
fi

# ---------------- modo normal: crear rama + vuln + PR (ROJO) ----------------
say "Preparando tu rama: $BRANCH  (repo $REPO)"
git fetch origin -q
git checkout -B "$BRANCH" origin/main -q

. "$HERE/_demo_app.sh"
scaffold_vuln_app "$APP"
git add "$APP"
git commit -q -m "feat(app-pedidos): logging de X-Api-Version (agrega log4j $VULN)

Introduce la dependencia vulnerable a proposito: el Security Gate del PR
debe bloquear y explicar el hallazgo (Log4Shell, CVE-2021-44228)."
git push -q -u origin "$BRANCH"

say "Abriendo el Pull Request"
PR_URL="$(gh pr create --repo "$REPO" --base main --head "$BRANCH" \
  --title "Lab Log4Shell — $USER_LOGIN" \
  --body "PR del lab. El **Security Gate** debe correr, **bloquear** (rojo) y la **IA** comentar el CVE y la remediación.

Pasos:
1. Observa el check \`gate\` en rojo y el comentario de la IA abajo.
2. Parcha con: \`bash seclab/bin/lab-pr.sh --fix\` (sube log4j a $FIX).
3. El gate pasa a **verde** y el PR queda mergeable.
4. Genera el informe: \`bash seclab/bin/informe.sh\` y súbelo a Moodle." 2>&1)" || die "No pude crear el PR: $PR_URL"

printf "${G}✔ PR abierto:${X} %s\n" "$PR_URL"
printf "${D}   El gate corre en Actions; en ~1 min verás el rojo + comentario de la IA.${X}\n"
printf "${B}   Cuando lo veas, parcha con:${X}  bash seclab/bin/lab-pr.sh --fix\n"
