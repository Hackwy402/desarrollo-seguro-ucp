// Script de instalación de DEMOSTRACIÓN.
// Solo IMPRIME qué tendría a su alcance; no lee contenidos ni hace conexiones.
const fs = require("fs");
const os = require("os");
const path = require("path");

const home = os.homedir();
const rutas = [".npmrc", ".ssh", ".aws/credentials", ".config/gh/hosts.yml", ".docker/config.json", ".gitconfig"];
const variables = Object.keys(process.env).filter((k) => /TOKEN|SECRET|KEY|PASSWORD|AWS_/i.test(k));

console.log("\n=========== postinstall de utilidad-fechas ===========");
console.log("Este código se ejecutó con sus permisos, solo por instalar el paquete.");
console.log("Usuario:", os.userInfo().username, "| Directorio:", process.cwd());
console.log("Variables de entorno sensibles visibles:", variables.length ? variables.join(", ") : "ninguna");
for (const r of rutas) {
  console.log(fs.existsSync(path.join(home, r)) ? "  [existe]  " : "  [no hay]  ", "~/" + r);
}
console.log("Un paquete malicioso (como Shai-Hulud) leería estos archivos y los enviaría afuera.");
console.log("=======================================================\n");

// Evidencia de ejecución (archivo local en /tmp, para mostrar que corrió aunque npm no lo imprima).
fs.writeFileSync(path.join(os.tmpdir(), "postinstall-ejecutado.txt"), `utilidad-fechas corrió el ${new Date().toISOString()}\n`);
