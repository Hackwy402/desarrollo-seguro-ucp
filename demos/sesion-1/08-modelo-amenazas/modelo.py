#!/usr/bin/env python3
"""Modelo de amenazas de la API de facturas (demo 3) como código, con OWASP pytm.

Uso dentro del contenedor:
  python modelo.py --dfd | dot -Tpng -Gdpi=200 -o dfd.png   # diagrama de flujo de datos
  python reporte.py                                          # amenazas encontradas, en español
"""
from pytm import TM, Actor, Boundary, Classification, Data, Dataflow, Datastore, Process, Server

tm = TM("API de facturas")
tm.description = "API de facturas de la demo 3 de la sesión 1: versión insegura antes de aplicar controles."
tm.isOrdered = True
tm.mergeResponses = True

# Límites de confianza
internet = Boundary("Internet")
servidor = Boundary("Red del servidor")

# Datos que viajan
token = Data("Token de sesión", classification=Classification.SECRET)
factura = Data("Factura (cliente y total)", classification=Classification.SENSITIVE)
rol = Data("Rol del usuario", classification=Classification.RESTRICTED)

# Elementos
usuario = Actor("Navegador")
usuario.inBoundary = internet

api = Server("API de facturas")
api.inBoundary = servidor
api.OS = "Linux (contenedor)"
api.controls.isHardened = False            # corre como root, depuración activa
api.controls.sanitizesInput = False
api.controls.encodesOutput = True
api.controls.authorizesSource = False      # no verifica que la factura sea del usuario
api.controls.implementsAuthenticationScheme = True
api.controls.hasAccessControl = False
api.controls.implementsPOLP = False
api.controls.handlesResourceConsumption = False

permisos = Process("Servicio de permisos")
permisos.inBoundary = servidor
permisos.controls.implementsAuthenticationScheme = False

datos = Datastore("Datos de facturas")
datos.inBoundary = servidor
datos.controls.isEncryptedAtRest = False
datos.controls.hasAccessControl = False
datos.storesSensitiveData = True

# Flujos
f1 = Dataflow(usuario, api, "GET /facturas/{id} con token")
f1.protocol = "HTTP"
f1.dstPort = 5000
f1.data = [token]
f1.controls.isEncrypted = False

f2 = Dataflow(api, permisos, "Consulta de rol")
f2.protocol = "HTTP"
f2.dstPort = 8000
f2.data = [rol]
f2.controls.isEncrypted = False

f3 = Dataflow(api, datos, "Lectura de factura")
f3.data = [factura]

f4 = Dataflow(api, usuario, "Respuesta con la factura")
f4.protocol = "HTTP"
f4.data = [factura]
f4.controls.isEncrypted = False

if __name__ == "__main__":
    tm.process()
