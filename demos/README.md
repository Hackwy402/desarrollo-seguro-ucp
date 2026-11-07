# Demos de la sesión 1

Demos en vivo del docente. Cada una conecta un tema de la sesión con herramientas reales (Docker, GitHub, Semgrep, gitleaks, Trivy, npm, git). Los estudiantes pueden repetirlas después en su VM.

Todos los scripts se ejecutan desde la raíz del repositorio y avanzan con **Enter** en cada paso, para explicar entre paso y paso.

## Antes de la clase

```bash
# Imágenes descargadas con anticipación (evita esperar en vivo)
docker pull bkimminich/juice-shop:latest
docker pull node:22-slim
docker pull python:3.12-slim
docker pull python:latest
SECRET_KEY=x docker compose -f demos/app/docker-compose.yml build

# Base de vulnerabilidades de Trivy actualizada
trivy fs --download-db-only 2>/dev/null || trivy image --download-db-only
```

- Proyectar desde una VM o un perfil limpio: `docker ps` sin filtro muestra todos los contenedores del equipo.
- Tener abierta la app de escritorio de OWASP Threat Dragon para la demo 8.
- Tener `gh auth status` en verde para la demo 7.

## Guion y tiempos

| Hora | Demo | Script | Tema de la sesión | Lo que tienen que ver |
|---|---|---|---|---|
| 8:20 | 1. El entorno del curso | `bash demos/entorno/demo-entorno.sh` | Superficie mínima, SSDF PO.3 | `127.0.0.1:3000` contra `0.0.0.0:3001`: el mismo contenedor expuesto a toda la red |
| 9:00 | 2. Log4Shell: ¿dónde usamos log4j? | `bash demos/log4shell/demo-log4shell.sh` | Caso 1, inventario de dependencias | SBOM CycloneDX, CVE-2021-44228 detectada, corrección a 2.17.1 y escaneo limpio |
| 9:20 | 3. xz: lo publicado no es lo revisado | `bash demos/xz/demo-xz.sh` | Caso 2, integridad (SSDF PS) | `diff` entre `git archive` y el tarball: archivo de prueba extra y Makefile alterado |
| 9:35 | 4. Shai-Hulud: npm ejecuta código al instalar | `bash demos/npm-scripts/demo-npm.sh` | Caso 3, cadena de suministro (A03) | El script corre **en silencio**; la evidencia lo prueba; `--ignore-scripts` lo evita |
| 10:05 | 5. Principios en una API real | `bash demos/app/demo-app.sh` | Mediación completa, fallar seguro, seguro por defecto, mínimo privilegio | IDOR (200 contra 404), tumbar el servicio de permisos (200 contra 403), traza de depuración, root contra usuario `app`, Semgrep y Trivy encuentran todo |
| 10:45 | 6. Un secreto borrado sigue en Git | `bash demos/secretos/demo-secretos.sh` | Secretos fuera del código | `gitleaks dir` limpio y `gitleaks git` con hallazgo; `git show` lo recupera; hook pre-commit lo bloquea |
| 11:00 | 7. El pipeline bloquea un PR inseguro | `bash demos/github/demo-github.sh` | SSDLC: verificación automática (SSDF PW.7, PW.8) | PR con la versión insegura: fallan Semgrep, Trivy y gitleaks; rama protegida |
| 11:35 | 8. Modelo de amenazas en vivo | Threat Dragon (ver abajo) | Cuatro preguntas, STRIDE | Las fallas de la demo 5 aparecen como amenazas del diagrama |

### Demo 8: modelo de amenazas de la API de facturas

En Threat Dragon: **New model** → diagrama **STRIDE**. Construirlo en vivo preguntando al grupo:

1. Actor externo **Navegador**; procesos **API de facturas** y **Servicio de permisos**; almacén **Datos de facturas**.
2. Flujos: Navegador → API (token, id de factura); API → Permisos (usuario, documento); API → Datos.
3. Límite de confianza entre Navegador y API.
4. Con el elemento seleccionado, pedir amenazas por letra. Las que deben salir:
   - **I** en API → Datos: lectura de facturas ajenas cambiando el id (demo 5A).
   - **E** en API → Permisos: si Permisos no responde, se concede edición (demo 5B).
   - **I** en API: trazas de error con rutas y versiones (demo 5C).
   - **E** en el contenedor: proceso como root (demo 5D).
   - **S** en Navegador → API: tokens estáticos y sin expiración.
   - **R** en API: no hay registro de quién editó qué.
   - **D** en API → Permisos: sin límite de peticiones ni timeout corto.
5. Cerrar con la cuarta pregunta: «¿lo hicimos suficientemente bien?» Las demos 5E y 7 son la verificación.

## Notas de seguridad de las demos

- Todo corre en `127.0.0.1`, en contenedores desechables o en carpetas temporales.
- Los tokens de las demos 6 y 7 son **falsos** y se generan al ejecutar; no hay ningún secreto en el repositorio.
- La demo 4 corre sin red (`--network none`) y su script solo imprime lo que vería; no lee ni envía archivos.
- La demo 7 crea un repositorio **privado** en la cuenta del docente. Para borrarlo al final: `gh repo delete demo-facturas-ucp --yes`.
- Las versiones de las herramientas en `demos/github/seguridad.yml` están fijadas. Antes de clase confirmen que la versión de Trivy es una posterior al incidente de marzo de 2026.
