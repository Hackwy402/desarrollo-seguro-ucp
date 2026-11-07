// Demo de seguridad de memoria: un nombre largo desborda el arreglo y sobrescribe es_admin.
#include <stdio.h>
#include <string.h>

struct sesion {
    char nombre[8];
    int es_admin;
};

int main(int argc, char *argv[]) {
    struct sesion s;
    s.es_admin = 0;
    strcpy(s.nombre, argc > 1 ? argv[1] : "ana");   // sin verificar el tamaño

    printf("usuario: %s | es_admin = %d\n", s.nombre, s.es_admin);
    puts(s.es_admin ? "ACCESO DE ADMINISTRADOR CONCEDIDO" : "acceso normal");
    return 0;
}
