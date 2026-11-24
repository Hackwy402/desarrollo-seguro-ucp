# Laboratorio 3 · Pipeline DevSecOps con SBOM y firma de artefactos

**Sesión 4 · viernes 20 de noviembre · 5:00 a 10:00 p. m. (300 min)**
**Entrega:** 10:00 p. m., como comentario en el issue de su equipo con el enlace a la carpeta `seguridad/lab3/` y al pull request.

Hasta ahora respondimos *¿qué fallas tiene este código?* (Lab 2). Hoy respondemos la pregunta del pipeline: **¿cómo evito que una falla nueva llegue a `main` sin frenar al equipo por la deuda que ya existe?** La respuesta son tres evidencias que se complementan:

| Fuente | Qué demuestra | Qué no demuestra |
|---|---|---|
| **Gate determinista** (Auditgate) | Lo nuevo que se introduce en un PR se bloquea; la deuda previa se reporta | Que el artefacto publicado sea el que se escaneó |
| **SBOM CycloneDX** (Trivy) | Qué componentes lleva realmente el artefacto y si aparece un CVE conocido | Cómo entró el componente ni quién lo firmó |
| **Firma + provenance** (cosign / SLSA) | Que el artefacto viene de este pipeline y no fue sustituido | Que el código sea seguro |

> **Regla del laboratorio:** el escaneo y la firma se hacen **sobre su repositorio y su VM**. No escaneen ni firmen artefactos de despliegues ajenos sin autorización escrita (Ley 1273 de 2009). Todo lo que aquí se firme es un artefacto de prueba.

## 0. Preparar (15 min)

```bash
# En su repositorio de equipo (o en su fork del material del curso)
cd <repo-de-su-equipo>

auditgate --version || pipx install "git+https://github.com/Jawy77/auditgate"
semgrep --version   || pipx install semgrep
gitleaks version    || echo "Instalen gitleaks: https://github.com/gitleaks/gitleaks#installing"
osv-scanner --version || echo "Instalen osv-scanner: https://google.github.io/osv-scanner/installation/"
trivy --version     || echo "Instalen trivy: https://trivy.dev/latest/getting-started/installation/"
cosign version      || echo "Instalen cosign: https://docs.sigstore.dev/cosign/installation/"

mkdir -p seguridad/lab3

# Si van a trabajar desde un fork, dejen el repo original como upstream
git remote add upstream https://github.com/Hackwy402/desarrollo-seguro-ucp.git 2>/dev/null || true
git fetch upstream main
```

Instalar el gate en el repo (una sola vez) y comprobarlo:

```bash
auditgate init --provider none --yes
auditgate doctor
git add .github/workflows/auditgate.yml
git commit -m "ci: instala Auditgate"
git push
```

`auditgate init` escribe el workflow fijado por SHA y configura las variables del repo. El agente de IA es opcional: el gate determinista funciona igual sin llave.

> En esta VM `api.osv.dev` puede estar bloqueado, así que el check `deps` falla localmente. Para validar en la terminal usen `--checks secrets,sast,actions`; el check de dependencias sí corre en GitHub Actions.

## 1. Gate determinista: bloquear solo lo nuevo (45 min)

El gate compara los commits del PR contra la rama base. Por eso **todo debe estar commiteado**: `auditgate scan` trabaja en un worktree temporal y no mira archivos sueltos.

```bash
BASE=upstream/main        # en un repo propio: origin/main

# 1) Un PR limpio: el gate pasa
git switch -c lab3/demo-gate
echo "# Evidencia del laboratorio 3" >> seguridad/lab3/README.md
git add seguridad/lab3/README.md && git commit -m "docs(lab3): crea carpeta de evidencia"
auditgate scan --base "$BASE" --checks secrets,sast,actions --json > seguridad/lab3/gate-limpio.json
python3 -c "import json;print(json.load(open('seguridad/lab3/gate-limpio.json'))['gate'])"
```

Ahora introduzcan **un** cambio vulnerable pequeño (por ejemplo, concatenar un parámetro en una consulta o dejar `debug=True`). No es necesario explotarlo: el gate solo busca el patrón.

```bash
# 2) El PR con el hallazgo nuevo: el gate bloquea
git commit -am "demo: cambio inseguro para el laboratorio"
auditgate scan --base "$BASE" --checks secrets,sast,actions --json > seguridad/lab3/gate-bloqueado.json
python3 - <<'PY'
import json
d = json.load(open('seguridad/lab3/gate-bloqueado.json'))
print('gate:', d['gate'])
for c in d['checks']:
    for f in c['findings']:
        print(f"{c['id']:8} {f['path']}:{f['line']}  {f['rule']}")
PY
```

Hagan **triage** en `seguridad/lab3/TRIAGE.md`: cada hallazgo con regla, `archivo:línea`, ¿verdadero o falso positivo?, por qué y la fila ASVS relacionada (reutilicen `labs/LAB2.md` §2). Un falso positivo bien justificado vale tanto como un verdadero positivo; «falso positivo» sin explicación no vale.

Corrijan el hallazgo y dejen el pase:

```bash
git commit -am "fix: corrige el hallazgo introducido"
auditgate scan --base "$BASE" --checks secrets,sast,actions --json > seguridad/lab3/gate-final.json
python3 -c "import json;print(json.load(open('seguridad/lab3/gate-final.json'))['gate'])"
```

Guarden en la carpeta: `gate-limpio.json`, `gate-bloqueado.json`, `gate-final.json` y `TRIAGE.md`.

## 2. SBOM CycloneDX: ¿qué lleva realmente el artefacto? (45 min)

Usen su aplicación o el proyecto de ejemplo de la demo de Log4Shell (`../demos/sesion-4/log4shell/proyecto-java`). La pregunta es concreta: **¿dónde usamos `log4j`?**

```bash
# Inventario del código fuente
trivy fs --quiet --format cyclonedx --output seguridad/lab3/sbom.cdx.json .

# ¿Qué componentes sensibles aparecen?
python3 - <<'PY'
import json
d = json.load(open('seguridad/lab3/sbom.cdx.json'))
print(f"{len(d['components'])} componentes")
for c in d['components']:
    if any(k in c['name'].lower() for k in ('log4j', 'sqlite', 'gunicorn', 'flask')):
        print(' ', c.get('group',''), c['name'], c.get('version',''))
PY

# Cruzar el inventario con vulnerabilidades conocidas
trivy sbom seguridad/lab3/sbom.cdx.json --scanners vuln --severity CRITICAL \
  --format json --output seguridad/lab3/trivy-sbom.json || true
```

Si van sobre el proyecto Java, ejecuten también la demo completa y comparen el antes y el después:

```bash
bash ../demos/sesion-4/log4shell/demo-log4shell.sh
```

En `seguridad/lab3/SBOM.md` respondan:

1. ¿Cuántos componentes tiene el SBOM y cuáles son transitivos?
2. ¿Aparece `log4j-core`? ¿En qué versión? ¿Qué CVE Critical dispara?
3. ¿El manifiesto declaraba esa versión o entró por una dependencia transitiva?
4. ¿Qué cambia en el SBOM después de corregir la versión?

Adjunto: `sbom.cdx.json` y `trivy-sbom.json`.

## 3. Firma y provenance: quién publicó el artefacto (60 min)

Un SBOM dice *qué* hay; la firma dice *quién* lo publicó. Primero una llave local para el laboratorio:

```bash
cd seguridad/lab3
cosign generate-key-pair            # crea cosign.key (privada) y cosign.pub (pública)

# Artefacto de prueba: usen el Dockerfile de su app o el de la demo
docker build -t devseguro-ucp/lab3:demo ../../demos/sesion-1/03-api

cosign sign --key cosign.key devseguro-ucp/lab3:demo
cosign verify --key cosign.pub devseguro-ucp/lab3:demo > firma-verificada.json
```

**No suban `cosign.key` al repositorio.** La pública sí se entrega como evidencia. Añadan a `.gitignore`:

```
seguridad/lab3/cosign.key
```

En CI el modelo es keyless: el workflow de Auditgate genera provenance SLSA y firma con cosign sin llaves de larga duración (`id-token: write`, `secrets: inherit`). En `seguridad/lab3/FIRMA.md` expliquen la diferencia:

| | Laboratorio (local) | CI (GitHub Actions) |
|---|---|---|
| Llave | `cosign.key` en la VM | Keyless, OIDC del job |
| Identidad | Quien tiene la llave | El workflow y el repo |
| Caducidad | La del certificado/llave | Corta, ligada al run |
| Evidencia | `firma-verificada.json` | Provenance SLSA + attestation |

Adjunto: `cosign.pub`, `firma-verificada.json` y `FIRMA.md`.

## 4. Corregir un hallazgo con su prueba (45 min)

Igual que en LAB2 §4, pero con la evidencia del gate:

1. Elijan **un** hallazgo de `TRIAGE.md` (prefieran V6, V8 o V9).
2. Escriban una **prueba que falle antes** y demuestre la falla.
3. Implementen el control sin romper las demás pruebas.
4. Vuelvan a correr `auditgate scan --base "$BASE" --checks secrets,sast,actions` y sus pruebas.
5. Abran el PR con esta descripción:

```
Requisito ASVS: Vx.y — <texto del requisito>
Amenaza del Lab 1 mitigada: <nombre>
Hallazgo del gate: <regla> en <archivo:línea>
Cómo ejecutar la prueba: <comando>
Evidencia: seguridad/lab3/gate-final.json
```

```bash
git push -u origin lab3/demo-gate
gh pr create --base main --head lab3/demo-gate \
  --title "fix(lab3): corrige hallazgo de SAST" \
  --body-file seguridad/lab3/PR.md
```

## 5. ¿Hicimos un buen trabajo? (15 min)

En `seguridad/lab3/REFLEXION.md`, tres párrafos cortos:

- ¿Qué hallazgo era deuda previa y cuál era nuevo? ¿Cómo lo supieron?
- ¿Qué les dio el SBOM que no les dio el SAST, y qué les dio la firma que no les dio el SBOM?
- Si el gate bloquea solo lo nuevo, ¿cómo se paga la deuda antigua? (PISTA: Dependabot, issues de remediación y PRs pequeños; no desactivando el gate).

## Entrega

En `seguridad/lab3/`:

1. `README.md` con el índice de evidencias.
2. `gate-limpio.json`, `gate-bloqueado.json`, `gate-final.json` y `TRIAGE.md`.
3. `SBOM.md`, `sbom.cdx.json` y `trivy-sbom.json`.
4. `FIRMA.md`, `cosign.pub` y `firma-verificada.json` (**nunca** `cosign.key`).
5. `PR.md` y el enlace al pull request de la sección 4.
6. `REFLEXION.md`.

Esto es exactamente el **entregable 2** de la [plantilla del proyecto](../proyecto/PLANTILLA.md): workflow, etapas (secretos, SAST, SCA, imágenes, DAST, IaC, SBOM, firma) y políticas de bloqueo.

Comenten el enlace en el issue de su equipo.

## Rúbrica

| Criterio | Peso | Sobresaliente | Aceptable | Insuficiente |
|---|---|---|---|---|
| Gate determinista y triaje | 30 % | Tres estados del gate con JSON, triaje justificado y ligado a ASVS | Resultados sin triaje o sin evidencia | Sin ejecutar el gate |
| SBOM CycloneDX | 25 % | Inventario real, CVE cruzado y análisis transitivo | SBOM generado sin análisis | Sin SBOM |
| Firma y provenance | 20 % | Firma verificada, llave privada fuera del repo y comparación keyless/local | Firma sin verificar | Sin firma |
| Corrección con prueba | 20 % | Prueba que falla antes, pasa después y PR con ASVS + amenaza | Corrección sin prueba | Sin corrección |
| Reflexión | 5 % | Respuestas con datos propios | Respuestas genéricas | Ausente |

Los laboratorios entregados después de la sesión se reciben hasta la siguiente con una penalización del 20 %.
