#!/usr/bin/env bash
# Demo (caso xz utils): lo que se publica no siempre es lo que está en el repositorio.
# Simula un proyecto y un tarball de release con un archivo extra. Todo es inofensivo y temporal.
set -u
pausa() { printf '\n\033[1;33m>> %s\033[0m\n' "$1"; read -r -p "   [Enter para continuar] " _; }

DIR=$(mktemp -d); cd "$DIR" || exit 1
mkdir -p libcompresion/src libcompresion/tests/files && cd libcompresion
git init -q -b main && git config user.email m@demo.local && git config user.name "Mantenedor"
echo 'int comprimir(void) { return 0; }' > src/comprimir.c
echo 'datos de prueba legítimos' > tests/files/good-1.xz
printf 'all:\n\tcc -c src/comprimir.c\n' > Makefile
git add -A && git commit -q -m "v5.6.0" && git tag v5.6.0

pausa "1. El repositorio público: esto es lo que la comunidad revisa"
git ls-files

pausa "2. El mantenedor arma el tarball de la versión «a mano», con un archivo de prueba extra"
mkdir -p /tmp/release-demo && rm -rf /tmp/release-demo/*
cp -r . /tmp/release-demo/libcompresion-5.6.0 && rm -rf /tmp/release-demo/libcompresion-5.6.0/.git
echo 'contenido binario «de prueba» que en el caso real era la carga maliciosa' > /tmp/release-demo/libcompresion-5.6.0/tests/files/bad-3-corrupt_lzma2.xz
printf '\n# paso extra del build que solo existe en el tarball\n' >> /tmp/release-demo/libcompresion-5.6.0/Makefile
tar -czf /tmp/release-demo/libcompresion-5.6.0.tar.gz -C /tmp/release-demo libcompresion-5.6.0
ls -l /tmp/release-demo/*.tar.gz

pausa "3. Control: comparar el tarball publicado con lo que hay en git para esa etiqueta"
mkdir -p /tmp/release-demo/desde-git && git archive v5.6.0 | tar -x -C /tmp/release-demo/desde-git
mkdir -p /tmp/release-demo/publicado && tar -xzf /tmp/release-demo/libcompresion-5.6.0.tar.gz -C /tmp/release-demo/publicado
diff -r /tmp/release-demo/desde-git /tmp/release-demo/publicado/libcompresion-5.6.0

pausa "4. Los hashes no coinciden: el artefacto no es reproducible desde el código"
(cd /tmp/release-demo && git -C "$DIR/libcompresion" archive --format=tar.gz --prefix=libcompresion-5.6.0/ v5.6.0 > desde-git.tar.gz
 shasum -a 256 libcompresion-5.6.0.tar.gz desde-git.tar.gz)

pausa "Fin. Controles: builds reproducibles, publicar desde CI y no desde el equipo del mantenedor, procedencia firmada (SLSA, Sigstore: 20 nov)."
rm -rf /tmp/release-demo "$DIR"
