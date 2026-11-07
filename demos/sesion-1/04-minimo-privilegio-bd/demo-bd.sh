#!/usr/bin/env bash
# Demo 4: mínimo privilegio y separación de privilegios en la base de datos.
# Supuesto: un atacante logra ejecutar SQL a través de la aplicación (por ejemplo, una inyección).
# Lo que puede hacer depende del usuario con el que la aplicación se conecta.
set -u
cd "$(dirname "$0")" || exit 1
NOMBRE=demo-bd-ucp
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }
sql() { # sql USUARIO CLAVE "SENTENCIA"
  printf '   \033[36m%s>\033[0m %s\n' "$1" "$3"
  docker exec -e PGPASSWORD="$2" "$NOMBRE" psql -h 127.0.0.1 -U "$1" -d facturacion -X -q -v ON_ERROR_STOP=1 -c "$3" 2>&1 | sed 's/^/      /'
}

pausa "0. Levantar PostgreSQL con dos usuarios: migraciones (dueño) y app_facturas (la aplicación)"
docker rm -f "$NOMBRE" >/dev/null 2>&1
docker run -d --name "$NOMBRE" -e POSTGRES_PASSWORD="$(openssl rand -hex 16)" \
  -v "$PWD/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" postgres:16-alpine >/dev/null
until docker exec "$NOMBRE" pg_isready -q -h 127.0.0.1 2>/dev/null && \
      docker exec -e PGPASSWORD=demo-app "$NOMBRE" psql -h 127.0.0.1 -U app_facturas -d facturacion -Xqc 'select 1' >/dev/null 2>&1; do sleep 1; done
echo "   Listo. Sin puertos publicados: solo se llega desde dentro del contenedor."

pausa "1. Lo que la aplicación necesita: leer y crear facturas"
sql app_facturas demo-app "SELECT f.id, c.nombre, f.total FROM facturas f JOIN clientes c ON c.id = f.cliente_id;"
sql app_facturas demo-app "INSERT INTO facturas (cliente_id, total) VALUES (1, 5000) RETURNING id;"

pausa "2. Lo que intentaría un atacante con el usuario de la aplicación"
sql app_facturas demo-app "SELECT nombre, cedula FROM clientes;"
sql app_facturas demo-app "DELETE FROM facturas;"
sql app_facturas demo-app "DROP TABLE facturas;"
sql app_facturas demo-app "CREATE TABLE puerta (x text);"
sql app_facturas demo-app "SELECT usename, passwd FROM pg_shadow;"

pausa "3. Si la aplicación se conectara con el usuario dueño, todo eso funcionaría"
sql migraciones demo-migraciones "SELECT nombre, cedula FROM clientes;"
sql migraciones demo-migraciones "BEGIN; DROP TABLE facturas; ROLLBACK;"

pausa "Fin. La inyección sigue siendo un error (se corrige el 13 de noviembre), pero el daño queda acotado."
docker rm -f "$NOMBRE" >/dev/null
