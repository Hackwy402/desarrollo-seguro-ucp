#!/usr/bin/env bash
# Demo 6: seguridad de memoria. El mismo error en C y en Rust, compilados en contenedores desechables.
set -u
cd "$(dirname "$0")" || exit 1
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }
c()    { docker run --rm --network none -v "$PWD":/src:ro -w /tmp gcc:14 sh -c "$1"; }
rust() { docker run --rm --network none -v "$PWD":/src:ro -w /tmp rust:1.88-slim sh -c "$1"; }
LARGO="ana_____X"   # 9 caracteres: uno más que el arreglo

pausa "1. El código: nombre[8] y justo después es_admin"
sed -n '5,13p' login.c

pausa "2. C, compilado sin protecciones. Entrada normal y entrada de 9 caracteres"
c "gcc -O0 -U_FORTIFY_SOURCE -fno-stack-protector -o login /src/login.c 2>/dev/null && ./login ana && ./login $LARGO"

pausa "3. C con protección del compilador (_FORTIFY_SOURCE): detecta y aborta, pero solo si alguien la activó"
c "gcc -O2 -D_FORTIFY_SOURCE=2 -o login /src/login.c 2>/dev/null && ./login $LARGO; echo \"   código de salida: \$?\""

pausa "4. Rust: el mismo error no puede corromper la memoria"
rust "rustc -O -o login /src/login.rs 2>/dev/null && ./login ana && ./login $LARGO; echo \"   código de salida: \$?\""

pausa "Fin. En C la seguridad depende de que cada desarrollador y cada opción de compilación acierten; en Rust es el comportamiento por defecto."
