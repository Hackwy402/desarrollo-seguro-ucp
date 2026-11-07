# Demo 7: autoevaluación OWASP SAMM en vivo

Duración: 20 minutos. Herramienta: [OWASP SAMM Assessment](https://owaspsamm.org/assessment/) (hoja oficial de autoevaluación; también existe la versión en hoja de cálculo en el mismo sitio).

## Objetivo

Que vean el SSDF «en una organización real»: no como lista de buenas intenciones, sino como un nivel de madurez que se mide y se mejora.

## Guion

1. Elegir con el grupo una organización de referencia: la empresa de un voluntario (sin nombrarla) o una ficticia, «Facturas S.A.S.», que desarrolla la API de la demo 3.
2. Proyectar la autoevaluación y responder en vivo, con votación rápida en el chat, **una práctica por cada función de negocio**:

   | Función | Práctica | Pregunta para el grupo |
   |---|---|---|
   | Gobierno | Educación y orientación | ¿Los desarrolladores reciben formación en seguridad al menos una vez al año? |
   | Diseño | Evaluación de amenazas | ¿Se hace un modelo de amenazas antes de construir una funcionalidad nueva? |
   | Implementación | Build seguro | ¿El build corre en un servidor de CI, con dependencias fijadas, o en el equipo de alguien? |
   | Verificación | Pruebas de seguridad | ¿Hay pruebas automáticas de seguridad en cada cambio? |
   | Operaciones | Gestión de incidentes | ¿Existe un procedimiento escrito para responder a una vulnerabilidad reportada? |

3. Mostrar el puntaje resultante y discutir: ¿dónde está el riesgo más grande? ¿qué mejora en tres meses tiene más impacto?
4. Conectar con el curso: cada sesión presencial sube el nivel de una de estas prácticas en el proyecto integrador.

## Tarea derivada

La autoevaluación completa sobre su propia organización está en la guía de estudio (`estudio/SESION_01.md`, actividad 5).
