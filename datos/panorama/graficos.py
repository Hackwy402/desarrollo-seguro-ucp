#!/usr/bin/env python3
"""Gráficos del panorama de la sesión 1, a partir de datos oficiales guardados en esta carpeta.

  cve_por_anio.csv  <- nvd_cve.py anios   (NVD, NIST)
  cwe_2025.csv      <- nvd_cve.py cwe     (NVD, NIST)
  kev.json          <- catálogo KEV de CISA
  paquetes.csv      <- cifras publicadas por Sonatype (ver fuentes.md)

Uso (en el contenedor): python graficos.py [todo|kev|cve|cwe|paquetes]
"""
import collections
import csv
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

# Tokens: tinta, superficie y paleta categórica validada (dataviz/validate_palette.js, modo claro)
TINTA, TINTA2, TENUE, REJILLA, SUPERFICIE = "#12202B", "#4A5560", "#8A8F94", "#E6E1D6", "#FFFDF8"
SERIE = "#2a78d6"
CATEGORICA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
OTROS = "#B8B4AA"

plt.rcParams.update({
    "font.family": "IBM Plex Sans", "font.size": 15, "text.color": TINTA,
    "axes.edgecolor": REJILLA, "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
})
SALIDA = "png"
os.makedirs(SALIDA, exist_ok=True)


def miles(n):
    return f"{n:,.0f}".replace(",", ".")


def barras_redondeadas(ax, xs, alturas, ancho, color, alpha=1.0, hatch=None):
    """Barras con extremo de datos redondeado (4 px aprox.) y separación de 2 px."""
    if alpha < 1.0:  # mezclar con la superficie: color sólido, sin bandas por superposición
        c = matplotlib.colors.to_rgb(color)
        s = matplotlib.colors.to_rgb(SUPERFICIE)
        color = tuple(alpha * a + (1 - alpha) * b for a, b in zip(c, s))
        alpha = 1.0
    for x, h in zip(xs, alturas):
        r = max(h * 0.0, 0)
        p = FancyBboxPatch((x - ancho / 2, 0), ancho, h, boxstyle="round,pad=0,rounding_size=0.12",
                           mutation_aspect=max(alturas) / 18, linewidth=0, facecolor=color, alpha=alpha,
                           hatch=hatch, edgecolor=SUPERFICIE if hatch else None)
        ax.add_patch(p)
        # tapar el redondeo inferior: el extremo de datos se ancla a la línea base
        ax.add_patch(plt.Rectangle((x - ancho / 2, 0), ancho, min(h, max(alturas) * 0.03),
                                   linewidth=0, facecolor=color, alpha=alpha))


def guardar(fig, nombre):
    fig.savefig(f"{SALIDA}/{nombre}.png", dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("  ", nombre)


def g_cve():
    filas = list(csv.DictReader(open("cve_por_anio.csv")))
    anios = [int(f["anio"]) for f in filas]
    n = [int(f["cve_publicados"]) for f in filas]
    completo = [f["anio_completo"] == "si" for f in filas]
    fig, ax = plt.subplots(figsize=(14, 6))
    for a, v, c in zip(anios, n, completo):
        barras_redondeadas(ax, [a], [v], 0.72, SERIE, alpha=1.0 if c else 0.45)
    ax.set_xlim(anios[0] - 0.8, anios[-1] + 0.8)
    ax.set_ylim(0, max(n) * 1.15)
    ax.yaxis.grid(True, color=REJILLA, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: miles(v)))
    ax.set_xticks([a for a in anios if a % 2 == 0 or a == anios[-1]])
    ax.tick_params(axis="x", length=0, labelsize=13)
    etiquetar = {anios[0], 2017, 2021, anios[-2], anios[-1]}
    for a, v, c in zip(anios, n, completo):
        if a in etiquetar:
            txt = miles(v) + ("" if c else "\nhasta nov.")
            ax.text(a, v + max(n) * 0.015, txt, ha="center", va="bottom", fontsize=13, color=TINTA, fontweight="semibold")
    ax.set_ylabel("CVE publicados en el año")
    guardar(fig, "cve_por_anio")


def g_cwe():
    filas = sorted(csv.DictReader(open("cwe_2025.csv")), key=lambda f: int(f["cve_publicados"]))[-12:]
    fig, ax = plt.subplots(figsize=(12, 7))
    ys = range(len(filas))
    vals = [int(f["cve_publicados"]) for f in filas]
    ax.barh(list(ys), vals, height=0.68, color=SERIE)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([f'{f["nombre"]}  ({f["cwe"]})' for f in filas], fontsize=14, color=TINTA)
    ax.tick_params(length=0)
    ax.xaxis.set_visible(False)
    ax.spines["bottom"].set_visible(False)
    for y, v in zip(ys, vals):
        ax.text(v + max(vals) * 0.01, y, miles(v), va="center", fontsize=13, color=TINTA2)
    ax.set_xlim(0, max(vals) * 1.12)
    guardar(fig, "cwe_2025")


CATEGORIAS_KEV = [
    ("Corrupción de memoria", {"CWE-787", "CWE-416", "CWE-119", "CWE-125", "CWE-122", "CWE-843", "CWE-190", "CWE-120", "CWE-476", "CWE-121", "CWE-415", "CWE-824"}),
    ("Inyección", {"CWE-78", "CWE-77", "CWE-89", "CWE-94", "CWE-74", "CWE-917", "CWE-1336", "CWE-95", "CWE-79"}),
    ("Autenticación y control de acceso", {"CWE-287", "CWE-306", "CWE-284", "CWE-862", "CWE-863", "CWE-639", "CWE-269", "CWE-288", "CWE-290", "CWE-798", "CWE-269"}),
    ("Validación de entrada y rutas", {"CWE-20", "CWE-22", "CWE-434", "CWE-23", "CWE-36"}),
    ("Deserialización insegura", {"CWE-502"}),
]


def categoria_kev(cwes):
    for nombre, conjunto in CATEGORIAS_KEV:
        if any(c in conjunto for c in cwes):
            return nombre
    return "Otras o sin CWE"


def g_kev():
    d = json.load(open("kev.json"))
    v = d["vulnerabilities"]
    # 1) Agregadas por año
    por_anio = collections.Counter(x["dateAdded"][:4] for x in v)
    anios = sorted(por_anio)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    vals = [por_anio[a] for a in anios]
    for i, (a, n) in enumerate(zip(anios, vals)):
        barras_redondeadas(ax, [i], [n], 0.62, SERIE, alpha=0.45 if a == anios[-1] else 1.0)
        ax.text(i, n + max(vals) * 0.015, miles(n) + ("\nhasta nov." if a == anios[-1] else ""), ha="center", va="bottom", fontsize=14, fontweight="semibold")
    ax.set_xticks(range(len(anios)))
    ax.set_xticklabels(anios, fontsize=14)
    ax.set_xlim(-0.6, len(anios) - 0.4)
    ax.set_ylim(0, max(vals) * 1.2)
    ax.yaxis.set_visible(False)
    ax.tick_params(length=0)
    guardar(fig, "kev_por_anio")

    # 2) Por categoría de falla (dona, pedido explícito; 6 segmentos con etiqueta directa)
    cat = collections.Counter(categoria_kev(x.get("cwes") or []) for x in v)
    orden = [c for c, _ in CATEGORIAS_KEV] + ["Otras o sin CWE"]
    vals = [cat[c] for c in orden]
    colores = CATEGORICA[:5] + [OTROS]
    fig, ax = plt.subplots(figsize=(13, 7))
    cuñas, _ = ax.pie(vals, colors=colores, startangle=90, counterclock=False,
                      wedgeprops=dict(width=0.36, edgecolor=SUPERFICIE, linewidth=3))
    total = sum(vals)
    for cuña, nombre, n in zip(cuñas, orden, vals):
        ang = (cuña.theta2 + cuña.theta1) / 2
        import math
        x, y = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        ax.annotate(f"{nombre}\n{miles(n)} · {n / total:.0%}", xy=(x * 0.82, y * 0.82), xytext=(x * 1.32, y * 1.22),
                    ha="left" if x >= 0 else "right", va="center", fontsize=14, color=TINTA,
                    arrowprops=dict(arrowstyle="-", color=TENUE, linewidth=1))
    ax.text(0, 0.06, miles(total), ha="center", va="center", fontsize=30, fontweight="bold")
    ax.text(0, -0.16, "explotadas\nactivamente", ha="center", va="center", fontsize=13, color=TINTA2)
    ax.set_aspect("equal")
    guardar(fig, "kev_categorias")

    # 3) Fabricantes con más vulnerabilidades explotadas
    fab = collections.Counter(x["vendorProject"] for x in v).most_common(10)[::-1]
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.barh(range(len(fab)), [n for _, n in fab], height=0.66, color=SERIE)
    ax.set_yticks(range(len(fab)))
    ax.set_yticklabels([f for f, _ in fab], fontsize=15, color=TINTA)
    ax.tick_params(length=0)
    ax.xaxis.set_visible(False)
    ax.spines["bottom"].set_visible(False)
    m = max(n for _, n in fab)
    for i, (_, n) in enumerate(fab):
        ax.text(n + m * 0.01, i, miles(n), va="center", fontsize=14, color=TINTA2)
    ax.set_xlim(0, m * 1.12)
    guardar(fig, "kev_fabricantes")
    # resumen para el deck
    rans = sum(1 for x in v if x.get("knownRansomwareCampaignUse") == "Known")
    print(f"KEV total={total} ransomware={rans} version={d.get('catalogVersion')} categorias={dict(zip(orden, vals))}")


def g_dbir():
    filas = list(csv.DictReader(open("dbir.csv")))
    fig, ax = plt.subplots(figsize=(11, 6))
    series = [("explotacion_vulnerabilidades", "Explotación de vulnerabilidades como vector inicial", CATEGORICA[0]),
              ("participacion_terceros", "Brechas con participación de terceros", CATEGORICA[1])]
    ancho = 0.36
    for k, (col, nombre, color) in enumerate(series):
        xs = [i + (k - 0.5) * (ancho + 0.03) for i in range(len(filas))]
        vals = [int(f[col]) for f in filas]
        barras_redondeadas(ax, xs, vals, ancho, color)
        for x, v in zip(xs, vals):
            ax.text(x, v + 0.8, f"{v} %", ha="center", va="bottom", fontsize=15, fontweight="semibold")
        ax.bar([0], [0], color=color, label=nombre)  # entrada de leyenda
    ax.set_xticks(range(len(filas)))
    ax.set_xticklabels([f["edicion"] for f in filas], fontsize=15)
    ax.set_xlim(-0.6, len(filas) - 0.4)
    ax.set_ylim(0, 58)
    ax.yaxis.set_visible(False)
    ax.tick_params(length=0)
    ax.legend(loc="upper left", frameon=False, fontsize=14)
    guardar(fig, "dbir")


def g_paquetes():
    filas = list(csv.DictReader(open("paquetes.csv")))
    fig, ax = plt.subplots(figsize=(11, 5.8))
    vals = [int(f["paquetes"]) for f in filas]
    for i, (f, n) in enumerate(zip(filas, vals)):
        barras_redondeadas(ax, [i], [n], 0.62, "#eb6834", alpha=0.45 if f["calidad"] != "anual" else 1.0)
        ax.text(i, n + max(vals) * 0.015, miles(n), ha="center", va="bottom", fontsize=14, fontweight="semibold")
    ax.set_xticks(range(len(filas)))
    ax.set_xticklabels([f["etiqueta"] for f in filas], fontsize=13)
    ax.set_xlim(-0.6, len(filas) - 0.4)
    ax.set_ylim(0, max(vals) * 1.18)
    ax.yaxis.set_visible(False)
    ax.tick_params(length=0)
    guardar(fig, "paquetes_maliciosos")


if __name__ == "__main__":
    que = sys.argv[1] if len(sys.argv) > 1 else "todo"
    for nombre, fn in [("kev", g_kev), ("cve", g_cve), ("cwe", g_cwe), ("paquetes", g_paquetes), ("dbir", g_dbir)]:
        if que in ("todo", nombre):
            fn()
