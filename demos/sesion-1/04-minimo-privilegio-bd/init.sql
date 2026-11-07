-- Separación de privilegios: el dueño del esquema (migraciones) y el usuario de la aplicación son distintos.
CREATE ROLE migraciones LOGIN PASSWORD 'demo-migraciones';
CREATE ROLE app_facturas LOGIN PASSWORD 'demo-app';

CREATE DATABASE facturacion OWNER migraciones;
\connect facturacion

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO migraciones;
GRANT USAGE ON SCHEMA public TO app_facturas;

SET ROLE migraciones;
CREATE TABLE clientes (id serial PRIMARY KEY, nombre text NOT NULL, cedula text NOT NULL);
CREATE TABLE facturas (id serial PRIMARY KEY, cliente_id int REFERENCES clientes(id), total numeric NOT NULL);
INSERT INTO clientes (nombre, cedula) VALUES ('ana', '1088000001'), ('luis', '1088000002');
INSERT INTO facturas (cliente_id, total) VALUES (1, 120000), (2, 980000), (2, 45000);

-- La aplicación solo lee y crea facturas, y solo ve el nombre del cliente (no la cédula).
GRANT SELECT, INSERT ON facturas TO app_facturas;
GRANT USAGE ON SEQUENCE facturas_id_seq TO app_facturas;
GRANT SELECT (id, nombre) ON clientes TO app_facturas;
RESET ROLE;
