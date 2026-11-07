#!/usr/bin/env bash
# Demo (caso Log4Shell): responder «¿dónde usamos log4j?» con un SBOM, sin explotar nada.
# Trabaja sobre una copia temporal del proyecto de ejemplo. Requiere: trivy.
set -u
ORIGEN="$(cd "$(dirname "$0")" && pwd)/proyecto-java"
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }

DIR=$(mktemp -d); cp -r "$ORIGEN" "$DIR/"; cd "$DIR/proyecto-java" || exit 1

pausa "1. 10 de diciembre de 2021. La pregunta del día: ¿usamos log4j? Miren las dependencias declaradas"
cat build.gradle | sed -n '/dependencies/,/}/p'

pausa "2. Generar el SBOM (CycloneDX): el inventario de lo que realmente lleva la aplicación"
trivy fs --quiet --format cyclonedx --output sbom.cdx.json .
python3 - <<'EOF'
import json
d = json.load(open("sbom.cdx.json"))
print(f"{len(d['components'])} componentes en el SBOM:")
for c in d["components"]:
    marca = "   <-- aquí" if "log4j-core" in c["name"] else ""
    print(f"  {c.get('group','')}:{c['name']} {c.get('version','')}{marca}")
EOF

pausa "3. Cruzar el inventario con las vulnerabilidades conocidas"
trivy fs --quiet --scanners vuln --severity CRITICAL .

pausa "4. Corregir: actualizar a log4j 2.17.1 y volver a escanear"
sed -i.bak 's/2\.14\.1/2.17.1/g' build.gradle gradle.lockfile && rm -f *.bak
grep log4j gradle.lockfile
trivy fs --quiet --scanners vuln --severity CRITICAL . && echo "Sin vulnerabilidades CRITICAL."

pausa "Fin. Sin SBOM, la respuesta a «¿dónde usamos log4j?» tomó semanas en muchas empresas."
rm -rf "$DIR"
