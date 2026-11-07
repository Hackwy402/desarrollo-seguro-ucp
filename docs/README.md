# Diagramas y pantallazos de la sesión 1

Todos los diagramas son código Graphviz (`diagramas/*.dot`) y se regeneran con:

```bash
bash docs/diagramas/render.sh     # PNG a 200 dpi en diagramas/png, SVG en diagramas/svg
```

## Arquitectura

### El laboratorio del curso
Cada estudiante trabaja en una VM Ubuntu con Docker. Las apps vulnerables escuchan solo en `127.0.0.1`. Demo 1.

![Arquitectura del laboratorio](diagramas/png/arquitectura-laboratorio.png)

### La API de facturas de las demos
Dos versiones de la misma API y un servicio de permisos, levantados con `demos/sesion-1/03-api/docker-compose.yml`. Demos 3 y 5.

![Arquitectura de la API](diagramas/png/arquitectura-api.png)

### Diagrama de flujo de datos generado con pytm
Generado desde `demos/sesion-1/08-modelo-amenazas/modelo.py`. Las líneas punteadas rojas son límites de confianza. Demo 8.

![DFD de la API](diagramas/png/dfd-api-pytm.png)

## Ciclo de vida de desarrollo seguro

Cada fase con su práctica del NIST SSDF y la sesión del curso donde se trabaja.

![SSDLC](diagramas/png/ssdlc.png)

## Principios, paso a paso

### Mediación completa (demo 3A)
![Flujo de mediación completa](diagramas/png/flujo-mediacion.png)

### Fallar de forma segura (demo 3B)
![Flujo de falla abierta contra falla segura](diagramas/png/flujo-falla-abierta.png)

### Mínimo privilegio en la base de datos (demo 4)
![Privilegios en PostgreSQL](diagramas/png/bd-privilegios.png)

### Defensa en profundidad (demo 5)
![Capas de defensa](diagramas/png/capas-defensa.png)

### Seguridad de memoria (demo 6)
![Desbordamiento en memoria](diagramas/png/memoria-desborde.png)

## Casos reales

### Log4Shell (2021) · cadena del incidente y controles
![Log4Shell](diagramas/png/caso-log4shell.png)

### xz utils (2024) · lo publicado no es lo revisado (demo 2)
![xz utils](diagramas/png/caso-xz.png)

### Shai-Hulud (2025) · un gusano en npm
![Shai-Hulud](diagramas/png/caso-shai-hulud.png)

## Pantallazos

| Archivo | Qué muestra |
|---|---|
| [`pantallazos/juice-shop.png`](pantallazos/juice-shop.png) | OWASP Juice Shop corriendo en `127.0.0.1:3000` dentro del laboratorio |
| [`pantallazos/api-insegura-error.png`](pantallazos/api-insegura-error.png) | La API insegura con `debug=True`: traza completa, rutas internas, versión de Python y consola de ejecución de código |
| [`pantallazos/api-segura-error.png`](pantallazos/api-segura-error.png) | La API segura ante el mismo error: mensaje genérico |
