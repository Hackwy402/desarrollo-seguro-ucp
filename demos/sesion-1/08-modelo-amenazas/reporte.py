#!/usr/bin/env python3
"""Resumen en español de las amenazas que pytm encuentra en modelo.py, agrupadas y priorizadas."""
import sys
from collections import Counter

sys.argv = [sys.argv[0]]
from modelo import tm  # noqa: E402

tm.resolve()
hallazgos = tm.findings

print(f"\npytm generó {len(hallazgos)} amenazas candidatas a partir de la biblioteca CAPEC.\n")
print("Por elemento:")
for elemento, n in Counter(str(h.target) for h in hallazgos).most_common():
    print(f"  {n:>3}  {elemento}")
print("\nPor severidad:")
for sev, n in Counter(h.severity for h in hallazgos).most_common():
    print(f"  {n:>3}  {sev}")

# Priorización humana: las que corresponden a lo que vimos en la demo 3.
RELEVANTES = {
    ("API de facturas", "AC01"): ("E", "Abuso de privilegios: leer facturas ajenas (demo 3A, mediación completa)"),
    ("API de facturas", "AC07"): ("E", "Control de acceso mal configurado (demo 3A)"),
    ("API de facturas", "AA01"): ("S", "Evasión de autenticación: tokens estáticos sin expiración"),
    ("API de facturas", "AC17"): ("S", "Secuestro de sesión: el token viaja sin cifrar"),
    ("API de facturas", "INP18"): ("I", "Mapeo de la app a partir de errores (demo 3C, traza de depuración)"),
    ("API de facturas", "DO01"): ("D", "Inundación de peticiones: sin límite de tasa"),
    ("Datos de facturas", "DE04"): ("R", "Manipulación del registro de auditoría: nadie sabe quién hizo qué"),
    ("GET /facturas/{id} con token", "DE01"): ("I", "Intercepción: HTTP sin TLS entre navegador y API"),
    ("Servicio de permisos", "AC12"): ("E", "Escalada de privilegios a través del servicio de permisos"),
}

print("\nPriorizadas por el equipo (STRIDE):")
print(f"  {'':1} {'Elemento':<30} {'ID':<6} {'Severidad':<10} Amenaza")
vistos = set()
for h in hallazgos:
    clave = (str(h.target), h.threat_id)
    if clave in RELEVANTES and clave not in vistos:
        vistos.add(clave)
        letra, texto = RELEVANTES[clave]
        print(f"  {letra} {str(h.target):<30} {h.threat_id:<6} {h.severity:<10} {texto}")

print("\nLo que pytm NO encontró, y sí encontramos en la demo 3:")
print("  E  La falla abierta del servicio de permisos (demo 3B): es lógica de la aplicación, no un atributo del diagrama.")
print("\nLección: la herramienta propone candidatos; el equipo filtra, prioriza y agrega lo que solo conoce quien entiende el negocio.\n")
