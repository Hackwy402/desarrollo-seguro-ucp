# Sesión 2 · Viernes 13 de noviembre · 6:00–10:00 p. m. (presencial)

**Modelado de amenazas aplicado y codificación segura frente al OWASP Top 10:2025.**
Un solo sistema de punta a punta: la Tienda UCP se **modela** en Threat Dragon (demo 1) y luego se **corrige** en código (demo 2 y katas). Cada amenaza del modelo termina en una prueba automática que verifica su control.

## Antes de la clase

```bash
docker pull owasp/threat-dragon:stable
docker build -q -t ucp-tienda demos/sesion-2/02-tienda
bash demos/sesion-2/02-tienda/katas.sh | tail -1                                    # 21 failed, 6 passed
APP_FILE=/app/.soluciones/app.py bash demos/sesion-2/02-tienda/katas.sh | tail -1   # 27 passed (solo docente)
```

`.soluciones/` no se publica en el repositorio: es la solución de referencia del docente. Se publica después de la sesión 3.

## Guion

| Hora | Bloque | Material | Lo que tienen que ver o producir |
|---|---|---|---|
| 6:00 | Apertura: repaso de la sesión 1 y verificación del entorno | `docker pull` y `docker build` de arriba | Todos con Threat Dragon y `ucp-tienda` listos |
| 6:15 | **Demo 1.** Modelo de amenazas de la Tienda UCP | [`01-modelo-amenazas`](01-modelo-amenazas/README.md) | Las cuatro preguntas; DFD con dos límites de confianza; 16 amenazas STRIDE con mitigación y capítulo ASVS |
| 6:40 | **Lab 1** por equipos sobre su aplicación | [`labs/LAB1.md`](../../labs/LAB1.md) | DFD, ≥ 10 amenazas STRIDE, top 5 con requisitos ASVS |
| 7:40 | Revisión cruzada: cada equipo busca 2 amenazas que le faltan al modelo de otro | — | Comentarios en el issue del otro equipo |
| 7:50 | Entrega del Lab 1 · pausa | — | Enlace en el issue del equipo |
| 8:00 | Principios de codificación segura | deck | Validar entradas, codificar salidas, parametrizar, el servidor decide, fallar cerrado, seguro por defecto |
| 8:10 | **Demo 2.** Falla → control en la Tienda UCP | `bash demos/sesion-2/02-tienda/demo-tienda.sh` | 7 fallas en vivo: insegura (:5003) contra segura (:5004) |
| 8:45 | **Katas** en parejas | [`02-tienda`](02-tienda/README.md) | Pasar de 21 pruebas en rojo a 27 en verde |
| 9:45 | Cierre: dos parejas muestran su solución; qué viene el sábado | deck | Autenticación, APIs, JWT/OAuth, criptografía |

## Qué categoría se ve dónde

| OWASP Top 10:2025 | Demo 1 (modelo) | Demo 2 (código) | Kata |
|---|---|---|---|
| A01 Control de acceso roto | IDOR en pedidos | (visto en la sesión 1) | `a01_acceso` |
| A02 Configuración insegura | CORS, traza de errores | CORS con credenciales | `a02_config` |
| A05 Inyección | SQL, XSS, comandos | Las tres en vivo | `a05_sql`, `a05_xss`, `a05_comandos` |
| A06 Diseño inseguro | Precio del cliente, cupón | Precio de 1 peso, cantidad negativa, cupón ×3 | `a06_diseno` |
| A10 Condiciones excepcionales | Falla abierta en la pasarela | Pasarela caída → pedido «pagado» | `a10_excepciones` |

## Notas de seguridad

- Threat Dragon y la tienda escuchan solo en `127.0.0.1`. Threat Dragon genera llaves aleatorias en cada arranque.
- La tienda corre con sistema de archivos de solo lectura, sin capacidades, `no-new-privileges` y límites de memoria y procesos; las katas, además, sin red.
- La inyección de comandos se ejecuta dentro del contenedor desechable como `uid=10001`: así se ve el impacto sin arriesgar la VM.
