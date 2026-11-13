# Desarrollo Seguro de Software – UCP

Optativa I – Ciberseguridad Aplicada al Desarrollo de Software
Especialización en Desarrollo de Software · Universidad Católica de Pereira · Cohorte 2026-2
Docente: Ing. Jawy Andrés Romero ([@Hackwy402](https://github.com/Hackwy402))

El curso trata los principios de seguridad y el ciclo de vida de desarrollo seguro (SSDLC), teórico y aplicado: diseñar, construir y verificar software seguro. La parte ofensiva aparece solo como medio para entender el control.

## Programación

| Sesión | Fecha | Modalidad | Horario | Tema |
|---|---|---|---|---|
| 1 | Sáb. 7 nov. | Virtual | 8:00–12:00 y 2:00–4:00 p. m. | Principios, SSDLC y preparación del entorno |
| 2 | Vie. 13 nov. | Presencial | 5:00–10:00 p. m. | Modelado de amenazas y codificación segura |
| 3 | Sáb. 14 nov. | Presencial | 8:00 a. m.–5:00 p. m. | Autenticación, APIs, criptografía y ASVS |
| 4 | Vie. 20 nov. | Presencial | 5:00–10:00 p. m. | Cadena de suministro y DevSecOps |
| 5 | Sáb. 21 nov. | Presencial | 8:00 a. m.–5:00 p. m. | IA segura, gobernanza y sustentación |

## Estructura

```
setup/        guía de instalación y script de verificación del entorno
lab-env/      aplicaciones de práctica (docker compose, solo 127.0.0.1)
demos/        demos en vivo, reproducibles, organizadas por sesión
  sesion-1/   las 8 demos de la sesión 1 (ver demos/sesion-1/README.md)
  sesion-2/   modelo de amenazas en Threat Dragon y katas de codificación segura (Tienda UCP)
  sesion-3/   Semgrep con reglas propias
  sesion-4/   cadena de suministro y pipeline en GitHub
docs/         diagramas de arquitectura y de flujo (Graphviz) y pantallazos
datos/        panorama: CVE (NVD), vulnerabilidades explotadas (CISA KEV), gráficos y fuentes
deck/         fuentes de los decks (sesión 1; sesión 2 en deck/sesion-2)
estudio/      guías de estudio independiente por sesión
labs/         laboratorios, se publican antes de cada sesión
proyecto/     plantilla del proyecto integrador
```

## Primeros pasos (sesión 1, tarde)

1. Seguir [setup/GUIA_INSTALACION.md](setup/GUIA_INSTALACION.md).
2. Ejecutar `bash setup/check-env.sh` dentro de la VM y guardar la salida.
3. Levantar el entorno de práctica: `docker compose -f lab-env/docker-compose.yml up -d`.
4. Abrir un issue con la plantilla **Equipo y aplicación** para registrar su equipo.
5. Antes del 13 de noviembre: [estudio/SESION_01.md](estudio/SESION_01.md) (16 h de estudio independiente).

## Reglas del laboratorio

- Solo se prueba contra las aplicaciones de `lab-env/` o contra sistemas propios con autorización escrita.
- Las aplicaciones vulnerables corren dentro de la VM y escuchan solo en `127.0.0.1`.
- Ningún secreto real (tokens, contraseñas, llaves) se sube a un repositorio.
- Probar sistemas de terceros sin autorización es delito (Ley 1273 de 2009) y falta grave.
