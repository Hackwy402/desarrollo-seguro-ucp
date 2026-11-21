# Lab: Log4Shell + Security Gate (Ubuntu)

Simula una feature que mete una dependencia vulnerable (**Log4Shell**, CVE-2021-44228),
deja que el **gate de seguridad** la bloquee y la explique con **IA**, y la parchea
hasta ponerlo en verde.

## 1. Requisitos (una sola vez)

```bash
# Docker (los escaneres corren en contenedores; no instalas nada mas) + git + gh
sudo apt-get update && sudo apt-get install -y docker.io git gh
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"   # cierra sesion y vuelve a entrar, o: newgrp docker
docker info >/dev/null && echo "Docker OK"
gh auth login                     # para abrir tu PR (paso 6)
```

## 2. Clona el repo

```bash
git clone https://github.com/Hackwy402/desarrollo-seguro-ucp.git
cd desarrollo-seguro-ucp
```

## 3. (Opcional) Tu API key de IA — gratis

La IA explica cada CVE y cómo corregirlo. **No es obligatoria**: sin key, el gate
igual escanea y bloquea.

- **Groq (gratis):** crea una key en <https://console.groq.com> → empieza con `gsk_...`
- O **Kimi/Moonshot:** <https://platform.moonshot.ai> → `sk-ms-...`

No necesitas escribirla en ningún archivo a mano: **el lab te la pedirá oculta** la
primera vez y la guardará (si quieres) en `seclab/.env`, que **está en `.gitignore`**
(nunca se sube). El prompt además **limpia el pegado** (espacios/comillas), **detecta
tu proveedor** por el prefijo (`gsk_` → Groq, `sk-ms-` → Kimi) y **valida la key**
contra el endpoint antes de guardarla: si está mal copiada, te avisa y la vuelve a
pedir en vez de guardar basura. Si prefieres dejarla lista a mano:

```bash
cp seclab/.env.example seclab/.env && chmod 600 seclab/.env
# edita seclab/.env y pega tu key en GATE_AI_API_KEY=
```

## 4. Corre el lab (un comando)

```bash
bash seclab/bin/lab.sh
```

Verás el ciclo completo:

1. **🔴 Rojo** — el gate encuentra Log4Shell y **bloquea** (exit 1). Si pusiste key,
   la IA comenta qué es cada CVE y a qué versión subir.
2. **Parche** — el lab cambia `log4j` a **2.26.1** en `pom.xml`.
3. **🟢 Verde** — re-escanea: sin hallazgos (exit 0).

## 5. Hazlo a mano (si quieres entender cada paso)

```bash
# escaneo manual sobre la app
bash seclab/bin/scan.sh --with-trivy --ai seclab/ci-demo-app   # -> rojo (pide la key)

# parche manual
sed -i 's/2.14.1/2.26.1/g' seclab/ci-demo-app/pom.xml          # Ubuntu: sed -i sin ''

# re-escaneo
bash seclab/bin/scan.sh --with-trivy --ai seclab/ci-demo-app   # -> verde
```

## 6. Abre tu PR y genera el informe (entrega en Moodle)

El gate también corre en **GitHub Actions** sobre tu Pull Request, usando el modelo
de IA ya configurado en el repo. Trabajas en **tu propia rama** del mismo repo.

```bash
# 1) abre tu PR con la app vulnerable -> el gate lo BLOQUEA (rojo) y la IA comenta
bash seclab/bin/lab-pr.sh

# 2) en GitHub mira el check `gate` en rojo + el comentario de la IA; luego parcha:
bash seclab/bin/lab-pr.sh --fix     # sube log4j a 2.26.1 -> el gate pasa a VERDE

# 3) genera tu informe (antes/después, CVEs, análisis IA, remediación)
bash seclab/bin/informe.sh          # escribe seclab/ci-demo-app/REPORTE.md

# 4) deja el informe en el repo y súbelo a Moodle
git add seclab/ci-demo-app/REPORTE.md
git commit -m "docs: informe del lab log4shell"
git push
```

**La API key en el PR:** el modelo está configurado como *secret* del repo
(`GATE_AI_API_KEY`) y **todos los PR del repo lo usan automáticamente** — no necesitas
poner nada para que la IA comente en tu PR. Para correr el gate **localmente** con tu
propia key usa `lab.sh` (te la pide oculta). Si quieres usar **tu** key en el CI (con
permiso del instructor): `gh secret set GATE_AI_API_KEY` — el secret es único por repo.

**Entrega:** sube a **Moodle** tu `REPORTE.md` (o su PDF) y el enlace a tu PR, del lab
de ayer y el de hoy.

## Seguridad de la key (importante)

- `seclab/.env` **nunca** entra a git (`seclab/.gitignore`). Se crea con permisos `600`.
- El propio gate corre **gitleaks**: si alguien intentara commitear una key, la caza.
- **Nunca** pegues la key en el prompt del shell directo ni en un commit; usa `seclab/.env`
  o deja que el lab te la pida oculta.

## La lección

El fix histórico de Log4Shell (**2.17.1**) corrige los CVE de 2021, pero **hoy no basta**:
hay CVEs de 2025/2026 en log4j. El gate exige una versión vigente (**2.26.1+**). Por eso
el pipeline no es "pasó una vez y listo": se re-evalúa contra bases de vulnerabilidades
actualizadas en cada PR.
