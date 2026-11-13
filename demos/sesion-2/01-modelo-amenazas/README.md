# Demo 1 · Modelo de amenazas de la Tienda UCP con OWASP Threat Dragon

El mismo sistema que corrigen en las katas (`../02-tienda`), modelado antes de tocar el código.

```bash
bash demos/sesion-2/01-modelo-amenazas/threat-dragon.sh      # http://127.0.0.1:8080
```

En una VM con procesador ARM la imagen corre emulada (es `linux/amd64`): el primer arranque tarda unos 20 s.

## Guion (30 min)

| Min | Pregunta del Threat Modeling Manifesto | En Threat Dragon |
|---|---|---|
| 0–8 | **¿En qué estamos trabajando?** | Abrir `tienda-ucp.json`. Recorrer actores, procesos, almacenes y flujos. Señalar los dos límites de confianza: Internet → servidor y servidor → pasarela. |
| 8–20 | **¿Qué puede salir mal?** | Seleccionar cada elemento y leer sus amenazas STRIDE. Preguntar al grupo antes de abrir cada una: «¿qué le puede pasar a este flujo?». |
| 20–26 | **¿Qué vamos a hacer al respecto?** | Cada amenaza tiene su mitigación con el capítulo de ASVS 5.0 y la kata que la verifica. Mostrar que el modelo genera requisitos, no solo una lista de miedos. |
| 26–30 | **¿Hicimos un buen trabajo?** | Botón **Report**: el informe es el entregable. Las 7 katas son la prueba de que las mitigaciones funcionan. |

## Las 16 amenazas del modelo

| Elemento | STRIDE | Amenaza | Severidad | Kata |
|---|---|---|---|---|
| API Tienda | E | A01 · IDOR: leer el pedido de otro cliente | Alta | `a01_acceso` |
| API Tienda | T | A06 · El cliente decide el precio y la cantidad | Alta | `a06_diseno` |
| API Tienda | T | A06 · Cupón de un solo uso reutilizable y transferible | Media | `a06_diseno` |
| API Tienda | I | A02 · CORS refleja cualquier origen con credenciales | Alta | `a02_config` |
| API Tienda | I | A02/A10 · Errores con traza y modo depuración | Media | `a02_config` |
| API Tienda | R | A09 · Sin registro de eventos de seguridad | Media | — |
| API Tienda | D | Abuso sin límite de solicitudes | Media | — |
| API Tienda | S | Tokens estáticos sin expiración | Media | sesión 3 |
| Generador de reportes | E | A05 · Inyección de comandos | Alta | `a05_comandos` |
| Generador de reportes | T | Path traversal en el nombre | Media | `a05_comandos` |
| Base de datos | I | Datos personales y hashes expuestos | Alta | — |
| Archivos de reportes | I | Reportes legibles en el servidor | Baja | — |
| Cliente → API | I | Tráfico interceptable o degradable a HTTP | Media | — |
| API → Cliente | T | A05 · XSS almacenado en las reseñas | Alta | `a05_xss` |
| API → Base de datos | T | A05 · Inyección SQL en la búsqueda | Alta | `a05_sql` |
| Pasarela → API | T | A10 · Falla abierta si la pasarela no responde | Alta | `a10_excepciones` |

Las que no tienen kata quedan como **riesgo residual** o se trabajan en otras sesiones: así se ve un modelo real.
