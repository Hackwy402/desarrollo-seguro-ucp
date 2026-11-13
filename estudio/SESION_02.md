# Estudio independiente – Sesión 2

Plazo: antes del viernes 20 de noviembre, 5:00 p. m. (la sesión 3 es al día siguiente, sábado 14: para ella solo traigan las katas como hayan quedado).
Carga estimada: 14 horas (parte de las 64 h de trabajo independiente del curso).

El objetivo es pasar de «corregí siete fallas en una tienda de juguete» a «sé encontrar y corregir esas fallas en el código de mi equipo».

## 1. Lecturas y actividades

| # | Actividad | Horas | Para qué |
|---|---|---|---|
| 1 | Terminar las 7 katas de la Tienda UCP hasta tener 27 pruebas en verde (`bash demos/sesion-2/02-tienda/katas.sh`). | 2 | Cada control queda probado, no supuesto. |
| 2 | OWASP Cheat Sheets: [Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html), [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html), [Cross Site Scripting Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) y [OS Command Injection Defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html). | 3 | La versión completa de lo que hicimos en A05, para su lenguaje y framework. |
| 3 | OWASP Top 10:2025: releer A01, A02, A05, A06 y A10, ahora con la tienda en la cabeza. Anoten un CWE de cada una que exista en su proyecto o en uno que conozcan. | 2 | Pasar del catálogo a su código. |
| 4 | [OWASP ASVS 5.0](https://github.com/OWASP/ASVS/tree/master/5.0/en): capítulos V1, V2, V8 y V16, solo los requisitos de nivel 1. | 2 | De ahí salen los requisitos verificables del Lab 1 y del proyecto. |
| 5 | Aplicar al proyecto: buscar en el código de su aplicación una instancia de cada patrón de la tienda (consulta concatenada, salida sin escapar, `shell=True` o equivalente, precio o rol que viene del cliente, `except` que deja pasar). Registrar lo que encuentren en la sección 3 de la [plantilla del proyecto](../proyecto/PLANTILLA.md). | 4 | Es la base del Lab 2 (sábado 14) y del entregable 1. |
| 6 | Mejorar el modelo del Lab 1 con los comentarios de la revisión cruzada. | 1 | Entregable 1 del proyecto (20 de noviembre). |
| | **Total** | **14** | |

## 2. Preguntas de autoevaluación

1. ¿Por qué una consulta parametrizada previene la inyección SQL y escapar comillas a mano no es suficiente?
2. En la kata de XSS, ¿qué hace el escape de plantillas y qué hace la CSP? Si solo pudieran tener uno, ¿cuál y por qué? ¿Por qué conviene tener los dos?
3. ¿Qué tienen en común la inyección SQL, el XSS y la inyección de comandos? Enuncien el principio en una frase.
4. ¿Por qué el precio enviado por el cliente es una falla de **diseño** (A06) y no de validación de entradas? ¿Qué pregunta del modelado de amenazas la habría encontrado?
5. El cupón se marca como usado con un `UPDATE ... WHERE usado = 0` y se revisa `rowcount`. ¿Qué problema resolvería esto que un `SELECT` seguido de un `UPDATE` no resuelve?
6. Den un ejemplo de su trabajo de un `try/except` que falla abierto. ¿Cómo lo reescribirían para fallar cerrado sin perjudicar al usuario?
7. ¿Por qué reflejar el encabezado `Origin` con `Access-Control-Allow-Credentials: true` es peor que `Access-Control-Allow-Origin: *`?
8. Un pedido ajeno, ¿debe responder 403 o 404? Argumenten.
9. En el modelo de la tienda quedaron amenazas sin kata (repudio, denegación de servicio, datos en reposo). ¿Qué control propondrían para cada una y cómo lo verificarían?
10. ¿Qué amenaza de lógica de negocio encontraron en su aplicación que ninguna herramienta automática detectaría?

## 3. Referencias

- Threat Modeling Manifesto: <https://www.threatmodelingmanifesto.org/>
- OWASP Threat Dragon: <https://www.threatdragon.com/docs/>
- Shostack, A. (2014). *Threat Modeling: Designing for Security*. Wiley. Capítulos 1–3 (STRIDE y DFD).
- OWASP Top 10:2025: <https://owasp.org/Top10/2025/>
- OWASP Cheat Sheet Series: <https://cheatsheetseries.owasp.org/>
