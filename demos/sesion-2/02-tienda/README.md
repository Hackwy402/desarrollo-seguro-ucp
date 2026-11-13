# Tienda UCP · katas de codificación segura (OWASP Top 10:2025)

Una API de tienda en línea (Flask + SQLite) con **una falla real por categoría**. La trabajamos en dos tiempos:

1. **Demo del docente** (`demo-tienda.sh`): cada falla en vivo contra su control.
2. **Katas en parejas** (`katas.sh`): ustedes construyen el control en `app.py` hasta que las pruebas pasen.

## Katas

```bash
bash demos/sesion-2/02-tienda/katas.sh               # las 27 pruebas
bash demos/sesion-2/02-tienda/katas.sh a05_sql       # solo una kata
```

Las pruebas corren en un contenedor **sin red** y con el código montado en solo lectura. Al principio fallan 21 de 27: esa es la meta.

| Kata | Categoría | Dónde está la falla | Pista |
|---|---|---|---|
| `a01_acceso` | A01 Control de acceso roto | `ver_pedido` | El dueño va en la consulta. Ajeno → 404, no 403. |
| `a05_sql` | A05 Inyección (SQL) | `buscar_productos` | `?` y una tupla de parámetros. El `%` va en el parámetro. |
| `a05_xss` | A05 Inyección (XSS) | `ver_resenas` | `render_template_string` escapa `{{ }}`. Y una CSP como segunda capa. |
| `a05_comandos` | A05 Inyección (comandos) | `generar_reporte` | Lista blanca del nombre y `tarfile`, sin `shell=True`. |
| `a06_diseno` | A06 Diseño inseguro | `checkout` | El servidor es la fuente de verdad: precio, cantidad, cupón. |
| `a10_excepciones` | A10 Condiciones excepcionales | `checkout` (pasarela) | Si no sabe si cobró, no entregue: 503. Y un manejador de errores genérico. |
| `a02_config` | A02 Configuración insegura | `cabeceras` y `__main__` | Lista blanca de orígenes CORS, `nosniff`, CSP y debug apagado por defecto. |

Orden sugerido: `a01` → `a05_sql` → `a05_xss` → `a06` → `a10` → `a05_comandos` → `a02`.

### Reglas

- **No borren funcionalidad.** Las pruebas también verifican que la tienda siga funcionando (buscar «D'Origen», comprar con cupón válido, generar `ventas-noviembre`).
- **No toquen `tests/`.** Si una prueba les parece injusta, discútanlo con el docente.
- Cada control que construyan es un requisito de su proyecto: anoten el capítulo de ASVS 5.0 que cumple.

## Probar a mano

```bash
cd demos/sesion-2/02-tienda
docker compose up -d insegura                       # http://127.0.0.1:5003
curl -s "http://127.0.0.1:5003/productos?q=Teclado"
curl -s http://127.0.0.1:5003/pedidos/1 -H "Authorization: Bearer token-ana"
docker compose down
```

Usuarios: `token-ana` y `token-beto`. Todo corre en `127.0.0.1`, con el sistema de archivos en solo lectura, sin capacidades y con límites de memoria y procesos.
