# Demos de la sesión 3 (sábado 14 de noviembre)

Autenticación, APIs y criptografía aplicada, verificadas con ASVS 5.0. Todo corre en `127.0.0.1`.

| Demo | Script | Qué muestra |
|---|---|---|
| Billetera UCP, falla contra control | `bash demos/sesion-3/02-billetera/demo-billetera.sh` | JWT sin firma (`alg: none`), enumeración y fuerza bruta en el login, MD5 contra Argon2id, BOLA, consumo sin límite, asignación masiva y AES-ECB contra AES-GCM. Insegura en `:5005`, segura en `:5006` |
| Katas de la billetera | `bash demos/sesion-3/02-billetera/katas.sh` | 7 katas y 35 pruebas: al empezar fallan 24 |
| Semgrep con reglas propias | `bash demos/sesion-3/01-semgrep/demo-semgrep.sh` | Reglas del equipo para la API de la sesión 1 y para la billetera (`reglas-billetera.yml`): 8 hallazgos en la insegura y 0 en la segura |
| Escaneo dinámico de la API | `bash demos/sesion-3/02-billetera/zap/zap-api.sh insegura` | OWASP ZAP con la especificación OpenAPI y un token de Ana. Encuentra cabeceras faltantes y un error 500, **no** encuentra BOLA, `alg: none` ni asignación masiva: por eso existen las pruebas de autorización |

Antes de la sesión, en la VM (descargas grandes):

```bash
docker build -t ucp-billetera demos/sesion-3/02-billetera
docker pull ghcr.io/zaproxy/zaproxy:stable        # ~1,2 GB
docker pull semgrep/semgrep                       # o: pipx install semgrep
```
