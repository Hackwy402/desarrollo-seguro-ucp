# app-pedidos — app de ejemplo para el gate en el PR

Servicio Java mínimo (Maven) que representa **"el producto del equipo"**. El gate
de seguridad (`.github/workflows/gate.yml`) lo escanea en **cada Pull Request** y
**bloquea el merge** si encuentra vulnerabilidades. Una IA comenta el PR en
español explicando cada hallazgo y cómo corregirlo.

> A diferencia de los labs `labs/*` (deliberadamente vulnerables para explotarlos),
> esta app es "el código real" que el gate protege. Aquí la vulnerabilidad **no se
> explota**: se **detecta por la dependencia** (SCA) antes de llegar a producción.

## El ejercicio (dentro de UN mismo PR)

1. Este PR agrega la "feature de logging" con **log4j 2.14.1** → arrastra
   **CVE-2021-44228 (Log4Shell)** + otras 8 CVEs.
2. El gate corre en el PR, lo **bloquea** (check rojo) y la IA comenta el detalle.
3. Parchas la dependencia **en el mismo PR** y vuelves a pushear.
4. El gate re-evalúa: **verde** → el PR ya se puede mergear.

## Lección clave: el fix histórico ya no basta

El parche famoso de Log4Shell (diciembre 2021) fue **2.17.1**. Hoy **no alcanza**:
hay CVEs posteriores (2025–2026) en log4j corregidas recién en 2.25.x / 2.26.1.

| Versión | Resultado del gate |
|---|---|
| `2.14.1` | 🚫 9 CVEs (Log4Shell CRITICAL + …) |
| `2.17.1` | 🚫 aún 5 MEDIUM (CVEs 2025/2026) — "el fix de 2021 caducó" |
| `2.26.1` | ✅ 0 hallazgos — versión vigente |

La seguridad es un blanco móvil: el gate no te pide "el parche de la noticia", te
pide **una versión soportada hoy**. Por eso el escaneo se corre en CI, siempre.

## Correr el gate localmente (igual que en CI)

```bash
cd ~/desarrollo-seguro-ucp
bash seclab/bin/scan.sh --with-trivy --no-anim seclab/ci-demo-app
```
Trivy trae su base de vulnerabilidades desde ghcr.io (no depende de osv.dev).
