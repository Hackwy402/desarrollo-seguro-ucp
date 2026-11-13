# Estudio independiente – Sesión 1

Plazo: antes del viernes 13 de noviembre, 6:00 p. m.
Carga estimada: 16 horas (parte de las 64 h de trabajo independiente del curso).

El objetivo es llegar a la sesión presencial con los conceptos claros y con el diagrama de su aplicación listo para modelar amenazas.

## 1. Lecturas y actividades

| # | Actividad | Horas | Para qué |
|---|---|---|---|
| 1 | [OWASP Top 10:2025](https://owasp.org/Top10/2025/): introducción y las 10 categorías. En cada una lean la descripción, cómo prevenirla y los CWE asociados. | 3 | Es la lista de controles que construiremos el 13 y 14 de noviembre. |
| 2 | [NIST SP 800-218 (SSDF)](https://csrc.nist.gov/pubs/sp/800/218/final): secciones 1 y 2 y la tabla completa de prácticas (PO, PS, PW, RV). | 3 | Es el marco de proceso de todo el curso. |
| 3 | [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/) y la documentación de [OWASP Threat Dragon](https://www.threatdragon.com/docs/). | 2 | Base del Laboratorio 1 del 13 de noviembre. |
| 4 | [CISA Secure by Design](https://www.cisa.gov/securebydesign) y las secciones I.A y I.B de [Saltzer y Schroeder (1975)](https://web.mit.edu/Saltzer/www/publications/protection/). | 2 | Los principios de diseño que vimos en clase, en su fuente. |
| 5 | Autoevaluación de [OWASP SAMM](https://owaspsamm.org/assessment/) aplicada a su equipo de trabajo actual (o a uno que conozcan). | 1,5 | Ver en qué nivel de madurez está una organización real. |
| 6 | [Ley 1581 de 2012](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981): principios del tratamiento (art. 4) y deberes del responsable (art. 17). | 1 | Obligaciones de privacidad que entran en el contexto del proyecto. |
| 7 | Preguntas de autoevaluación (sección 2) y diagrama de la aplicación (sección 3). | 3,5 | Preparación directa para el 13 de noviembre. |
| | **Total** | **16** | |

Opcional para profundizar: curso gratuito [Developing Secure Software (LFD121)](https://training.linuxfoundation.org/training/developing-secure-software-lfd121/) de OpenSSF.

## 2. Preguntas de autoevaluación

Respóndanlas por escrito, en sus palabras. No se entregan, pero el quiz del 21 de noviembre sale de aquí.

1. Den un ejemplo de su trabajo donde se haya violado cada una de estas propiedades: confidencialidad, integridad y disponibilidad.
2. ¿Qué diferencia hay entre autenticación y autorización? ¿Qué categoría del Top 10:2025 aparece cuando se confunden?
3. Expliquen con un ejemplo de código la diferencia entre «fallar de forma segura» y «fallar abierto».
4. ¿Qué significa mediación completa? ¿Por qué no basta con verificar el permiso al iniciar sesión?
5. En Log4Shell, ¿qué principio de diseño falló en la librería y qué práctica le faltó a las organizaciones afectadas para responder rápido?
6. En xz utils, el código malicioso no estaba en el repositorio visible sino en el tarball publicado. ¿Qué práctica del grupo PS del SSDF ayuda a detectar eso?
7. Nombren tres medidas que reducen el riesgo de un gusano como Shai-Hulud en su equipo de desarrollo.
8. ¿Qué diferencia hay entre el OWASP Top 10 y OWASP ASVS? ¿Para qué sirve cada uno en un proyecto?
9. ¿Qué nivel de ASVS exigirían para una app bancaria, para un blog institucional y para la app de su proyecto? Justifiquen.
10. Para cada letra de STRIDE, escriban la propiedad que viola y un control.
11. ¿Qué controles de ISO/IEC 27001:2022 tratan el desarrollo seguro? ¿Qué le pide cada uno al equipo?
12. Según la Ley 1581, ¿qué obligación tiene un desarrollador que diseña un formulario que recoge datos personales?

## 3. Preparación para el 13 de noviembre

Cada equipo trae el **diagrama de flujo de datos** de su aplicación:

- Actores externos (usuarios, sistemas de terceros).
- Procesos (frontend, API, servicios, tareas programadas).
- Almacenes de datos (bases de datos, colas, buckets, caché).
- Flujos de datos entre ellos, indicando qué datos viajan (credenciales, datos personales, pagos).
- Límites de confianza: dónde cambia el nivel de confianza (internet → API, API → base de datos, sistema → proveedor externo).

Puede ser una foto de un tablero, un diagrama en draw.io o directamente en Threat Dragon. Lo usaremos como punto de partida del Laboratorio 1.

## 4. Referencias de los casos vistos en clase

- Log4Shell: [CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)
- xz utils: [CVE-2024-3094](https://nvd.nist.gov/vuln/detail/CVE-2024-3094)
- Shai-Hulud: gusano en el ecosistema npm, septiembre de 2025. Busquen el análisis de un proveedor de seguridad y anoten: vector inicial, qué robaba y cómo se propagaba.
