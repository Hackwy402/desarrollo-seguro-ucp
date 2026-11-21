#!/usr/bin/env python3
# ai_triage.py — convierte el report.json del gate en un comentario de PR en
# espanol: tabla determinista de hallazgos + explicacion de la IA (que es cada
# CVE, por que importa, como parcharlo). Pensado para correr en GitHub Actions.
#
# AGNOSTICO DE PROVEEDOR: usa el estandar OpenAI-compatible (/chat/completions).
# Sirve con Groq (gratis), Gemini (gratis), OpenRouter, Ollama local, etc.
# Solo cambian base_url + model + api_key. Ninguna key viaja en el codigo.
#
#   python3 ai_triage.py <ruta/report.json>   -> escribe el comentario a stdout
#
# Variables de entorno:
#   GATE_AI_API_KEY    la key del proveedor (o GROQ_API_KEY / OPENAI_API_KEY)
#   GATE_AI_BASE_URL   default: https://api.groq.com/openai/v1
#   GATE_AI_MODEL      default: llama-3.3-70b-versatile
#
# FAIL-SAFE: si no hay key o el proveedor falla, imprime la tabla de hallazgos
# igual y una nota; nunca revienta el pipeline (siempre exit 0). El gate (quien
# bloquea el merge) es el shell, no este script.
import json
import os
import sys
import urllib.request
import urllib.error

MARKER = "<!-- seclab-gate-ai -->"  # para que el workflow actualice el mismo comentario


def load_report(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_error": f"No se pudo leer el reporte ({e})", "findings": [], "total": 0}


def findings_table(report):
    fs = report.get("findings", [])
    if not fs:
        return "_Sin hallazgos registrados._\n"
    rows = ["| Herramienta | Severidad | Regla / CVE | Ubicacion |",
            "|---|---|---|---|"]
    for f in fs[:40]:
        rows.append("| {} | {} | {} | {} |".format(
            f.get("tool", "?"), f.get("severity", "?"),
            f.get("rule", "?"), str(f.get("loc", "?")).replace("|", "\\|")))
    extra = len(fs) - 40
    if extra > 0:
        rows.append(f"| ... | | | +{extra} mas |")
    return "\n".join(rows) + "\n"


def ask_ai(report):
    """Devuelve (texto_markdown, nota). nota != '' cuando la IA no se uso."""
    key = (os.environ.get("GATE_AI_API_KEY")
           or os.environ.get("GROQ_API_KEY")
           or os.environ.get("OPENAI_API_KEY"))
    # ojo: en CI una variable no definida llega como "" (no ausente) -> usar `or`.
    base = (os.environ.get("GATE_AI_BASE_URL") or "https://api.groq.com/openai/v1").rstrip("/")
    model = os.environ.get("GATE_AI_MODEL") or "llama-3.3-70b-versatile"

    if not key:
        return "", ("IA no configurada: define el secret `GATE_AI_API_KEY` "
                    "(p. ej. una key gratis de Groq o Gemini) y `GATE_AI_MODEL`/"
                    "`GATE_AI_BASE_URL` si usas otro proveedor.")

    fs = report.get("findings", [])
    if not fs:
        return "", ""

    # Solo mandamos los hallazgos (datos tecnicos, no secretos).
    compact = [{"tool": f.get("tool"), "sev": f.get("severity"),
                "rule": f.get("rule"), "loc": f.get("loc")} for f in fs[:40]]

    system = (
        "Eres un ingeniero de seguridad de aplicaciones (AppSec) que revisa el "
        "Pull Request de un estudiante en un curso de desarrollo seguro. "
        "Explica en ESPANOL, claro y breve, sin alarmismo. Para el conjunto de "
        "hallazgos: (1) di en una frase el riesgo principal, (2) por cada CVE o "
        "regla relevante explica en 1-2 lineas que es y por que importa, (3) da "
        "el PASO CONCRETO para arreglarlo (version a la que subir, config, o "
        "codigo). Si ves log4j-core 2.14.1 / CVE-2021-44228, di explicitamente "
        "que es Log4Shell (RCE): 2.17.1 corrige los CVE de 2021, pero si el "
        "escaneo aun marca CVEs mas recientes en log4j, hay que subir a la "
        "ultima 2.x estable (2.26.1+), no basta con 2.17.1. "
        "Usa Markdown con vinetas. Maximo ~200 palabras. No inventes CVEs que no "
        "esten en la lista."
    )
    user = ("Hallazgos del gate (JSON):\n```json\n"
            + json.dumps(compact, ensure_ascii=False, indent=2)
            + "\n```\nRedacta el comentario para el PR.")

    msgs = [{"role": "system", "content": system},
            {"role": "user", "content": user}]

    # Holgado: los modelos con reasoning (p. ej. Kimi) gastan parte del
    # presupuesto "pensando"; si es bajo, el `content` util vuelve truncado/vacio.
    max_tok = int(os.environ.get("GATE_AI_MAX_TOKENS") or 3000)

    def call(temp):
        payload = {
            "model": model,
            "messages": msgs,
            "temperature": temp,
            "max_tokens": max_tok,
        }
        # pista estandar para abaratar el "pensado" si el modelo lo soporta;
        # los proveedores que no la conocen la ignoran.
        eff = os.environ.get("GATE_AI_REASONING_EFFORT")
        if eff:
            payload["reasoning_effort"] = eff
        req = urllib.request.Request(
            base + "/chat/completions", data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"Authorization": "Bearer " + key,
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read().decode("utf-8"))
        # Solo el `content` final; el reasoning_content es borrador, no se publica.
        return (data["choices"][0]["message"].get("content") or "").strip()

    # Algunos modelos (p. ej. Kimi k2.6) solo aceptan temperature=1.
    temp_env = os.environ.get("GATE_AI_TEMPERATURE")
    temp = float(temp_env) if temp_env else 0.2
    try:
        return call(temp), ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        if e.code == 400 and "temperature" in body.lower() and temp != 1:
            try:
                return call(1), ""   # reintento: el proveedor exige temperature=1
            except Exception as e2:
                return "", f"IA no disponible ({type(e2).__name__}: {e2})."
        return "", f"IA no disponible (HTTP {e.code} de {base}). Revisa modelo/key. Detalle: {body}"
    except Exception as e:
        return "", f"IA no disponible ({type(e).__name__}: {e})."


def main():
    if len(sys.argv) < 2:
        print("uso: ai_triage.py <report.json>", file=sys.stderr)
        sys.exit(0)
    report = load_report(sys.argv[1])
    total = report.get("total", len(report.get("findings", [])))

    out = [MARKER, "## 🛡️ Gate de seguridad — resultado del escaneo", ""]
    if report.get("_error"):
        out.append(f"> ⚠️ {report['_error']}")
    if total and total > 0:
        out.append(f"🚫 **Bloqueado: {total} hallazgo(s).** Este PR no debe mergearse asi.")
    else:
        out.append("✅ **Sin hallazgos.** El gate pasa.")
    out += ["", "### Hallazgos", findings_table(report)]

    ai_text, nota = ask_ai(report)
    if ai_text:
        out += ["### 🤖 Explicacion y remediacion (IA)", "", ai_text, ""]
    if nota:
        out += [f"> 🤖 _{nota}_", ""]
    out += ["---",
            "_Escaneo automatico (SCA/SAST/secretos) + triage con IA. "
            "Corrige los hallazgos y vuelve a pushear para re-evaluar._"]
    print("\n".join(out))


if __name__ == "__main__":
    main()
