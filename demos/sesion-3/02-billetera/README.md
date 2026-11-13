# Billetera UCP · katas de autenticación, APIs y criptografía

Una API de billetera digital (Flask + SQLite + JWT) con una falla real en cada control de la sesión 3. Igual que la Tienda UCP: primero la demo del docente (`demo-billetera.sh`), después ustedes construyen el control en `app.py` hasta que las pruebas pasen.

## Katas

```bash
bash demos/sesion-3/02-billetera/katas.sh               # las 35 pruebas
bash demos/sesion-3/02-billetera/katas.sh v9_jwt        # solo una kata
```

Las pruebas corren en un contenedor **sin red** y con el código en solo lectura. Al empezar fallan 24 de 35.

| Kata | Control | Dónde | Pista | ASVS 5.0 |
|---|---|---|---|---|
| `v6_claves` | Almacenamiento de contraseñas | `hashear`, `verificar_clave`, `registro` | `argon2.PasswordHasher()`. Mínimo 12 caracteres, sin exigir símbolos, y fuera de `claves_comunes.txt`. | V6 · V11 |
| `v6_fuerza` | Fuerza bruta y enumeración | `login` | Mismo 401 y mismo mensaje exista o no el usuario. Un contador de fallos por usuario: al quinto, 429. Un acierto lo reinicia. | V6 |
| `v9_jwt` | Tokens JWT | `JWT_SECRETO`, `emitir_token`, `usuario_actual` | `jwt.decode(token, secreto, algorithms=["HS256"], audience=…, issuer=…)`. Defina `JWT_EMISOR` y `JWT_AUDIENCIA`. `exp` a 15 min. Secreto de 32+ bytes desde el entorno. | V9 |
| `api1_bola` | Autorización por objeto | `movimientos` | Igual que el A01 de la tienda: el dueño va en la consulta. Cuenta ajena o inexistente → 404. | V8 |
| `api3_propiedades` | Autorización por propiedad | `ver_perfil`, `editar_perfil` | Lista blanca de lectura (sin `hash_clave`, documento enmascarado) y de escritura (`nombre`, `correo`). Campo extra → 400. | V8 · V4 |
| `api4_recursos` | Consumo de recursos | `movimientos` | `limite` entero entre 1 y 100. Texto → 400, no 500. | V4 · V2 |
| `v11_cripto` | Cifrado de datos en reposo | `cifrar`, `descifrar`, `LLAVE_DATOS` | `AESGCM` con nonce aleatorio de 12 bytes antepuesto al cifrado y el usuario como dato asociado. Llave de 32 bytes desde el entorno. | V11 |

Orden sugerido: `api1_bola` → `api3_propiedades` → `api4_recursos` → `v6_claves` → `v6_fuerza` → `v9_jwt` → `v11_cripto`.

Las tres primeras son de autorización, como las de ayer. Las cuatro últimas son de autenticación y criptografía: casi todo lo resuelve una librería madura bien configurada; el error típico no es el algoritmo, es la configuración.

### Reglas

- **No borren funcionalidad**: el login, el registro con una frase larga, editar el nombre y paginar con `limite=50` también se prueban.
- **No toquen `tests/`.**
- **No inventen criptografía.** Todo lo que necesitan está en `argon2-cffi`, `pyjwt` y `cryptography`, ya instaladas en la imagen.

## Probar a mano

```bash
cd demos/sesion-3/02-billetera
docker compose up -d insegura                       # http://127.0.0.1:5005
curl -s -X POST http://127.0.0.1:5005/api/login -H 'Content-Type: application/json' \
     -d '{"usuario":"ana","clave":"Cafetal-de-Risaralda-2026"}'
docker compose down
```

Usuarios: `ana` / `Cafetal-de-Risaralda-2026` y `beto` / `Nevado-del-Ruiz-5321m`. Son claves de laboratorio, no las reutilicen.
