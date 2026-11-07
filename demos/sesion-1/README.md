# Demos de la sesión 1 (sábado 7 de noviembre, virtual)

Ocho demos en vivo del docente, todas sobre temas de la Unidad 1: principios de seguridad, panorama de amenazas, ciclo de vida de desarrollo seguro y modelado de amenazas. Los estudiantes las pueden repetir después en su VM.

Los scripts se ejecutan desde la raíz del repositorio y avanzan con **Enter** en cada paso. Los diagramas que acompañan cada demo están en [`docs/`](../../docs/README.md).

## Antes de la clase

```bash
docker pull bkimminich/juice-shop:latest
docker pull python:3.12-slim && docker pull python:latest
docker pull postgres:16-alpine
docker pull gcc:14 && docker pull rust:1.88-slim
SECRET_KEY=x docker compose -f demos/sesion-1/03-api/docker-compose.yml build
docker build -q -t ucp-pytm demos/sesion-1/08-modelo-amenazas
```

- Proyectar desde una VM o un perfil limpio: `docker ps` sin filtro muestra todos los contenedores del equipo.
- Tener abiertos el navegador y `docs/diagramas/png/` para ir mostrando cada diagrama.

## Guion

| Hora | Demo | Script | Tema | Lo que tienen que ver |
|---|---|---|---|---|
| 8:20 | 1. El entorno del curso | `bash demos/sesion-1/01-entorno/demo-entorno.sh` | Superficie mínima · SSDF PO.3 | `127.0.0.1:3000` contra `0.0.0.0:3001`: el mismo contenedor expuesto a toda la red |
| 9:10 | 2. xz: lo publicado no es lo revisado | `bash demos/sesion-1/02-xz/demo-xz.sh` | Caso real · integridad, diseño abierto | `diff` entre `git archive` y el tarball: archivo extra y Makefile alterado; hashes distintos |
| 9:30 | 3. Principios en una API real | `bash demos/sesion-1/03-api/demo-api.sh` | Mediación completa · fallar de forma segura · seguro por defecto | IDOR (200 contra 404); tumbar el servicio de permisos (200 contra 403); traza de depuración en el navegador |
| 10:35 | 4. Mínimo privilegio en la base de datos | `bash demos/sesion-1/04-minimo-privilegio-bd/demo-bd.sh` | Mínimo privilegio · separación de privilegios | El usuario de la app no puede leer cédulas, borrar ni hacer `DROP`; el dueño sí |
| 10:50 | 5. Defensa en profundidad | `bash demos/sesion-1/05-defensa-profundidad/demo-capas.sh` | Defensa en profundidad | Con el «atacante» dentro de la API: PERMITIDO contra BLOQUEADO por capa; `CapEff`, `NoNewPrivs`, límites |
| 11:05 | 6. Seguridad de memoria | `bash demos/sesion-1/06-memoria/demo-memoria.sh` | Seguro por defecto desde el lenguaje | En C la `X` (88) sobrescribe `es_admin`; `_FORTIFY_SOURCE` aborta; Rust se detiene con *index out of bounds* |
| 11:20 | 7. SAMM en vivo | [`07-samm/README.md`](07-samm/README.md) | Madurez del SSDLC | Autoevaluación con el grupo de cinco prácticas, una por función de negocio |
| 11:35 | 8. Modelo de amenazas como código | `bash demos/sesion-1/08-modelo-amenazas/demo-modelo.sh` | Cuatro preguntas · STRIDE | pytm genera el diagrama desde código y 109 amenazas candidatas; el equipo prioriza 9 y agrega la que la herramienta no ve |

## Qué NO está aquí

Las herramientas de verificación y de cadena de suministro tienen su propia sesión, para no adelantar los laboratorios:

- Semgrep con reglas propias → [`../sesion-3`](../sesion-3/README.md) (14 de noviembre).
- SBOM, scripts de npm, gitleaks, Trivy y el pipeline de GitHub → [`../sesion-4`](../sesion-4/README.md) (20 de noviembre).

## Notas de seguridad

- Todo corre en `127.0.0.1`, en contenedores desechables (`--rm`) y, cuando no hace falta red, con `--network none`.
- PostgreSQL de la demo 4 no publica puertos; sus contraseñas son de demostración y el contenedor se borra al terminar.
- Las demos 2 y 6 trabajan en carpetas temporales.
