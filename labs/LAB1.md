# Laboratorio 1 · Modelo de amenazas de la aplicación del equipo

**Sesión 2 · viernes 13 de noviembre · 60 min en clase · 7,5 % de la nota**
**Entrega:** al cierre del bloque (7:50 p. m.), como comentario en el issue de su equipo.

Van a hacer con **su** aplicación lo que vimos con la Tienda UCP en la demo 1: responder las cuatro preguntas del Threat Modeling Manifesto y salir con requisitos de seguridad verificables.

## Antes de empezar (5 min)

```bash
docker pull owasp/threat-dragon:stable
bash demos/sesion-2/01-modelo-amenazas/threat-dragon.sh     # http://127.0.0.1:8080
```

«Login to Local Session» → «Create a new, empty threat model». Tengan a mano el diagrama de arquitectura que trajeron.

Si su aplicación es muy grande, **acoten**: un flujo de negocio completo (por ejemplo, registro → login → compra) modelado a fondo vale más que todo el sistema en superficie.

## 1. ¿En qué estamos trabajando? (15 min)

Dibujen el diagrama de flujo de datos (DFD) en Threat Dragon:

- **Actores** (rectángulos): usuarios, administradores, sistemas externos (pasarelas, proveedores de identidad, APIs de terceros).
- **Procesos** (círculos): sus servicios, funciones, workers.
- **Almacenes** (dos líneas): bases de datos, buckets, colas, archivos, cachés.
- **Flujos** (flechas): qué dato viaja, en qué dirección y por qué protocolo. Llenen *Protocol*, *Encrypted* y *Public network*.
- **Límites de confianza** (línea punteada): en cada sitio donde cambia el nivel de confianza. Mínimo: Internet → su sistema, y su sistema → cada tercero.

> Regla práctica: **toda amenaza interesante cruza un límite de confianza.** Si su diagrama no tiene límites, no tiene amenazas.

## 2. ¿Qué puede salir mal? (20 min)

Recorran **cada elemento** con STRIDE y registren las amenazas en Threat Dragon (panel *Threats* → *New Threat*):

| Letra | Pregunta | Ejemplo típico |
|---|---|---|
| **S** Suplantación | ¿Alguien puede hacerse pasar por otro usuario o servicio? | Token sin expiración, webhook sin firma |
| **T** Manipulación | ¿Alguien puede alterar datos en tránsito, en reposo o en la lógica? | Precio enviado por el cliente, inyección SQL |
| **R** Repudio | ¿Alguien puede negar que hizo algo? | Sin registro de quién aprobó un pago |
| **I** Divulgación | ¿Se puede leer algo que no debería? | IDOR, traza de errores, CORS abierto |
| **D** Denegación | ¿Se puede tumbar o agotar el servicio? | Sin límite de solicitudes, consultas sin paginar |
| **E** Elevación | ¿Alguien puede hacer más de lo que le corresponde? | Inyección de comandos, rol en un campo editable |

**Mínimo:** 10 amenazas, al menos una de cada letra, y **al menos una de lógica de negocio** que ninguna herramienta automática encontraría (como el cupón reutilizable de la tienda).

## 3. ¿Qué vamos a hacer al respecto? (15 min)

1. Califiquen cada amenaza: **impacto** (1–3) × **probabilidad** (1–3) = riesgo (1–9). En Threat Dragon usen *Severity*: 7–9 → High, 4–6 → Medium, 1–3 → Low.
2. Elijan las **5 de mayor riesgo** y para cada una escriban un **requisito verificable** con su capítulo de ASVS 5.0:

| ID | Amenaza | STRIDE | I × P | Requisito de seguridad (verificable) | ASVS 5.0 | Cómo lo verificamos |
|---|---|---|---|---|---|---|
| T1 | | | | | V_ | prueba / revisión / herramienta |

Un requisito verificable dice **qué** debe cumplir el sistema y se puede probar: «Toda consulta a `pedidos` filtra por el usuario autenticado; un pedido ajeno responde 404» sí lo es. «Mejorar la seguridad del acceso» no.

Capítulos de ASVS 5.0 más usados: V1 codificación y sanitización · V2 validación y lógica de negocio · V3 seguridad del frontend web · V4 APIs · V5 archivos · V6 autenticación · V7 sesiones · V8 autorización · V9 tokens autocontenidos · V11 criptografía · V12 comunicación segura · V13 configuración · V14 protección de datos · V16 registro y manejo de errores.

## 4. ¿Hicimos un buen trabajo? (5 min)

Respondan en dos líneas: ¿qué parte del sistema quedó **fuera** del modelo y por qué? ¿Qué amenaza les sorprendió?

## Entrega

En el repositorio de su equipo, carpeta `seguridad/lab1/`:

1. `modelo.json`: el modelo exportado de Threat Dragon (*Save* lo descarga).
2. `informe.pdf`: botón *Report* → imprimir a PDF.
3. `LAB1.md`: la tabla de la sección 3 y las respuestas de la sección 4.

Comenten el enlace a la carpeta en el issue de su equipo. Estas tablas son la sección 2 del [proyecto integrador](../proyecto/PLANTILLA.md): no es trabajo extra, es el entregable 1 adelantado.

## Rúbrica (7,5 %)

| Criterio | Peso | Sobresaliente | Aceptable | Insuficiente |
|---|---|---|---|---|
| DFD y límites de confianza | 25 % | Todos los flujos del alcance, con protocolo; límites en cada cambio de confianza | Flujos principales; algún límite faltante | Sin límites o sin flujos |
| Cobertura STRIDE | 25 % | ≥ 10 amenazas, las 6 letras, ligadas a elementos concretos | 6–9 amenazas o faltan letras | < 6 o genéricas («hackers») |
| Lógica de negocio | 10 % | Al menos una amenaza propia del dominio, bien explicada | Mencionada sin explicar | Ausente |
| Priorización | 20 % | I × P justificado; top 5 coherente | Priorización sin justificar | Sin priorizar |
| Requisitos ASVS | 20 % | 5 requisitos verificables, con capítulo y forma de verificación | Requisitos vagos o sin capítulo | Sin requisitos |

Los laboratorios entregados después de la sesión se reciben hasta la sesión siguiente con una penalización del 20 %.
