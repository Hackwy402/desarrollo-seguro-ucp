# Laboratorio 2 · Verificación ASVS 5.0 de la aplicación del equipo

**Sesión 3 · sábado 14 de noviembre · 2:10 a 4:10 p. m. (120 min) · 7,5 % de la nota**
**Entrega:** 4:10 p. m., como comentario en el issue de su equipo con el enlace a la carpeta y al pull request.

En la mañana corregimos la Billetera UCP con pruebas que ya estaban escritas. Ahora la pregunta es la cuarta del modelado de amenazas aplicada a **su** aplicación: **¿hicimos un buen trabajo?** La respuesta se da con evidencia y no con opiniones. Esa evidencia sale de tres fuentes que se complementan:

| Fuente | Qué encuentra | Qué no encuentra |
|---|---|---|
| **Revisión con ASVS** (humana) | Autorización, lógica de negocio, diseño | Lo que nadie se acordó de revisar |
| **SAST** (Semgrep) | Patrones en el código: `md5`, `verify_signature: False`, SQL concatenado, secretos | Si el control existe en otra capa |
| **DAST** (ZAP) | Lo que se ve desde afuera: cabeceras, errores 500, configuración | BOLA, asignación masiva, tokens falsificados (lo vimos en la demo) |

> **Regla del laboratorio:** el escaneo dinámico se hace **solo contra su aplicación corriendo en su VM, en `127.0.0.1`**. Nunca contra un ambiente desplegado de la empresa, ni contra el de otro equipo, ni contra un tercero, sin autorización escrita (Ley 1273 de 2009).

## 0. Preparar (10 min)

```bash
docker image inspect ghcr.io/zaproxy/zaproxy:stable >/dev/null || docker pull ghcr.io/zaproxy/zaproxy:stable
semgrep --version || pipx install semgrep
mkdir -p seguridad/lab2        # en el repositorio de su equipo
```

Levanten su aplicación en la VM. Si no puede correr completa, usen el módulo que modelaron en el Lab 1 o, como último recurso, la Billetera UCP (con penalización en el criterio de alcance).

## 1. Revisión con ASVS 5.0 nivel 1 (40 min)

Copien la tabla en `seguridad/lab2/ASVS.md`. Para **cada fila** busquen el requisito exacto en [ASVS 5.0](https://github.com/OWASP/ASVS/tree/master/5.0/en) (nivel 1), anoten su número y decidan con evidencia: **Cumple**, **No cumple** o **No aplica** (con una línea de justificación).

| # | Capítulo | Qué verificar | Requisito ASVS (número) | Estado | Evidencia (archivo:línea, prueba, captura) |
|---|---|---|---|---|---|
| 1 | V6 Autenticación | Contraseñas de mínimo 8 caracteres (ASVS recomienda 15), sin reglas de composición, contra una lista de comunes | | | |
| 2 | V6 / V11 | Contraseñas con un hash lento y con sal (Argon2id, scrypt, bcrypt, PBKDF2) | | | |
| 3 | V6 | Límite de intentos o protección contra fuerza bruta en el login | | | |
| 4 | V6 | El login y la recuperación no revelan si el usuario existe | | | |
| 5 | V7 Sesiones | La sesión expira y el cierre de sesión la invalida en el servidor | | | |
| 6 | V7 | Cookie de sesión con `Secure`, `HttpOnly` y `SameSite` (si usan cookies) | | | |
| 7 | V9 Tokens | La firma del token se verifica con una lista fija de algoritmos | | | |
| 8 | V9 | El token tiene `exp`, y se validan emisor y audiencia | | | |
| 9 | V8 Autorización | Cada consulta a un objeto filtra por el dueño o por el permiso (BOLA) | | | |
| 10 | V8 | Los campos sensibles (rol, saldo, estado) no se pueden escribir desde el cliente | | | |
| 11 | V8 | La autorización se aplica en el servidor, no solo ocultando botones | | | |
| 12 | V4 APIs | Las respuestas no devuelven más campos de los necesarios | | | |
| 13 | V4 / V2 | Paginación con límite máximo; límites de tamaño en las peticiones | | | |
| 14 | V1 Codificación | Consultas parametrizadas en todo acceso a datos | | | |
| 15 | V1 | Salida escapada según el contexto (HTML, JS, URL) | | | |
| 16 | V11 Criptografía | Datos sensibles en reposo con cifrado autenticado (o justificación de por qué no) | | | |
| 17 | V11 / V13 | Ninguna llave, secreto o contraseña en el código ni en el historial de git | | | |
| 18 | V12 Comunicación | TLS en todo tráfico externo; HSTS en producción | | | |
| 19 | V13 Configuración | Debug apagado, sin trazas al usuario, cabeceras de seguridad | | | |
| 20 | V16 Registro | Se registran los fallos de autenticación y de autorización, sin datos sensibles | | | |

Agreguen **las 5 filas del top 5 de su Lab 1**, con el requisito que escribieron. Son las más importantes: comprueben si su control existe.

## 2. Análisis estático con Semgrep (20 min)

```bash
semgrep scan --config p/owasp-top-ten --config p/secrets \
  --config ~/desarrollo-seguro-ucp/demos/sesion-3/01-semgrep/reglas-billetera.yml \
  --metrics=off --sarif -o seguridad/lab2/semgrep.sarif .
semgrep scan --config p/owasp-top-ten --config p/secrets --metrics=off .     # para leerlo en pantalla
```

(Cambien `p/owasp-top-ten` por el conjunto de su lenguaje si aplica: `p/javascript`, `p/java`, `p/csharp`, `p/php`, `p/golang`.)

**Triage** en `seguridad/lab2/TRIAGE.md`: para **cada hallazgo** de severidad ERROR (máximo 15), una fila:

| Regla | Archivo:línea | ¿Verdadero o falso positivo? | Por qué | Fila ASVS relacionada |
|---|---|---|---|---|

Un falso positivo bien justificado vale tanto como un verdadero positivo. «Falso positivo» sin explicación no vale.

## 3. Análisis dinámico con ZAP (20 min)

Con su aplicación corriendo **en la VM**. Elijan la variante:

```bash
# A) Tienen especificación OpenAPI/Swagger
docker run --rm --network host -v "$PWD/seguridad/lab2":/zap/wrk:rw ghcr.io/zaproxy/zaproxy:stable \
  zap-api-scan.py -t http://127.0.0.1:PUERTO/openapi.json -f openapi -r zap.html -I

# B) Aplicación web sin especificación: escaneo pasivo
docker run --rm --network host -v "$PWD/seguridad/lab2":/zap/wrk:rw ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://127.0.0.1:PUERTO -r zap.html -I
```

(`--network host` funciona en la VM Linux del curso. Si su aplicación corre en Docker Compose, usen `--network NOMBRE_red` y el nombre del servicio, como en `demos/sesion-3/02-billetera/zap/zap-api.sh`. Si necesita sesión, pasen un token de un **usuario de prueba** con `-e ZAP_AUTH_HEADER=Authorization -e ZAP_AUTH_HEADER_VALUE="Bearer …"`.)

Lleven cada alerta Medium o High a la tabla de triage, con la fila ASVS que corresponde.

## 4. Corregir una falla con su prueba (25 min)

Elijan **un** «No cumple» de la sección 1 (de preferencia de V6, V8 o V9) y hagan lo mismo que en las katas:

1. Una **prueba automática que falle** y demuestre la falla (como las de `tests/` de la billetera).
2. El **control** que la hace pasar, sin romper las demás pruebas.
3. Un **pull request** que diga en la descripción: requisito ASVS, amenaza del Lab 1 que mitiga (si aplica), y cómo ejecutar la prueba.

## 5. ¿Hicimos un buen trabajo? (5 min)

En `ASVS.md`, tres líneas: ¿cuántos requisitos cumplen de los 25? ¿Qué encontró la revisión humana que ninguna herramienta encontró? ¿Qué falso positivo les hizo perder más tiempo?

## Entrega

En el repositorio de su equipo, carpeta `seguridad/lab2/`:

1. `ASVS.md`: la tabla de 25 filas y las respuestas de la sección 5.
2. `semgrep.sarif` y `TRIAGE.md`.
3. `zap.html`.
4. El enlace al pull request de la sección 4.

Comenten el enlace en el issue de su equipo. La tabla de ASVS es la sección 3 del [proyecto integrador](../proyecto/PLANTILLA.md) y el inicio del checklist del informe final.

## Rúbrica (7,5 %)

| Criterio | Peso | Sobresaliente | Aceptable | Insuficiente |
|---|---|---|---|---|
| Revisión ASVS | 35 % | 25 filas con número de requisito, estado y evidencia concreta (archivo:línea o prueba) | Estados sin evidencia o filas faltantes | Menos de 15 filas o sin números de requisito |
| Triage SAST y DAST | 25 % | Cada hallazgo clasificado y justificado, ligado a ASVS | Clasificación sin justificar | Reportes adjuntos sin análisis |
| Corrección con prueba | 30 % | Prueba que falla antes y pasa después; PR con requisito y amenaza | Corrección sin prueba o prueba que no demuestra la falla | Sin corrección |
| Reflexión | 10 % | Responde con datos propios | Respuestas genéricas | Ausente |

Los laboratorios entregados después de la sesión se reciben hasta la sesión siguiente con una penalización del 20 %.
