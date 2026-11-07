# Demos de la sesión 4 (viernes 20 de noviembre)

Cadena de suministro y DevSecOps. Los casos de Log4Shell y Shai-Hulud se presentan en la sesión 1 como panorama; aquí se trabajan con las herramientas.

| Demo | Script | Qué muestra |
|---|---|---|
| Log4Shell: ¿dónde usamos log4j? | `bash demos/sesion-4/log4shell/demo-log4shell.sh` | SBOM CycloneDX con Trivy, detección de CVE-2021-44228, corrección a 2.17.1 |
| npm ejecuta código al instalar | `bash demos/sesion-4/npm-scripts/demo-npm.sh` | El `postinstall` corre en silencio y ve los tokens; `--ignore-scripts` lo evita |
| Un secreto borrado sigue en Git | `bash demos/sesion-4/secretos/demo-secretos.sh` | `gitleaks git` encuentra el token en el historial; hook pre-commit lo bloquea |
| Dockerfile inseguro | `trivy config demos/sesion-1/03-api` | Imagen `latest`, sin `USER`, sin `HEALTHCHECK` |
| Pipeline que bloquea un PR | `bash demos/sesion-4/github/demo-github.sh` | Repositorio privado con Actions: gitleaks, Semgrep y Trivy fallan ante un PR inseguro |

La demo de GitHub crea un repositorio privado en la cuenta del docente; para borrarlo: `gh repo delete demo-facturas-ucp --yes`.
