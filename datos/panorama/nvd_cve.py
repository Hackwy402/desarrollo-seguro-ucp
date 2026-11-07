#!/usr/bin/env python3
"""Cuenta CVE publicados en el NVD (NIST) por año y, para un año dado, por CWE.

Fuente: API pública NVD 2.0 (https://services.nvd.nist.gov/rest/json/cves/2.0).
Sin llave la API permite 5 consultas cada 30 s, por eso el script espera entre consultas.
La API admite rangos de fechas de máximo 120 días: cada año se consulta por trimestres.
Se excluyen los CVE rechazados (noRejected).

Uso:
  python3 nvd_cve.py anios 1999 2026  > cve_por_anio.csv
  python3 nvd_cve.py cwe 2025         > cwe_2025.csv
"""
import csv
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
PAUSA = 6.5
HOY = dt.date.today()

CWES = {
    "CWE-79": "Cross-site scripting (XSS)",
    "CWE-89": "Inyección SQL",
    "CWE-862": "Falta de autorización",
    "CWE-787": "Escritura fuera de límites",
    "CWE-22": "Path traversal",
    "CWE-352": "CSRF",
    "CWE-125": "Lectura fuera de límites",
    "CWE-78": "Inyección de comandos del SO",
    "CWE-416": "Uso después de liberar",
    "CWE-434": "Carga de archivos peligrosos",
    "CWE-94": "Inyección de código",
    "CWE-20": "Validación de entrada incorrecta",
    "CWE-287": "Autenticación incorrecta",
    "CWE-639": "IDOR: autorización por clave controlada por el usuario",
    "CWE-200": "Exposición de información sensible",
    "CWE-502": "Deserialización insegura",
    "CWE-918": "SSRF",
    "CWE-798": "Credenciales embebidas",
}


def trimestres(anio):
    fin_anio = min(dt.date(anio, 12, 31), HOY)
    for mes in (1, 4, 7, 10):
        ini = dt.date(anio, mes, 1)
        if ini > fin_anio:
            break
        fin = (dt.date(anio + (mes == 10), (mes + 3 - 1) % 12 + 1, 1) - dt.timedelta(days=1))
        yield ini, min(fin, fin_anio)


def total(ini, fin, **extra):
    params = {
        "pubStartDate": f"{ini.isoformat()}T00:00:00.000",
        "pubEndDate": f"{fin.isoformat()}T23:59:59.999",
        "resultsPerPage": 1,
        **extra,
    }
    url = API + "?" + urllib.parse.urlencode(params) + "&noRejected"
    for intento in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ucp-desarrollo-seguro/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                n = json.load(r)["totalResults"]
            time.sleep(PAUSA)
            return n
        except Exception as e:  # 403/503 por límite de tasa: esperar y reintentar
            print(f"# reintento {intento + 1}: {e}", file=sys.stderr)
            time.sleep(30)
    raise SystemExit(f"No se pudo consultar {url}")


def por_anio(desde, hasta):
    w = csv.writer(sys.stdout)
    w.writerow(["anio", "cve_publicados", "anio_completo"])
    for anio in range(desde, hasta + 1):
        n = sum(total(i, f) for i, f in trimestres(anio))
        w.writerow([anio, n, "no" if anio == HOY.year else "si"])
        sys.stdout.flush()
        print(f"# {anio}: {n}", file=sys.stderr)


def por_cwe(anio):
    w = csv.writer(sys.stdout)
    w.writerow(["cwe", "nombre", "cve_publicados", "anio"])
    for cwe, nombre in CWES.items():
        n = sum(total(i, f, cweId=cwe) for i, f in trimestres(anio))
        w.writerow([cwe, nombre, n, anio])
        sys.stdout.flush()
        print(f"# {cwe}: {n}", file=sys.stderr)


if __name__ == "__main__":
    if sys.argv[1] == "anios":
        por_anio(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "cwe":
        por_cwe(int(sys.argv[2]))
