# Demos de la sesión 3 (sábado 14 de noviembre)

Verificación del código: análisis estático con reglas propias.

| Demo | Script | Qué muestra |
|---|---|---|
| Semgrep con reglas propias | `bash demos/sesion-3/semgrep/demo-semgrep.sh` | Las fallas de la API de la sesión 1 (falla abierta, depuración activa, secreto en código, CORS abierto) detectadas por reglas escritas por el equipo; la versión segura sale limpia |

Las reglas están en `semgrep/reglas-principios.yml`, cada una con su CWE y su categoría del OWASP Top 10:2025.
