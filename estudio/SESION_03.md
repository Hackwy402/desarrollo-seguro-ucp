# Estudio independiente – Sesión 3

Plazo: antes de la sesión 4 (viernes 20 de noviembre).
Carga estimada: 14 horas (parte de las 64 h de trabajo independiente del curso).

El objetivo es que la tabla ASVS del Lab 2 deje de tener «No cumple» en autenticación, autorización y tokens, y que cada control quede con su prueba.

## 1. Lecturas y actividades

| # | Actividad | Horas | Para qué |
|---|---|---|---|
| 1 | Terminar las 7 katas de la Billetera UCP hasta tener 35 pruebas en verde (`bash demos/sesion-3/02-billetera/katas.sh`). | 2 | Cada control de la sesión, probado. |
| 2 | OWASP Cheat Sheets: [Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), [Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) y [JSON Web Token for Java](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html) (los conceptos aplican a cualquier lenguaje). | 3 | La versión completa de V6, V7 y V9 para su stack. |
| 3 | [OWASP API Security Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/): API1 a API5 completas, el resto en resumen. Identifiquen cuál aplica a su proyecto. | 2 | BOLA y asignación masiva son las fallas más comunes en APIs reales. |
| 4 | NIST SP 800-63B, secciones de contraseñas (*memorized secrets*) y autenticadores. Y la guía de [passkeys](https://passkeys.dev/docs/intro/what-are-passkeys/). | 1 | De dónde salen los 12 caracteres sin reglas de composición, y hacia dónde va la autenticación. |
| 5 | [Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html) y [Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html). | 1 | Cifrado autenticado, rotación de llaves y por qué un secreto en git es para siempre. |
| 6 | Terminar el Lab 2: cerrar al menos **tres** «No cumple» de V6, V8 o V9 en su proyecto, cada uno con su prueba y su pull request. | 4 | Sección 3 del proyecto integrador. |
| 7 | Entregable 1 del proyecto (secciones 1 a 3 de la plantilla), con el modelo mejorado del Lab 1 y la tabla ASVS del Lab 2. | 1 | Se entrega el 20 de noviembre. |
| | **Total** | **14** | |

## 2. Preguntas de autoevaluación

1. ¿Por qué MD5 o SHA-256 no sirven para contraseñas, si son funciones hash criptográficas? ¿Qué agrega Argon2id que ellas no tienen?
2. La sal no es secreta. Entonces, ¿qué protege?
3. ¿Por qué NIST y ASVS desaconsejan exigir mayúsculas, números y símbolos, y obligar a cambiar la clave cada 90 días?
4. En la kata de fuerza bruta, ¿qué ataque deja pasar un bloqueo por usuario? (Pista: muchas cuentas, una clave común cada una.) ¿Cómo lo mitigarían?
5. Un JWT no está cifrado. ¿Qué garantiza la firma y qué no garantiza? ¿Qué datos nunca deben ir en un JWT?
6. ¿Por qué `algorithms=["HS256"]` es obligatorio aunque «ya sabemos» que firmamos con HS256? Investiguen la confusión de algoritmos RS256/HS256.
7. Un JWT de 15 minutos no se puede revocar antes de que expire. ¿Cómo resolverían el cierre de sesión? Comparen con una sesión en el servidor.
8. ¿En qué se diferencian BOLA (API1) y BOPLA (API3)? Den un ejemplo de cada uno en su proyecto.
9. ¿Por qué AES-GCM detecta la manipulación y AES-ECB no? ¿Qué pasa si se repite un nonce con la misma llave en GCM?
10. En la demo, ZAP no encontró BOLA ni el token sin firma. ¿Qué tipo de prueba sí los encuentra, y en qué etapa del pipeline la pondrían el 20 de noviembre?

## 3. Referencias

- OWASP ASVS 5.0: <https://github.com/OWASP/ASVS/tree/master/5.0/en>
- OWASP API Security Top 10:2023: <https://owasp.org/API-Security/>
- OWASP Cheat Sheet Series: <https://cheatsheetseries.owasp.org/>
- NIST SP 800-63B, *Digital Identity Guidelines: Authentication*: <https://pages.nist.gov/800-63-4/sp800-63b.html>
- RFC 8725, *JSON Web Token Best Current Practices*: <https://www.rfc-editor.org/rfc/rfc8725>
- RFC 9700, *Best Current Practice for OAuth 2.0 Security*: <https://www.rfc-editor.org/rfc/rfc9700>
- RFC 9106, *Argon2*: <https://www.rfc-editor.org/rfc/rfc9106>
