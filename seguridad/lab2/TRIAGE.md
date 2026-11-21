# Laboratorio 2 · Triage de hallazgos (SAST y DAST) — Billetera UCP

## Hallazgos de Semgrep (SAST)

| Regla | Archivo:línea | Clasificación | Justificación | Fila ASVS relacionada |
|---|---|---|---|---|
| `hash-rapido-para-claves` | `app.py:56` | Verdadero positivo | Confirmado mediante prueba dirigida: `hashear()` usa `hashlib.md5` sin sal | 2 |
| `hash-rapido-para-claves` | `app.py:60` | Verdadero positivo | Misma causa; `verificar_clave()` compara contra el mismo hash MD5 | 2 |
| `secreto-en-el-codigo` | `app.py:69` | Verdadero positivo | La llave de cifrado `LLAVE_DATOS` está escrita como literal en el código fuente | 17 |
| `aes-modo-ecb` | `app.py:75` | Verdadero positivo | `cifrar()` usa `modes.ECB()`, confirmado por lectura directa del código | 16 |
| `aes-modo-ecb` | `app.py:80` | Verdadero positivo | Misma causa; `descifrar()` usa el mismo modo ECB | 16 |
| `secreto-en-el-codigo` | `app.py:91` | Verdadero positivo | `JWT_SECRETO` está escrito como literal y es un valor trivial de adivinar | 17 |
| `jwt-sin-verificar-firma` | `app.py:101` | Verdadero positivo | Confirmado mediante prueba dirigida: un token fabricado con un secreto arbitrario fue aceptado por `/api/perfil` | 7, 21 |
| `columna-desde-la-peticion` | `app.py:160` | Verdadero positivo | Confirmado mediante prueba dirigida: se envió `{"rol":"admin","saldo":999999999}` a `/api/perfil` y se aplicó sin validación | 10, 14, 22, 25 |
| `python.lang.security.insecure-hash-algorithms-md5.insecure-hash-algorithm-md5` | `app.py:56` | Verdadero positivo | Regla del set genérico `p/owasp-top-ten` que detecta el mismo uso de MD5 ya identificado por la regla propia `hash-rapido-para-claves` | 2 |
| `python.lang.security.insecure-hash-algorithms-md5.insecure-hash-algorithm-md5` | `app.py:60` | Verdadero positivo | Misma causa que el hallazgo anterior, sobre la verificación de la contraseña | 2 |
| `python.jwt.security.jwt-hardcode.jwt-python-hardcoded-secret` | `app.py:95` | Verdadero positivo | Señala el uso del secreto fijo `JWT_SECRETO` en el punto donde se firma el token; corresponde a la misma causa que `secreto-en-el-codigo` en la línea 91 | 17 |
| `python.jwt.security.unverified-jwt-decode.unverified-jwt-decode` | `app.py:101` | Verdadero positivo | Confirma, desde el set genérico, el mismo hallazgo que `jwt-sin-verificar-firma`: el token se decodifica con `verify_signature=False` | 7, 21 |
| `python.flask.security.injection.tainted-sql-string.tainted-sql-string` | `app.py:160` | Verdadero positivo | Confirma, desde el set genérico, el mismo hallazgo que `columna-desde-la-peticion` | 10, 14, 22, 25 |
| `python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host` | `app.py:183` | Falso positivo, en este contexto | El servidor se ejecuta dentro de un contenedor Docker; enlazar a `0.0.0.0` es necesario para que el puerto se exponga desde el contenedor al host mediante `docker compose`. El riesgo real que señala la regla (exposición no intencionada a toda la red) aplicaría si la aplicación corriera directamente sobre un sistema operativo sin contenedor | No corresponde a una fila específica de la tabla de 25 |

## Alertas de ZAP (DAST)

Se clasifican las alertas de severidad Medium y High del reporte `zap.html`. Se incluye además la alerta Low de error 500, porque está ligada a la causa real de la alerta Medium.

| Alerta | Severidad | URL y parámetro | Clasificación | Justificación | Fila ASVS relacionada |
|---|---|---|---|---|---|
| SQL Injection (CWE-89) | High | `POST /api/registro`, parámetro `usuario` | Falso positivo | ZAP comparó las respuestas a `zap AND 1=1 --` y `zap AND 1=2 --` y encontró diferencias. Sin embargo, `registro()` usa consultas parametrizadas con `?` en `app.py:113` y `app.py:115`, por lo que el valor nunca se interpreta como SQL. La diferencia entre respuestas se explica por el estado de la base de datos: el registro responde `409` si el usuario ya existe y `201` si se crea. La inyección real de la aplicación está en el nombre de columna de `PATCH /api/perfil` (`app.py:160`), que ZAP no detectó | 14 |
| Buffer Overflow (CWE-120) | Medium | `GET /api/cuentas/1/movimientos`, parámetro `limite` | Falso positivo como desbordamiento de búfer; evidencia una falla real de validación | Python administra la memoria, por lo que no existe sobrescritura de registros ni de la pila. ZAP envió una cadena de varios miles de caracteres y recibió un error del servidor porque `app.py:175` ejecuta `int(request.args.get("limite", 20))` sin validar el tipo ni el rango. La falla real es la ausencia de validación y de límites en el parámetro, la misma que permite `limite=-1` | 13 |
| A Server Error response code was returned (CWE-388) | Low | `GET /api/cuentas/1/movimientos`, parámetro `limite` | Verdadero positivo | Con `limite=http://www.google.com/` el servidor respondió `500`. La excepción `ValueError` de `int()` no se controla y no existe un manejador de errores; por lo tanto, una entrada inválida produce un error interno en lugar de un `400` | 13, 19 |
