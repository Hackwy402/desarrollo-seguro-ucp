"""Genera las slides de la sesión 3 (mismo sistema visual que las sesiones 1 y 2)."""
import html, json, pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent.parent / "project"
OUT = BASE / "slides"
LOGO = sys.argv[1] if len(sys.argv) > 1 else "/_blob/LOGO"
SANS = "font-family:'IBM Plex Sans', Arial, sans-serif"
MONO = "font-family:'JetBrains Mono', 'Courier New', monospace"
E = html.escape
INK, PAPER, ORANGE, ORANGE_D, BLUE, MUTED, SOFT, CARD_D = "#12202B", "#F4F2EC", "#E8893A", "#A8520F", "#2F6FB0", "#4A5560", "#BCC8D2", "#1C2E3C"
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

# ---------------------------------------------------------------- S1 Encuadre
section("s1", "Encuadre: agenda del día, puente con la sesión 2 y verificación del entorno")
save("cover", f'''<div style="display:flex;justify-content:space-between;align-items:center">
<img src="{LOGO}" alt="Universidad Católica de Pereira" style="width:420px;height:152px;object-fit:contain">
<p style="{MONO};font-size:26px;color:{SOFT};letter-spacing:2px;text-align:right">ESPECIALIZACIÓN EN DESARROLLO DE SOFTWARE<br>OPTATIVA I · COHORTE 2026-2</p>
</div>
<div style="display:flex;flex-direction:column;gap:32px">
<div style="width:120px;height:8px;background:{ORANGE};border-radius:4px"></div>
<h1 style="font-size:112px;font-weight:700;line-height:1.05;color:{PAPER}">Desarrollo seguro de software</h1>
<p style="font-size:44px;color:{SOFT};line-height:1.3">Sesión 3 · Autenticación, APIs y criptografía, verificadas con ASVS 5.0</p>
</div>
<div style="display:flex;justify-content:space-between;align-items:end">
<p style="font-size:32px;color:{PAPER}"><b>Ing. Jawy Andrés Romero</b></p>
<p style="{MONO};font-size:28px;color:{SOFT}">Sábado 14 de noviembre de 2026 · presencial</p>
</div>''', "Ayer la pregunta fue qué puede salir mal y cómo se corrige en el código. Hoy: quién es quién (autenticación), qué puede hacer (autorización en APIs), cómo protegemos los datos (criptografía) y cómo demostramos que todo eso se cumple (ASVS, SAST y DAST). Un solo hilo: la Billetera UCP.",
     dark=True, pad="128px", extra=";justify-content:space-between", fade=True)
mark("s1")

save("agenda", kicker("HOY · 8:00 A. M. A 5:00 P. M.") + h2("Quién es, qué puede hacer y cómo lo demostramos") + table(
    ["Hora", "Bloque", "Producto"],
    [["8:00", "Repaso y entorno", "Billetera, Semgrep y ZAP listos"],
     ["8:20", "<b>Autenticación</b> · contraseñas, fuerza bruta, MFA y passkeys", "Demo V6"],
     ["9:00", "<b>Tokens</b> · sesiones, JWT, OAuth 2.0 y OIDC", "Demo V9"],
     ["9:40", "<b>APIs</b> · OWASP API Security Top 10", "Demo API1, API3, API4"],
     ["10:10", "Pausa", ""],
     ["10:25", "<b>Criptografía aplicada</b> y secretos", "Demo V11"],
     ["11:00", "<b>Katas</b> en parejas", "De 24 pruebas en rojo a 35 en verde"],
     ["12:30", "Almuerzo", ""],
     ["1:30", "Verificación: ASVS 5.0, Semgrep y ZAP", "Tres fuentes de evidencia"],
     ["2:10", "<b>Lab 2</b> · verificación de su aplicación", "Entregable del 7,5 %"],
     ["4:10", "Revisión entre equipos y entrega", ""],
     ["4:30", "Cierre y sesión 4", "Trazabilidad amenaza → prueba"]],
    [12, 56, 32], size=25, hl=(6, 9)),
    "Las filas resaltadas son trabajo de ustedes: tres horas y media de las ocho. Cada bloque teórico de la mañana termina con su demo en la Billetera UCP, y esas mismas fallas son las katas antes del almuerzo.", gap=28)

save("repaso", kicker("AYER EN LA TIENDA", True) + h2("Quedó una amenaza abierta: la S de STRIDE", True) + cards([
    ("Users", "token-ana", "Un token fijo, que nunca expira y que no se puede revocar. Si se filtra, es Ana para siempre."),
    ("Warning", "Sin límite de intentos", "Nada impedía probar millones de claves. Nadie lo modeló: no había login."),
    ("Database", "Hashes en la base", "La inyección SQL extrajo hash_clave. ¿Qué tan rápido se rompe ese hash?"),
], dark=True) + p("Hoy cerramos las tres, en otra aplicación y con pruebas.", 34, dark=True),
    "Conectar con el Lab 1: casi todos los equipos tenían una amenaza de suplantación en su top 5. Pedir a dos equipos que la lean en voz alta; esa es la que van a verificar en el Lab 2.", dark=True, gap=40)

save("entorno", kicker("8:00 · VERIFICAR EL ENTORNO") + h2("Tres cosas antes de empezar") + code(
    f"git pull<br>docker build -t ucp-billetera demos/sesion-3/02-billetera<br>"
    f"bash demos/sesion-3/02-billetera/katas.sh {OR}| tail -1{END}{A}{A}<span style=\"color:{SOFT}\"># 24 failed, 11 passed</span><br>"
    f"docker pull ghcr.io/zaproxy/zaproxy:stable{A}<span style=\"color:{SOFT}\"># ~1,2 GB: déjenlo bajando</span><br>"
    f"semgrep --version{A}{A}{A}{A}{A}{A}{A}{A}{A}{A}{A}<span style=\"color:{SOFT}\"># o pipx install semgrep</span>") +
    p("Si «24 failed» aparece, todo está bien: esa es la meta de la mañana."),
    "La imagen de ZAP pesa más de un gigabyte: que la descarguen ya, la necesitan después del almuerzo. Si la red del salón no da, tengo la imagen en una memoria USB (docker load).")

# ---------------------------------------------------------------- S2 Autenticación
section("s2", "Autenticación: almacenamiento de contraseñas, política, fuerza bruta, enumeración, MFA y passkeys")
save("billetera", kicker("EL HILO DE HOY") + h2("Billetera UCP: una API, siete fallas") + table(
    ["Endpoint", "Falla", "Control", "ASVS 5.0"],
    [["POST /api/registro", "MD5 sin sal, acepta «123456»", "Argon2id y política", "V6 · V11"],
     ["POST /api/login", "Intentos ilimitados; dice si el usuario existe", "Bloqueo y respuesta única", "V6"],
     ["Authorization: Bearer", "No verifica la firma del JWT", "HS256 fijo, exp, iss, aud", "V9"],
     ["GET /api/cuentas/{id}/…", "Lee cuentas ajenas (BOLA)", "Dueño en la consulta", "V8"],
     ["PATCH /api/perfil", "Acepta rol y saldo; devuelve el hash", "Listas blancas", "V8 · V4"],
     ["?limite=", "-1 o 100000 devuelven todo", "Entero entre 1 y 100", "V4"],
     ["documento", "AES-ECB, llave en el código", "AES-GCM, llave del entorno", "V11"]],
    [26, 32, 26, 16], size=25) + p("Insegura en 127.0.0.1:5005 · segura en 127.0.0.1:5006 · Flask, SQLite, PyJWT, argon2-cffi, cryptography", 26),
    "Es la misma idea de la tienda, pero las fallas de hoy no se arreglan con un ? en la consulta: se arreglan usando bien librerías que ya existen. Ninguna de las soluciones inventa criptografía.", gap=28)
mark("s2")

save("hash", kicker("V6 · V11 · ALMACENAMIENTO DE CONTRASEÑAS") + h2("Un hash rápido es un regalo para el atacante") +
     f'''<div style="display:flex;gap:96px;align-items:end">
<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:150px;font-weight:700;line-height:1;color:{ORANGE_D}">2 573 691</p><p style="font-size:32px;color:{MUTED}">intentos por segundo con MD5, en un núcleo</p></div>
</div>
<div style="display:flex;gap:96px;align-items:end">
<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:150px;font-weight:700;line-height:1;color:{BLUE}">43</p><p style="font-size:32px;color:{MUTED}">con Argon2id, y cada uno ocupa 64 MiB de memoria</p></div>
</div>''' + p("Medido en la VM del curso. Una GPU multiplica el MD5 por mil; el Argon2id casi no mejora: esa es la idea de una función con costo de memoria.", 28),
     "Estos números salen de la demo, en vivo. El punto no es la cifra exacta sino la relación: unas 60 000 veces más caro probar cada clave. La sal hace que dos usuarios con la misma clave tengan hashes distintos y que no sirvan las tablas precalculadas; Argon2id la genera sola y la guarda dentro del hash.", gap=36)

save("hash-codigo", kicker("V6 · KATA v6_claves") + h2("Argon2id con la librería, no a mano") +
     code(f"def hashear(clave):<br>{A}return hashlib.md5(clave.encode()).hexdigest(){A}<span style=\"color:{SOFT}\"># 962b0054…</span>", "Antes") +
     code(f"from argon2 import PasswordHasher<br>PH = PasswordHasher(){A}{A}<span style=\"color:{MUTED}\"># t=3, m=64 MiB, p=4: sobre el mínimo de OWASP</span><br>"
          f"def hashear(clave): return PH.hash(clave)<br><span style=\"color:{MUTED}\"># $argon2id$v=19$m=65536,t=3,p=4$<b>sal</b>$<b>hash</b></span>", "Después", dark_box=False) +
     p("Política (ASVS V6 y NIST 800-63B): largo mínimo (8; se recomiendan 15; la billetera exige 12), sin reglas de composición, contra una lista de claves comunes y sin cambio periódico forzado."),
     "Si su framework ya trae hash de contraseñas (Django, Spring Security, ASP.NET Identity, Laravel), úsenlo y verifiquen el algoritmo y los parámetros. La prueba del registro con una frase con espacios existe para que nadie meta una regla de «solo alfanuméricos».", gap=26)

save("fuerza", kicker("V6 · KATA v6_fuerza") + h2("El login no debe ayudar al atacante") + table(
    ["Petición", "Insegura", "Segura"],
    [["usuario «nadie», clave x", "404 · «el usuario no existe»", "401 · «usuario o contraseña incorrectos»"],
     ["usuario «ana», clave x", "401 · «contraseña incorrecta»", "401 · «usuario o contraseña incorrectos»"],
     ["6 intentos contra beto", "401 401 401 401 401 401", "401 401 401 401 401 <b>429</b>"]],
    [30, 35, 35], size=26) + cards([
        ("Users", "Enumeración", "Mismo código, mismo mensaje y tiempo parecido: la segura verifica contra un hash señuelo si el usuario no existe."),
        ("Lock", "Fuerza bruta", "Cinco fallos seguidos bloquean al usuario 15 minutos. Un acierto reinicia el contador."),
        ("Warning", "Lo que no cubre", "Password spraying: una clave común contra mil usuarios. Para eso: límite por IP, CAPTCHA adaptativo y MFA."),
    ], size=26),
    "El tiempo de respuesta también enumera: si el usuario no existe y no se calcula ningún hash, la respuesta llega en 1 ms en vez de 80. Por eso el hash señuelo. El bloqueo por usuario tiene un costo: permite bloquear a la víctima a propósito; en producción, bloqueos progresivos y por IP. En la kata, el contador vive en memoria; en producción, en Redis o en la base de datos.", gap=28)

save("mfa", kicker("V6 · MÁS ALLÁ DE LA CONTRASEÑA", True) + h2("No todo segundo factor resiste el phishing", True) + table(
    ["Factor", "Resiste phishing", "Comentario"],
    [["SMS / correo con código", "No", "SIM swapping; el código se reenvía al sitio falso"],
     ["TOTP (app autenticadora)", "No", "Mejor que SMS, pero el usuario lo teclea en el sitio falso"],
     ["Push con número a confirmar", "Parcial", "Evita la fatiga de notificaciones; no el proxy en tiempo real"],
     ["<b>Passkeys (FIDO2 / WebAuthn)</b>", "<b>Sí</b>", "La firma va atada al dominio: en el sitio falso no hay llave"]],
    [34, 20, 46], size=27).replace(f"color:{INK}\"><tr>", f"color:{INK};background:{PAPER};border-radius:12px\"><tr>") +
    p("Para su proyecto: MFA obligatorio para administradores (ASVS V6, nivel 2) y passkeys como opción para todos.", 30, dark=True),
    "La diferencia clave: con TOTP el usuario es quien decide a qué sitio le entrega el código, y se equivoca. Con WebAuthn el navegador firma un reto que incluye el origen; en ucp-login.example la llave de ucp.edu.co no existe. passkeys.dev tiene librerías para cada lenguaje.", dark=True, gap=32)

save("demo-v6", kicker("DEMO · AUTENTICACIÓN", True) + h2("Enumeración, fuerza bruta y el costo de un hash", True) + code(
    f"bash demos/sesion-3/02-billetera/demo-billetera.sh<br><span style=\"color:{SOFT}\"># pasos V6: ENUMERACIÓN · FUERZA BRUTA · CONTRASEÑAS</span>") +
    p("Fíjense en las dos columnas: la misma petición contra :5005 y contra :5006.", 30, dark=True),
    "Correr hasta el paso de contraseñas. Detener ahí: los pasos de JWT y API van con su bloque.", dark=True)

# ---------------------------------------------------------------- S3 Tokens
section("s3", "Tokens y sesiones: sesión en servidor frente a JWT, anatomía y fallas del JWT, OAuth 2.0 y OIDC")
save("sesiones", kicker("9:00 · V7 SESIONES · V9 TOKENS") + h2("Sesión en el servidor o token autocontenido") + table(
    ["", "Cookie de sesión (id opaco)", "JWT (autocontenido)"],
    [["Dónde vive el estado", "En el servidor", "En el token"],
     ["Cerrar sesión / revocar", "Se borra la sesión: inmediato", "Difícil: vive hasta exp (o lista de revocación)"],
     ["Robo por XSS", "Cookie HttpOnly: JS no la lee", "Si está en localStorage, sí"],
     ["CSRF", "Requiere SameSite o token anti-CSRF", "No, si va en la cabecera Authorization"],
     ["Buen uso", "Aplicaciones web clásicas", "APIs entre servicios, vida corta"]],
    [26, 37, 37], size=26) + p("No es una moda: es una decisión de diseño con consecuencias. Para una SPA con su propio backend, la cookie HttpOnly + SameSite suele ser la opción más segura."),
    "Muchos equipos usan JWT porque el tutorial lo usaba. Pregunta para el grupo: ¿alguno necesita de verdad que el token sea autocontenido? Si su único consumidor es su propio frontend, una sesión de servidor es más simple y se revoca.", gap=28)
mark("s3")

save("jwt", kicker("V9 · ANATOMÍA DE UN JWT") + h2("Un JWT está firmado, no cifrado") + code(
    f"<span style=\"color:{ORANGE}\">eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9</span>.<span style=\"color:#7FB0E0\">eyJzdWIiOiJhbmEiLCJpc3MiOiJiaWxsZXRlcmEtdWNwIiwi…</span>.<span style=\"color:{SOFT}\">Xq4…</span><br><br>"
    f"<span style=\"color:{ORANGE}\">{{\"alg\": \"HS256\", \"typ\": \"JWT\"}}</span><br>"
    f"<span style=\"color:#7FB0E0\">{{\"sub\": \"ana\", \"iss\": \"billetera-ucp\", \"aud\": \"api-billetera\",<br>{A}\"iat\": 1794605122, \"exp\": 1794606022}}</span><br>"
    f"<span style=\"color:{SOFT}\">HMAC-SHA256(header.payload, secreto)</span>", size=25) + cards([
        ("Search", "Cualquiera lo lee", "base64 no es cifrado: nada de datos personales ni permisos sensibles en el payload."),
        ("Lock", "Nadie lo altera", "…si el servidor verifica la firma, con el algoritmo que él decide."),
        ("Activity", "Vida corta", "exp de 15 minutos; para más, un refresh token rotado."),
    ], size=26),
    "Copiar un token real de la demo en jwt.io (o decodificarlo con base64 en la terminal) para que vean que el payload se lee sin el secreto. El exp - iat de la segura es 900 segundos.", gap=28)

save("jwt-fallas", kicker("V9 · KATA v9_jwt") + h2("Cuatro maneras de aceptar un token falso") +
     code(f"jwt.decode(token, options={{{OR}\"verify_signature\": False{END}}}){A}<span style=\"color:{SOFT}\"># firma ignorada</span><br>"
          f"JWT_SECRETO = {OR}\"secreto\"{END}{A}{A}{A}{A}{A}{A}{A}{A}{A}{A}<span style=\"color:{SOFT}\"># se adivina con un diccionario</span><br>"
          f"jwt.encode({{\"sub\": u}}, …){A}{A}{A}{A}{A}{A}{A}{A}{A}<span style=\"color:{SOFT}\"># sin exp: vale para siempre</span>", "Antes", size=25) +
     code(f"jwt.decode(token, JWT_SECRETO, <b>algorithms=[\"HS256\"]</b>,<br>{A}{A}{A}{A}{A}{A}{A}<b>audience</b>=\"api-billetera\", <b>issuer</b>=\"billetera-ucp\",<br>"
          f"{A}{A}{A}{A}{A}{A}{A}options={{\"require\": [\"exp\", \"iat\", \"sub\", \"iss\", \"aud\"]}})<br>"
          f"JWT_SECRETO = os.environ[\"JWT_SECRETO\"]{A}{A}<span style=\"color:{MUTED}\"># 32+ bytes aleatorios</span>", "Después", dark_box=False, size=25) +
     p("La cuarta: algorithms ausente. Con llaves RS256, un atacante firma con HS256 usando la llave pública como secreto (RFC 8725).", 27),
     "alg: none no es una curiosidad histórica: sigue apareciendo en librerías caseras y en código que usa decode sin verificar «solo para leer el usuario». La audiencia evita que un token emitido para otra API del mismo proveedor de identidad sirva en la suya.", gap=24)

save("oauth", kicker("V10 OAUTH Y OIDC", True) + h2("Si delegan el login, usen el flujo correcto", True) +
     f'''<div style="display:flex;gap:16px;align-items:center">{"<x-shape kind=\"arrow-right\" style=\"background:#E8893A;width:48px;height:24px\"></x-shape>".join(
         f'<div style="flex:1;background:{CARD_D};border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:10px"><p style="{MONO};font-size:22px;color:{ORANGE}">{a}</p><p style="font-size:24px;color:{PAPER};line-height:1.3">{b}</p></div>'
         for a, b in [("1 · APP", "Genera code_verifier y su hash (PKCE), state y nonce"), ("2 · NAVEGADOR", "Login en el proveedor de identidad, no en la app"),
                      ("3 · REDIRECCIÓN", "Vuelve con un code a la redirect_uri exacta"), ("4 · BACKEND", "Cambia code + verifier por tokens; valida el id_token")])}</div>''' +
     table(["Hacer", "No hacer (RFC 9700)"],
           [["Authorization Code + PKCE, también en SPA y móvil", "Implicit (token en la URL)"],
            ["redirect_uri registrada y comparada exacta", "Comodines o prefijos en redirect_uri"],
            ["Validar state, nonce, iss, aud y exp del id_token", "Password grant: la app ve la clave"]],
           [50, 50], size=25).replace(f"color:{INK}\"><tr>", f"color:{INK};background:{PAPER};border-radius:12px\"><tr>"),
     "OAuth 2.0 es autorización delegada; OpenID Connect agrega la identidad (id_token). Para su proyecto: si usan Google, Microsoft Entra, Keycloak o Auth0, la librería oficial ya implementa PKCE; el error típico es aceptar cualquier redirect_uri o no validar el id_token. El capítulo de ASVS 5.0 es V10 (OAuth y OIDC).", dark=True, gap=28)

save("demo-v9", kicker("DEMO · TOKENS", True) + h2("Un token de «admin» sin firma", True) + code(
    f"<span style=\"color:{SOFT}\"># header {{\"alg\":\"none\"}} + payload {{\"sub\":\"admin\"}} + firma vacía</span><br>"
    f"eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0.eyJzdWIiOiAiYWRtaW4ifQ.<br><br>"
    f"Insegura{A}{OR}200{END}{A}{{\"correo\":\"admin@billetera.test\", \"hash_clave\":\"9a0e94…\"}}<br>"
    f"Segura{A}{A}{A}401{A}{{\"error\":\"no autenticado\"}}") + p("Nadie robó una contraseña: el servidor creyó lo que decía el token.", 32, dark=True),
    "Paso V9 del script. Resaltar que el perfil de admin además devuelve el hash MD5: tres fallas encadenadas (token, exposición de propiedades, hash débil).", dark=True)

# ---------------------------------------------------------------- S4 APIs
section("s4", "APIs: OWASP API Security Top 10:2023, BOLA, autorización por propiedad y consumo de recursos")
save("api-top10", kicker("9:40 · OWASP API SECURITY TOP 10:2023") + h2("Las APIs fallan sobre todo en autorización") + table(
    ["#", "Riesgo", "En una frase"],
    [["API1", "<b>Autorización a nivel de objeto (BOLA)</b>", "Cambio el id y veo lo de otro"],
     ["API2", "Autenticación rota", "Tokens débiles, login sin límites"],
     ["API3", "<b>Autorización a nivel de propiedad</b>", "Leo o escribo campos que no debo"],
     ["API4", "<b>Consumo de recursos sin restricción</b>", "Pido todo y tumbo el servicio"],
     ["API5", "Autorización a nivel de función", "Llamo /admin siendo cliente"],
     ["API6", "Acceso sin restricción a flujos de negocio", "Bots que compran todo el inventario"],
     ["API7", "Server-side request forgery", "La API descarga la URL que le doy"],
     ["API8", "Configuración insegura", "CORS, debug, cabeceras"],
     ["API9", "Inventario inadecuado", "La v1 olvidada sigue en línea"],
     ["API10", "Consumo inseguro de APIs", "Confiar ciegamente en el tercero"]],
    [10, 46, 44], size=24, hl=(0, 2, 3)),
    "Las tres resaltadas están en la billetera. API2 la acabamos de ver. Tres de las cinco primeras son de autorización: ninguna herramienta automática sabe que la cuenta 2 no es de Ana. Por eso ASVS V8 es el capítulo más importante para una API.", gap=24)
mark("s4")

save("bola", kicker("API1 · KATA api1_bola") + h2("Es el IDOR de la tienda, en cada endpoint") +
     code(f"@app.get(\"/api/cuentas/&lt;int:cid&gt;/movimientos\")<br>…<br>if not usuario_actual(): return 401<br>{OR}SELECT … FROM movimientos WHERE cuenta_id = ?{END}", "Antes: autenticado ≠ autorizado") +
     code(f"if not db().execute(\"SELECT 1 FROM cuentas <b>WHERE id = ? AND usuario = ?</b>\",<br>{A}{A}{A}{A}{A}{A}{A}{A}{A}{A}{A}{A}(cid, usuario)).fetchone():<br>{A}return jsonify(error=\"no encontrado\"), <b>404</b>", "Después", dark_box=False) +
     p("Demo: Ana pide /api/cuentas/2/movimientos y recibe la nómina y el arriendo de Beto."),
     "Ayer fue un pedido; hoy una cuenta; en su proyecto será una factura, una historia clínica o una nota. La regla es la misma: el dueño va en la consulta. Patrón recomendado: una función por recurso (cuenta_de(usuario, cid)) que todos los endpoints usan, y una prueba de BOLA por endpoint.", gap=26)

save("bopla", kicker("API3 · KATA api3_propiedades") + h2("Qué campos se leen y cuáles se escriben") +
     f'<div style="display:flex;gap:24px">' +
     f'<div style="flex:1;display:flex;flex-direction:column;gap:20px">' +
     code(f"for campo, valor in request.get_json().items():<br>{A}db().execute(f\"UPDATE usuarios<br>{A}{A}SET {OR}{{campo}}{END} = ? …\")", "Antes: asignación masiva", size=24) +
     code(f"PATCH /api/perfil<br>{{\"rol\": \"admin\", \"saldo\": 999999999}}<br>→ 200 {{…\"rol\":\"admin\", \"saldo\":999999999…}}", "Resultado", size=24) + '</div>' +
     f'<div style="flex:1;display:flex;flex-direction:column;gap:20px">' +
     code(f"LECTURA = (\"usuario\", \"nombre\", \"correo\", \"rol\", \"saldo\")<br>ESCRITURA = {{\"nombre\", \"correo\"}}<br>if not set(cambios) &lt;= ESCRITURA:<br>{A}return …, 400<br>perfil[\"documento\"] = \"******\" + doc[-4:]", "Después: listas blancas", dark_box=False, size=24) +
     p("Exposición: SELECT * devolvía hash_clave y el documento cifrado. Asignación: el JSON decidía las columnas (y además era inyección SQL en el identificador).", 26) + '</div></div>',
     "En frameworks: DTOs o serializadores con campos explícitos (Pydantic, DRF serializers, records en Java, [Bind] en .NET). Nunca pasar el modelo de la base directo al JSON de respuesta, ni el JSON de la petición directo al modelo.", gap=28)

save("recursos", kicker("API4 · KATA api4_recursos") + h2("El cliente no decide cuánto trabaja el servidor") +
     f'''<div style="display:flex;gap:96px;align-items:end">
<div style="display:flex;flex-direction:column;gap:8px"><p style="{MONO};font-size:44px;color:{INK}">?limite=-1</p><p style="font-size:150px;font-weight:700;line-height:1;color:{ORANGE_D}">250</p><p style="font-size:30px;color:{MUTED}">movimientos en una respuesta (en SQLite, LIMIT -1 es «sin límite»)</p></div>
<div style="display:flex;flex-direction:column;gap:8px"><p style="{MONO};font-size:44px;color:{INK}">?limite=todo</p><p style="font-size:150px;font-weight:700;line-height:1;color:{ORANGE_D}">500</p><p style="font-size:30px;color:{MUTED}">error interno con traza: int("todo")</p></div>
</div>''' + p("Control: entero entre 1 y 100, texto → 400. Y en la capa de infraestructura: límite de peticiones por cliente, tamaño máximo del cuerpo y tiempo máximo por consulta."),
     "Con 250 filas no se cae nada; con una tabla de 50 millones, una sola petición tumba la base. Un 500 por entrada inválida es además una señal de que no hay validación: lo encontró ZAP, como veremos después del almuerzo.", gap=32)

save("demo-api", kicker("DEMO · APIs", True) + h2("BOLA, recursos y asignación masiva", True) + code(
    f"Insegura{A}GET /api/cuentas/2/movimientos{A}→ {OR}Nómina, Arriendo, Mercado{END}<br>"
    f"Segura{A}{A}{A}GET /api/cuentas/2/movimientos{A}→ 404<br><br>"
    f"Insegura{A}PATCH {{\"rol\":\"admin\",\"saldo\":999999999}}{A}→ {OR}rol admin{END}<br>"
    f"Segura{A}{A}{A}PATCH {{\"rol\":\"admin\",\"saldo\":999999999}}{A}→ 400"),
    "Pasos API1, API4 y API3 del script. Después, pausa de 15 minutos.", dark=True)

# ---------------------------------------------------------------- S5 Cripto
section("s5", "Criptografía aplicada: decisiones correctas, ECB frente a GCM y manejo de secretos")
save("cripto", kicker("10:25 · V11 CRIPTOGRAFÍA APLICADA") + h2("No se inventa: se elige bien y se configura bien") + table(
    ["Necesito…", "Uso", "Nunca"],
    [["Guardar contraseñas", "Argon2id (o scrypt, bcrypt)", "MD5, SHA-*, cifrado reversible"],
     ["Cifrar datos en reposo", "AES-256-GCM o ChaCha20-Poly1305", "ECB; CBC sin MAC"],
     ["Números aleatorios para seguridad", "secrets / SecureRandom / crypto.randomUUID", "random, Math.random"],
     ["Firmar o verificar", "Ed25519, ECDSA P-256, HMAC-SHA256", "RSA con PKCS#1 v1.5 casero"],
     ["Proteger el transporte", "TLS 1.2+ (ideal 1.3) y HSTS", "TLS 1.0/1.1, certificados sin validar"],
     ["Guardar las llaves", "KMS o gestor de secretos, rotación", "En el código, en .env versionado"]],
    [28, 40, 32], size=26) + p("Y prepararse para la criptografía poscuántica: inventario de algoritmos (ASVS V11 lo pide) para poder cambiarlos."),
    "La regla de oro: use la API de alto nivel de una librería mantenida. En Python, cryptography (AESGCM) o PyNaCl; en Java, Tink; en .NET, AesGcm; en Node, crypto con aes-256-gcm. Si ven las palabras ECB, IV fijo o padding manual, algo anda mal.", gap=28)
mark("s5")

save("ecb", kicker("V11 · KATA v11_cripto") + h2("ECB delata los datos repetidos; GCM además detecta la manipulación") + table(
    ["Usuario", "Insegura (AES-ECB)", "Segura (AES-GCM)"],
    [["carla", f"<span style=\"{MONO}\">tMIpBslUKJ/wM75/A/q63g==</span>", f"<span style=\"{MONO}\">eyrqAoC8k1MdtNBmBcNy…</span>"],
     ["dario", f"<span style=\"{MONO}\">tMIpBslUKJ/wM75/A/q63g==</span>", f"<span style=\"{MONO}\">KvIIMf3eKOlQkVyMP4nB…</span>"]],
    [16, 42, 42], size=26) + p("Mismo documento (1088999111) en los dos usuarios.", 26) +
    code(f"nonce = secrets.token_bytes(12){A}{A}<span style=\"color:{MUTED}\"># nunca se repite con la misma llave</span><br>"
         f"blob = nonce + AESGCM(LLAVE).encrypt(nonce, documento, <b>usuario.encode()</b>)<br>"
         f"<span style=\"color:{MUTED}\"># usuario = dato asociado: el cifrado de Ana no descifra como de Beto</span>", "Después", dark_box=False, size=25),
    "Con ECB, quien vea la base sabe qué usuarios comparten documento, y puede copiar el cifrado de una fila a otra sin que nadie lo note. GCM agrega una etiqueta de 16 bytes: si cambia un bit, descifrar lanza InvalidTag. El dato asociado (AAD) amarra el cifrado a su fila. Repetir un nonce con la misma llave en GCM es catastrófico: por eso aleatorio de 12 bytes.", gap=26)

save("secretos", kicker("V13 · SECRETOS", True) + h2("Un secreto en git es para siempre", True) + cards([
    ("Warning", "Borrar no basta", "El commit sigue en el historial, en los forks y en los clones. Si se publicó, se rota."),
    ("Lock", "Del entorno o de un gestor", "JWT_SECRETO y LLAVE_DATOS se leen del entorno; en producción, de un KMS o un gestor de secretos."),
    ("Check", "Se detecta antes del push", "Semgrep (p/secrets) hoy; gitleaks en el pipeline el viernes 20."),
], dark=True) + p("En la billetera insegura hay dos: LLAVE_DATOS y JWT_SECRETO = \"secreto\". La regla secreto-en-el-codigo los marca.", 30, dark=True),
    "Pregunta al grupo: ¿quién tiene un .env en el repositorio del proyecto? Si alguno levanta la mano, ese es su primer hallazgo del Lab 2. Rotar significa generar uno nuevo y revocar el viejo, no solo borrarlo.", dark=True, gap=36)

save("demo-v11", kicker("DEMO · CRIPTOGRAFÍA", True) + h2("Dos usuarios, un documento, ¿un cifrado?", True) + code(
    f"Insegura{A}carla {OR}tMIpBslUKJ/wM75/A/q63g=={END}{A}dario {OR}tMIpBslUKJ/wM75/A/q63g=={END}<br>"
    f"Segura{A}{A}{A}carla eyrqAoC8k1MdtNBm…{A}{A}{A}{A}{A}dario KvIIMf3eKOlQkVyM…"),
    "Último paso del script; después, docker compose down. Pasamos a las katas.", dark=True)

# ---------------------------------------------------------------- S6 Katas
section("s6", "Katas en parejas: los siete controles de la Billetera UCP con sus pruebas")
save("katas", kicker("11:00 · KATAS EN PAREJAS · 90 MIN", True) + h2("Ahora el control lo construyen ustedes", True) +
     f'''<div style="display:flex;gap:40px">
<div style="flex:1;display:flex;flex-direction:column;gap:20px">
<div style="background:#0B1620;border-radius:16px;padding:32px"><p style="{MONO};font-size:26px;color:{SOFT};line-height:1.6">code demos/sesion-3/02-billetera/app.py<br><span style="color:{ORANGE}">bash demos/sesion-3/02-billetera/katas.sh api1_bola</span><br>bash demos/sesion-3/02-billetera/katas.sh</p></div>
<p style="font-size:28px;color:{SOFT};line-height:1.4">Orden: api1 → api3 → api4 → v6_claves → v6_fuerza → v9_jwt → v11_cripto</p>
</div>
<div style="flex:1;display:flex;flex-direction:column;gap:20px">''' + "".join(
         f'<div style="display:flex;gap:16px;align-items:center"><x-icon name="Check" style="color:{ORANGE};width:40px;height:40px"></x-icon><p style="font-size:28px;color:{PAPER}">{t}</p></div>'
         for t in ["Editen solo <b>app.py</b>; no toquen tests/", "No inventen criptografía: argon2-cffi, pyjwt y cryptography ya están", "Las pruebas corren sin red y en solo lectura", "Anoten el capítulo ASVS de cada control: es su Lab 2"]) + "</div></div>",
     "Mismas reglas que ayer: una persona escribe y la otra lee las pruebas, y cambian en cada kata. Las tres primeras son de autorización y salen rápido; las de autenticación y criptografía son de leer la documentación de la librería. A las 12:20 pido una pareja que muestre v9_jwt.", dark=True, fade=True)
mark("s6")

STY = {"actor": ("#FFFDF8", INK, INK), "req": ("#FFFDF8", "#B9B3A5", MUTED), "falla": ("#FBEBDD", ORANGE, ORANGE_D), "ctrl": ("#E3EDF7", BLUE, BLUE)}


def card(t, icon, etq, texto, mono):
    bg, bd, ic = STY[t]
    return (f'<div style="flex:1;background:{bg};border:2px solid {bd};border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:14px">'
            f'<div style="display:flex;gap:14px;align-items:center"><x-icon name="{icon}" style="color:{ic};width:44px;height:44px"></x-icon>'
            f'<p style="{MONO};font-size:24px;color:{ic};letter-spacing:1px">{E(etq)}</p></div>'
            f'<p style="{MONO if mono else SANS};font-size:26px;line-height:1.3;color:{INK}">{E(texto)}</p></div>')


ARROW = '<x-shape kind="arrow-right" style="background:#B9B3A5;width:48px;height:24px"></x-shape>'
KATAS = [
 ("k-api1", "API1 AUTORIZACIÓN POR OBJETO (BOLA)", 10, "Ana no lee la cuenta de Beto",
  [("actor", "Users", "ATACANTE", "Ana, con su token válido", False), ("req", "Globe", "PETICIÓN", "GET /api/cuentas/2/movimientos", True),
   ("falla", "Warning", "HOY", "WHERE cuenta_id = ?", True), ("ctrl", "Lock", "CONTROL", "cuenta de Ana o 404", False)],
  ["Ana ve sus movimientos: 200 y 20 filas", "Sin sesión: 401", "La cuenta de Beto: 404 y sin «Nómina»", "Cuenta inexistente: 404"],
  "api1_bola", "Consulte cuentas con id y usuario antes de leer movimientos. Ajena e inexistente responden igual.", "V8 Autorización", "movimientos",
  "Es la más rápida: es la misma de ayer. Sirve para calentar y para que vean que el patrón se repite en cada recurso."),
 ("k-api3", "API3 AUTORIZACIÓN POR PROPIEDAD", 15, "El cliente no elige sus campos",
  [("actor", "Users", "ATACANTE", "Ana edita su perfil", False), ("req", "Globe", "PETICIÓN", "{\"rol\": \"admin\"}", True),
   ("falla", "Warning", "HOY", "SET {campo} = ? por cada llave", True), ("ctrl", "Lock", "CONTROL", "Listas blancas de lectura y escritura", False)],
  ["El perfil no trae hash_clave", "Documento: ******3456", "Editar nombre funciona", "rol y saldo no cambian", "Campo no permitido: 400"],
  "api3_propiedades", "Dos conjuntos: lo que se muestra y lo que se edita. Para el documento, use descifrar() y deje los 4 últimos.", "V8 Autorización · V4 APIs", "ver_perfil y editar_perfil",
  "La prueba del documento enmascarado depende de descifrar(): si ya hicieron v11 con otro formato, tiene que seguir funcionando. El nombre de la columna debe salir de la lista blanca, no del JSON."),
 ("k-api4", "API4 CONSUMO DE RECURSOS", 10, "Paginación con techo",
  [("actor", "Users", "CLIENTE", "Cualquier usuario autenticado", False), ("req", "Globe", "PETICIÓN", "?limite=-1", True),
   ("falla", "Warning", "HOY", "int(limite) sin rango", True), ("ctrl", "Lock", "CONTROL", "1 ≤ limite ≤ 100 · texto → 400", True)],
  ["limite=50 devuelve 50", "limite=100000: 400 o máximo 100", "limite=-1: 400 o máximo 100", "limite=todo: 400, no 500"],
  "api4_recursos", "try/except ValueError alrededor de int(), y un rango. Decidan: ¿400 o recortar a 100? Ambas pasan.", "V4 APIs · V2 Validación", "movimientos",
  "Pedir que justifiquen la decisión entre rechazar y recortar. Rechazar es más explícito; recortar es más amable con clientes existentes."),
 ("k-v6c", "V6 CONTRASEÑAS", 15, "Argon2id y una política sensata",
  [("actor", "Users", "ATACANTE", "Tiene una copia de la base", False), ("req", "Database", "ENCUENTRA", "962b00548e226b6a…", True),
   ("falla", "Warning", "HOY", "md5(clave), sin sal", True), ("ctrl", "Lock", "CONTROL", "PasswordHasher().hash()", True)],
  ["El hash empieza por $argon2id$", "Misma clave, distinto hash", "123456 y password1234: 400", "Una frase con espacios: 201"],
  "v6_claves", "PH.verify lanza excepción si no coincide: atrápela y devuelva False. La lista de comunes está en claves_comunes.txt.", "V6 Autenticación · V11", "hashear, verificar_clave, registro",
  "datos.crear recibe hashear: al cambiarla, los usuarios de prueba se crean con Argon2id sin migración. En un sistema real habría que migrar: rehash al siguiente login exitoso (PH.check_needs_rehash)."),
 ("k-v6f", "V6 FUERZA BRUTA Y ENUMERACIÓN", 15, "El login no da pistas",
  [("actor", "Users", "ATACANTE", "Script con un diccionario", False), ("req", "Globe", "PETICIÓN", "6 × POST /api/login", True),
   ("falla", "Warning", "HOY", "404 «no existe» · sin límite", False), ("ctrl", "Lock", "CONTROL", "401 único · 429 al quinto fallo", False)],
  ["Usuario inexistente y clave errada: misma respuesta", "5 fallos → 429 aunque la clave sea correcta", "El bloqueo es por usuario", "Un acierto reinicia el contador"],
  "v6_fuerza", "Un diccionario FALLOS = {usuario: (n, desde)}. Para el tiempo, verifique contra un hash señuelo si el usuario no existe.", "V6 Autenticación", "login",
  "La prueba no mide el tiempo, pero la solución de referencia usa un hash señuelo. Discutir el costo del bloqueo: un atacante puede bloquear a la víctima. Por eso en producción se combina con límites por IP y MFA."),
 ("k-v9", "V9 TOKENS JWT", 15, "Solo valen los tokens que emitimos",
  [("actor", "Users", "ATACANTE", "Fabrica su propio token", False), ("req", "Globe", "TOKEN", "{\"alg\":\"none\",\"sub\":\"admin\"}", True),
   ("falla", "Warning", "HOY", "verify_signature: False", True), ("ctrl", "Lock", "CONTROL", "HS256 · exp · iss · aud", True)],
  ["alg none, otro secreto o «secreto»: 401", "Token expirado: 401", "Audiencia ajena: 401", "Emitido con iat y exp ≤ 15 min"],
  "v9_jwt", "Defina JWT_EMISOR y JWT_AUDIENCIA. Secreto: os.environ.get(\"JWT_SECRETO\") or secrets.token_hex(32).", "V9 Tokens autocontenidos", "emitir_token, usuario_actual",
  "Las pruebas leen JWT_SECRETO, JWT_EMISOR y JWT_AUDIENCIA del módulo para fabricar tokens válidos pero vencidos o con otra audiencia. Si generan el secreto al azar al arrancar, los tokens mueren al reiniciar: en producción viene del entorno."),
 ("k-v11", "V11 CIFRADO DE DATOS", 10, "Cifrado autenticado, llave fuera del código",
  [("actor", "Users", "ATACANTE", "Lee o edita la base", False), ("req", "Database", "VE", "Dos documentos iguales", False),
   ("falla", "Warning", "HOY", "AES-ECB, llave en app.py", True), ("ctrl", "Lock", "CONTROL", "AESGCM + nonce + AAD", True)],
  ["Ida y vuelta funciona", "Mismo texto, distinto cifrado", "Un bit cambiado: InvalidTag", "Con otro usuario: InvalidTag", "La llave no es la del código"],
  "v11_cripto", "Guarde nonce + cifrado en base64. El usuario va como dato asociado. LLAVE_DATOS de 32 bytes desde el entorno.", "V11 Criptografía", "cifrar, descifrar, LLAVE_DATOS",
  "Si la llave se genera al azar al arrancar, los datos cifrados no sobreviven a un reinicio: en producción viene de un KMS. En la kata da igual porque la base se crea en cada prueba."),
]
for n, (sid, cat, mins, tit, flujo, pruebas, kata, pista, asvs, fn, notas) in enumerate(KATAS, 1):
    lis = "".join(f"<li>{E(x)}</li>" for x in pruebas)
    save(sid, f'''{kicker(f"KATA {n} DE 7 · {cat} · {mins} MIN")}
<h2 style="font-size:56px;font-weight:700;line-height:1.1">{E(tit)}</h2>
<div style="display:flex;gap:16px;align-items:center">{ARROW.join(card(*f) for f in flujo)}</div>
<div style="display:flex;gap:24px">
<div style="flex:1;background:#FFFDF8;border:2px solid #D9D4C7;border-radius:16px;padding:28px 32px;display:flex;flex-direction:column;gap:14px"><p style="{MONO};font-size:24px;color:{ORANGE_D};letter-spacing:1px">LAS PRUEBAS EXIGEN</p><ul style="font-size:26px;line-height:1.35;color:{INK}">{lis}</ul></div>
<div style="flex:1;display:flex;flex-direction:column;gap:16px">
<div style="background:{INK};border-radius:16px;padding:24px 28px"><p style="{MONO};font-size:24px;color:{PAPER}">bash demos/sesion-3/02-billetera/katas.sh <span style="color:{ORANGE}">{kata}</span></p></div>
<div style="background:#FBEBDD;border-radius:16px;padding:24px 28px;display:flex;flex-direction:column;gap:10px"><p style="{MONO};font-size:24px;color:{ORANGE_D};letter-spacing:1px">PISTA</p><p style="font-size:26px;line-height:1.35;color:{INK}">{E(pista)}</p></div>
<p style="font-size:24px;color:{MUTED}">ASVS 5.0 · {E(asvs)} · {E(fn)} en app.py</p>
</div></div>''', notas, gap=28)

save("meta", kicker("LA META ANTES DEL ALMUERZO") + f'''<div style="display:flex;gap:96px;align-items:end">
<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:200px;font-weight:700;line-height:1;color:{ORANGE_D}">24</p><p style="font-size:36px;color:{MUTED}">pruebas fallan al empezar</p></div>
<x-shape kind="arrow-right" style="background:#D9D4C7;width:180px;height:90px"></x-shape>
<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:200px;font-weight:700;line-height:1;color:{BLUE}">35</p><p style="font-size:36px;color:{MUTED}">pruebas pasan al terminar</p></div>
</div>''' + p("Las 11 que pasan al inicio son de funcionalidad: login, registro, editar el nombre, paginar. Si una se pone roja, rompieron la billetera.", 34, INK),
     "Quien no termine, las cierra en el estudio independiente: es la actividad 1 de la guía. Lo importante es haber hecho al menos una de autorización y una de autenticación antes del Lab 2.", extra=";justify-content:center", gap=48)

# ---------------------------------------------------------------- S7 Verificación
section("s7", "Verificación: ASVS 5.0, análisis estático con Semgrep y dinámico con ZAP, y lo que cada uno no ve")
save("evidencia", kicker("1:30 · ¿HICIMOS UN BUEN TRABAJO?", True) + h2("Tres fuentes de evidencia, ninguna suficiente sola", True) + cards([
    ("Users", "Revisión con ASVS", "Una persona con la lista de requisitos. Encuentra autorización, lógica de negocio y diseño. No escala sola."),
    ("Code", "SAST · Semgrep", "Lee el código sin ejecutarlo. Encuentra patrones: md5, verify_signature, secretos. No sabe si el control está en otra capa."),
    ("Globe", "DAST · ZAP", "Ataca la aplicación corriendo. Encuentra cabeceras, errores 500, configuración. No sabe de quién es la cuenta 2."),
], dark=True) + p("Más las pruebas automáticas de las katas: la única evidencia que se repite en cada cambio.", 32, dark=True),
    "Este es el marco del Lab 2. La pregunta 4 del manifiesto de modelado de amenazas, respondida con datos. En la sesión 4, las tres fuentes (más SCA y secretos) se vuelven etapas del pipeline.", dark=True, gap=36)
mark("s7")

save("asvs", kicker("OWASP ASVS 5.0") + h2("La lista de lo que hay que verificar") + table(
    ["Capítulos que tocamos hoy", "Nivel 1: el mínimo de su proyecto"],
    [["V6 Autenticación", "Largo mínimo, lista de comunes, límite de intentos, sin enumeración"],
     ["V7 Sesiones", "Expiración, invalidación al cerrar sesión, cookies seguras"],
     ["V8 Autorización", "Por objeto, por propiedad y por función, siempre en el servidor"],
     ["V9 Tokens autocontenidos", "Firma verificada, algoritmos fijos, exp, audiencia"],
     ["V10 OAuth y OIDC", "Code + PKCE, redirect_uri exacta, validar id_token"],
     ["V11 Criptografía", "Algoritmos aprobados, cifrado autenticado, aleatorio seguro"],
     ["V4 APIs · V13 Configuración", "Respuestas mínimas, límites, secretos fuera del código"]],
    [36, 64], size=26) + p("Niveles: 1 para toda aplicación, 2 para la mayoría con datos sensibles, 3 para alto valor. Cada requisito tiene número: en el Lab 2 citan el número exacto."),
    "ASVS 5.0 (mayo de 2025) reorganizó los capítulos respecto de 4.0: si encuentran guías viejas con V2 Autenticación o V3 Sesiones, es la numeración anterior. Mostrar el repositorio github.com/OWASP/ASVS, carpeta 5.0/en, y buscar juntos un requisito de V6.", gap=26)

save("semgrep", kicker("SAST · SEMGREP CON REGLAS PROPIAS") + h2("Una regla por cada falla que no queremos volver a ver") +
     f'<div style="display:flex;gap:24px">' +
     f'<div style="flex:1.2">' + code(
         f"- id: jwt-sin-verificar-firma<br>{A}message: jwt.decode con verify_signature=False …<br>{A}severity: ERROR<br>{A}languages: [python]<br>"
         f"{A}metadata: {{cwe: CWE-347, asvs: V9}}<br>{A}pattern: |<br>{A}{A}jwt.decode(..., options={{...,<br>{A}{A}{A}\"verify_signature\": False, ...}}, ...)", size=24) + '</div>' +
     f'<div style="flex:1;display:flex;flex-direction:column;gap:20px;justify-content:center">' +
     f'<div style="display:flex;gap:48px;align-items:end"><div><p style="font-size:140px;font-weight:700;line-height:1;color:{ORANGE_D}">8</p><p style="font-size:28px;color:{MUTED}">hallazgos en la insegura</p></div>'
     f'<div><p style="font-size:140px;font-weight:700;line-height:1;color:{BLUE}">0</p><p style="font-size:28px;color:{MUTED}">en la solución</p></div></div>' +
     p("6 reglas en demos/sesion-3/01-semgrep/reglas-billetera.yml: JWT, algoritmos, hash rápido, ECB, secretos y asignación masiva.", 26) + '</div></div>' +
     code("semgrep scan --config p/owasp-top-ten --config p/secrets --config reglas-billetera.yml .", size=24),
     "Correr demo-semgrep.sh, pasos 4 a 6. El valor de las reglas propias: cada falla que corrigieron hoy se vuelve una regla que impide que regrese. Las reglas de la comunidad dan amplitud; las propias, precisión sobre su código.", gap=26)

save("zap", kicker("DAST · OWASP ZAP CONTRA LA API") + h2("Lo que el escáner ve y lo que no") + table(
    ["Alerta de ZAP", "Insegura", "Segura"],
    [["Falta X-Content-Type-Options", "Sí", "—"], ["Error 500 (limite=texto)", "Sí", "—"],
     ["Server revela la versión", "Sí", "Sí"], ["Falta Cross-Origin-Resource-Policy", "Sí", "Sí"],
     ["<b>BOLA: Ana lee la cuenta de Beto</b>", f"<b style=\"color:{ORANGE_D}\">No la detecta</b>", "—"],
     ["<b>JWT alg: none aceptado</b>", f"<b style=\"color:{ORANGE_D}\">No la detecta</b>", "—"],
     ["<b>Asignación masiva de rol</b>", f"<b style=\"color:{ORANGE_D}\">No la detecta</b>", "—"]],
    [50, 25, 25], size=26, hl=(4, 5, 6)) + code("bash demos/sesion-3/02-billetera/zap/zap-api.sh insegura", size=24),
    "Escaneo con la especificación OpenAPI y el token de Ana, dentro de la red de Docker del laboratorio, nunca contra un sistema ajeno. ZAP hizo 118 verificaciones y no encontró ninguna de las tres fallas graves: no sabe que la cuenta 2 es de Beto ni qué campos son sensibles. Por eso las pruebas de autorización se escriben a mano, como las de las katas.", gap=26)

# ---------------------------------------------------------------- S8 Lab 2
section("s8", "Laboratorio 2: verificación ASVS 5.0 de la aplicación del equipo con revisión, SAST, DAST y una corrección probada")
save("lab2", kicker("2:10 · LAB 2 · 120 MIN · 7,5 %") + h2("Verificar su aplicación con evidencia") + table(
    ["Min", "Paso", "Producto en seguridad/lab2/"],
    [["10", "Preparar: app corriendo en la VM, ZAP y Semgrep", ""],
     ["40", "<b>Revisión ASVS</b>: 20 filas guía + su top 5 del Lab 1", "ASVS.md con número, estado y evidencia"],
     ["20", "<b>Semgrep</b>: p/owasp-top-ten, p/secrets y las reglas de hoy", "semgrep.sarif y TRIAGE.md"],
     ["20", "<b>ZAP</b>: api-scan si hay OpenAPI; si no, baseline", "zap.html y su triage"],
     ["25", "<b>Corregir un «No cumple»</b> con una prueba que falla antes", "Pull request"],
     ["5", "¿Hicimos un buen trabajo? Tres líneas", "Al final de ASVS.md"]],
    [8, 56, 36], size=26, hl=(1, 4)) + p("Enunciado completo: labs/LAB2.md · Entrega a las 4:10 p. m. en el issue del equipo."),
    "El paso más valioso es el de la corrección con prueba: es exactamente lo que hicieron en las katas, ahora en su código. Si la aplicación del equipo no corre en la VM, que trabajen el módulo del Lab 1; la billetera es el último recurso y pierde puntos en alcance.", gap=28)
mark("s8")

save("lab2-regla", kicker("REGLA DEL LABORATORIO", True) + h2("Se escanea solo lo que es suyo y está en su máquina", True) + cards([
    ("Check", "Sí", "Su aplicación corriendo en la VM, en 127.0.0.1 o en la red de Docker del laboratorio. La billetera."),
    ("Warning", "No", "El ambiente de pruebas o producción de su empresa, la aplicación de otro equipo, cualquier sitio de un tercero."),
    ("Lock", "Por qué", "Sin autorización escrita es acceso abusivo a un sistema informático: Ley 1273 de 2009, artículo 269A."),
], dark=True) + p("ZAP en modo api-scan hace ataques activos. En su empresa, eso se pide por escrito y con ventana acordada.", 30, dark=True),
    "Ser explícito: algunos estudiantes trabajan en empresas con aplicaciones expuestas y van a querer escanearlas. No hoy, no desde la universidad y no sin autorización firmada. Pasivo (baseline) sigue siendo tráfico contra el sistema.", dark=True, gap=36)

save("rubrica", kicker("LAB 2 · RÚBRICA") + h2("Qué se califica") + table(
    ["Criterio", "Peso", "Sobresaliente"],
    [["Revisión ASVS", "35 %", "25 filas con número de requisito, estado y evidencia (archivo:línea o prueba)"],
     ["Triage SAST y DAST", "25 %", "Cada hallazgo clasificado como verdadero o falso positivo, justificado y ligado a ASVS"],
     ["Corrección con prueba", "30 %", "Prueba que falla antes y pasa después; PR con requisito y amenaza del Lab 1"],
     ["Reflexión", "10 %", "Responde con datos propios: cuántos cumplen, qué vio solo la revisión humana"]],
    [26, 12, 62], size=26) + p("Un falso positivo bien justificado vale lo mismo que un verdadero positivo. Entregas tardías: hasta la sesión 4, con 20 % menos."),
    "La rúbrica completa está en labs/LAB2.md. Recalcar que «No aplica» necesita justificación de una línea.", gap=32)

# ---------------------------------------------------------------- S9 Cierre
section("s9", "Cierre: trazabilidad de la amenaza de ayer a la prueba de hoy, estudio independiente y sesión 4")
save("trazabilidad", kicker("4:30 · CIERRE", True) + h2("La amenaza de ayer ya tiene su prueba", True) +
     f'''<div style="display:flex;gap:16px;align-items:center">{"<x-shape kind=\"arrow-right\" style=\"background:#E8893A;width:64px;height:32px\"></x-shape>".join(
         f'<div style="flex:1;background:{CARD_D};border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:12px"><p style="{MONO};font-size:24px;color:{ORANGE}">{a}</p><p style="font-size:28px;color:{PAPER};line-height:1.35">{b}</p></div>'
         for a, b in [("AMENAZA · S", "token-ana nunca expira"), ("REQUISITO", "Token con exp ≤ 15 min, firma verificada · ASVS V9"),
                      ("CONTROL", "emitir_token y jwt.decode con require"), ("PRUEBA", "test_token_emitido_expira_en_15_minutos")])}</div>''' +
     p("Así se ve la sección 3 del proyecto. El viernes 20 esas pruebas, Semgrep y ZAP corren solos en el pipeline de cada pull request.", 32, dark=True),
     "Cerrar el círculo con la amenaza que abrimos al empezar. Sesión 2: qué puede salir mal. Sesión 3: cómo verificamos que no sale mal. Sesión 4: cómo lo hacemos automático en cada cambio.", dark=True, gap=48)
mark("s9")

save("estudio", kicker("ESTUDIO INDEPENDIENTE · 14 H · ANTES DEL 20 DE NOVIEMBRE") + h2("De la billetera a su proyecto") + table(
    ["Actividad", "Horas"],
    [["Terminar las 7 katas: 35 pruebas en verde", "2"],
     ["Cheat Sheets: Password Storage, Authentication, Session Management, JWT", "3"],
     ["OWASP API Security Top 10:2023 (API1 a API5 a fondo)", "2"],
     ["NIST SP 800-63B (contraseñas) y passkeys", "1"],
     ["Cryptographic Storage y Secrets Management", "1"],
     ["<b>Cerrar tres «No cumple» de V6, V8 o V9 en su proyecto, con prueba y PR</b>", "4"],
     ["Entregable 1 del proyecto: secciones 1 a 3", "1"]],
    [80, 20], size=26, hl=(5,)) + p("Guía completa y diez preguntas de autoevaluación: estudio/SESION_03.md", 26),
    "La fila resaltada es la que más vale. El entregable 1 junta el modelo del Lab 1 (mejorado con la revisión cruzada) y la tabla ASVS del Lab 2.", gap=28)

save("proxima", kicker("PRÓXIMA SESIÓN · VIERNES 20 NOV · PRESENCIAL", True) +
     '<div style="display:flex;flex-direction:column;gap:28px">' + h2("Cadena de suministro y DevSecOps", True, 80) +
     p("Dependencias (SCA), SBOM, firma de artefactos, secretos en el historial y un pipeline de GitHub Actions que corre sus pruebas, Semgrep y ZAP en cada pull request. Laboratorio 3.", 36, dark=True) + '</div>' +
     cards([("Check", "Traer", "Las katas de hoy, el Lab 2 entregado y una cuenta de GitHub con acceso al repositorio del equipo."),
            ("Code", "Entregable 1", "Secciones 1 a 3 del proyecto integrador, en el repositorio del equipo.")], dark=True) +
     p("Dudas: jawy.romero@gmail.com", 26, dark=True).replace(SANS, MONO),
     "Todo lo de hoy se vuelve automático el viernes: la regla de Semgrep bloquea el PR, la prueba de BOLA corre sola y ZAP baseline se ejecuta contra el contenedor de la aplicación.", dark=True, pad="128px", extra=";justify-content:space-between", fade=True)

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-13T22:00:00Z"}, "lists": "css", "title": "Desarrollo Seguro UCP – Sesión 3",
        "order": ORDER, "sections": SECTIONS,
        "faces": {"ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap"}}}
(BASE / "deck.json").write_text(json.dumps(deck, ensure_ascii=False), encoding="utf-8")
print(len(ORDER), "slides")
