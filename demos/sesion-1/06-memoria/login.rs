// La misma lógica en Rust: el lenguaje verifica los límites del arreglo.
use std::env;

struct Sesion {
    nombre: [u8; 8],
    es_admin: i32,
}

fn main() {
    let entrada = env::args().nth(1).unwrap_or_else(|| "ana".to_string());
    let mut s = Sesion { nombre: [0; 8], es_admin: 0 };

    for (i, b) in entrada.bytes().enumerate() {
        s.nombre[i] = b; // índice fuera de rango => el programa se detiene, no corrompe memoria
    }

    let nombre = String::from_utf8_lossy(&s.nombre);
    println!("usuario: {} | es_admin = {}", nombre.trim_end_matches('\0'), s.es_admin);
    println!("{}", if s.es_admin != 0 { "ACCESO DE ADMINISTRADOR CONCEDIDO" } else { "acceso normal" });
}
