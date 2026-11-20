| Campo             | Información                                                                                                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documento**     | Taller 1 - Modelo de Amenazas                                                                                                                                               |
| **Programa**      | Especialización en Desarrollo de Software                                                                                                                                   |
| **Asignatura**    | Optativa - Ciberseguridad Aplicada al Desarrollo de Software                                                                                                                |
| **Integrantes**   | Alexandra Giraldo Roman<br>Sergio Jaramillo Luna<br>Andrés Simbaqueba Del Rio                                                                                               |
| **Observaciones** | El taller fue elaborado con base en el proyecto base suministrado por el profesor debido a restricciones del repositorio propuesto de Aquasoft (se encuentra en producción) |

## 3. CALIFICACION DE AMENAZAS

### 3.1 Priorización (Impacto × Probabilidad = Riesgo)

| ID  | Amenaza                    | STRIDE | I (1–3) | P (1–3) | I×P   | Severity |
| --- | -------------------------- | ------ | ------- | ------- | ----- | -------- |
| T01 | Token sin expiración       | S      | 3       | 3       | **9** | High     |
| T03 | Inyección SQL              | T      | 3       | 3       | **9** | High     |
| T08 | IDOR pedidos               | I      | 3       | 3       | **9** | High     |
| T14 | Inyección de comandos      | E      | 3       | 3       | **9** | High     |
| T16 | Escalada de rol            | E      | 3       | 3       | **9** | High     |
| T02 | Webhook sin firma          | S      | 3       | 2       | **6** | Medium   |
| T04 | Precio enviado por cliente | T      | 3       | 2       | **6** | Medium   |
| T09 | CORS abierto               | I      | 2       | 3       | **6** | Medium   |
| T10 | XSS almacenado             | I      | 3       | 2       | **6** | Medium   |
| T15 | Path traversal             | E      | 3       | 2       | **6** | Medium   |
| T05 | Cupón reutilizable (race)  | T      | 2       | 2       | **4** | Medium   |
| T06 | Sin registro de auditoría  | R      | 2       | 2       | **4** | Medium   |
| T11 | Modo debug expuesto        | I      | 2       | 2       | **4** | Medium   |
| T12 | Sin rate limiting          | D      | 2       | 2       | **4** | Medium   |
| T07 | Reportes no auditados      | R      | 1       | 2       | **2** | Low      |
| T13 | Sin paginación             | D      | 1       | 2       | **2** | Low      |

### 3.2 Top 5 — Requisitos de seguridad verificables

| ID      | Amenaza                                           | STRIDE | I×P | Requisito de seguridad (verificable)                                                                                                                                                                                                                                                             | ASVS 5.0                                                                        | Cómo lo verificamos                                                                                                                                                                                  |
| ------- | ------------------------------------------------- | ------ | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **T01** | Token estático sin expiración ni revocación       | S      | 9   | Todo token de acceso debe tener un TTL máximo de 15 minutos y un TTL de refresco de 7 días. El endpoint `GET /pedidos/<id>` con un token emitido hace > 15 min debe responder `401 Unauthorized`.                                                                                                | **V7.1.1** (Tiempo de vida de tokens de sesión)                                 | Prueba automatizada: emitir token, avanzar el reloj de prueba 16 min con `freezegun`, verificar que `/pedidos/1` devuelve 401.                                                                       |
| **T03** | Inyección SQL en búsqueda                         | T      | 9   | Toda consulta SQL que use parámetros externos debe usar consultas parametrizadas (`?`). Un payload `' OR '1'='1` en `GET /productos?q=...` debe devolver solo los productos que coincidan literalmente con ese texto, nunca la tabla completa.                                                   | **V1.1** (Consultas parametrizadas / codificación de salida)                    | Prueba: `GET /productos?q=' OR '1'='1` → la respuesta JSON tiene 0 ítems; el log de BD no muestra `SELECT *`. Revisión de código: `grep -n "%" app.py` no debe encontrar f-strings en consultas SQL. |
| **T08** | IDOR — leer pedido ajeno                          | I      | 9   | Cada petición `GET /pedidos/<id>` debe verificar que el `id` pertenece al usuario autenticado. Una petición de `beto` a un pedido de `ana` debe devolver `404 Not Found` (no 403, para no revelar existencia).                                                                                   | **V8.3.1** (Autorización a nivel de objeto)                                     | Prueba: autenticar como `beto` y solicitar `GET /pedidos/1` (pedido de `ana`) → debe devolver `{"error": "no encontrado"}` con código 404.                                                           |
| **T14** | Inyección de comandos en nombre de reporte        | E      | 9   | El nombre del archivo de reporte debe validarse con una lista de caracteres permitidos (`[a-zA-Z0-9_\-.]`, máx. 64 chars) antes de ser usado en cualquier llamada a `subprocess`. Un nombre con `;`, `\|`, `&` o `..` debe rechazarse con `400 Bad Request`.                                     | **V1.1** (Codificación y sanitización de entrada) · **V5.3.3** (Path traversal) | Prueba: `POST /reportes` con `filename="test; id > /tmp/pwned"` → respuesta 400; verificar que `/tmp/pwned` no fue creado. Revisión: Semgrep regla `subprocess-shell-true`.                          |
| **T16** | Escalada de privilegios por campo `role` editable | E      | 9   | El endpoint `PUT /perfil` debe ignorar (o rechazar con 400) cualquier campo `role`, `is_admin` o similar que venga en el body. El perfil actualizado en BD no debe cambiar el rol del usuario. Un usuario normal que envíe `{"role": "admin"}` debe seguir siendo `role=user` tras la operación. | **V8.1.1** (Autorización de campo a nivel de objeto — BOPLA)                    | Prueba: `PUT /perfil` con `{"nombre": "nuevo", "role": "admin"}` → `GET /perfil` devuelve `role=user`. Revisión de código: validar que se use una allowlist de campos actualizables.                 |

## 4. ¿Qué quedó fuera del modelo?

El flujo de administración ( gestión del catalogo, alta de productos, gestión de cupones), infraestructura de despliegue y el proceso de recuperación de contraseña.

### ¿Qué amenaza nos sorprendió?

**T05 — Race condition en el cupón** fue la más sorprendente. Inicialmente el equipo asumió que como el código "verifica si el cupón ya fue usado", el problema estaba resuelto. Al dibujarlo en el DFD y analizar el flujo de datos entre la lectura y la escritura quedó claro que sin una transacción atómica la verificación no sirve. Ningún escáner estático habría encontrado esta falla — refuerza por qué el modelado de amenazas va antes del código, no después.
