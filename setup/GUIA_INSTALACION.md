# Guía de instalación – Sesión 1 (tarde)

Tiempo estimado: 2 horas. Al final deben entregar la salida de `check-env.sh`, una captura de Juice Shop en `http://127.0.0.1:3000` y el issue de su equipo.

Si se bloquean, escriban en el chat de la sesión con el paso exacto y el mensaje de error.

## 0. Requisitos del equipo

- 16 GB de RAM recomendados (8 GB mínimo; ver Plan B al final).
- 60 GB libres en disco.
- Virtualización habilitada en la BIOS/UEFI (Intel VT-x o AMD-V).
- Permisos de administrador.

## 1. Hipervisor

| Su equipo | Hipervisor | Imagen de Ubuntu |
|---|---|---|
| Windows o Linux con Intel/AMD | [VirtualBox 7](https://www.virtualbox.org/wiki/Downloads) | Ubuntu 24.04 LTS Desktop (amd64) |
| Mac con Apple Silicon (M1–M4) | [UTM](https://mac.getutm.app/) | Ubuntu 24.04 LTS para ARM64 |
| Mac con Intel | VirtualBox 7 | Ubuntu 24.04 LTS Desktop (amd64) |

Descarga de Ubuntu: <https://ubuntu.com/download>

## 2. Crear la VM

- Nombre: `ucp-dev-seguro`
- 4 vCPU, 8 GB de RAM (6 GB si su equipo tiene 12 GB), disco de 60 GB.
- Red: NAT (no usar modo puente).
- Usuario: el que prefieran. Anoten la contraseña.

Al terminar la instalación, actualicen el sistema:

```bash
sudo apt update && sudo apt -y upgrade
sudo apt install -y git curl wget gnupg ca-certificates python3 python3-venv pipx
pipx ensurepath
```

Cierren la terminal y ábranla de nuevo.

## 3. Herramientas base

### VS Code y Node.js LTS

```bash
sudo snap install code --classic
sudo snap install node --classic --channel=22
```

### Docker Engine

Tomado de la documentación oficial de Docker para Ubuntu:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Cierren sesión en Ubuntu y vuelvan a entrar para que el grupo `docker` aplique. Verifiquen:

```bash
docker run --rm hello-world
```

### Git

```bash
git config --global user.name "Su Nombre"
git config --global user.email "su-correo@ejemplo.com"
```

## 4. Herramientas de seguridad del curso

### Semgrep (análisis estático)

```bash
pipx install semgrep
```

### gitleaks (detección de secretos)

```bash
sudo apt install -y gitleaks
```

### Trivy (dependencias, imágenes e IaC)

Instalar solo desde el repositorio oficial de Aqua Security. Antes de instalar, revisen el canal del curso por si el docente indica una versión fija: en marzo de 2026 hubo un compromiso de la cadena de suministro de esta herramienta, y lo estudiaremos como caso el 20 de noviembre.

```bash
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update
sudo apt install -y trivy
```

### OWASP ZAP (pruebas dinámicas)

```bash
sudo snap install zaproxy --classic
```

### OWASP Threat Dragon (modelado de amenazas)

Descarguen el paquete `.deb` (amd64) o el AppImage de la última versión estable desde <https://github.com/OWASP/threat-dragon/releases> e instálenlo:

```bash
sudo apt install -y ./threat-dragon_*.deb
```

En ARM64 (UTM), si no hay paquete para su arquitectura, usen la versión web en <https://www.threatdragon.com/>.

## 5. Clonar el repositorio y levantar el entorno de práctica

```bash
git clone https://github.com/Hackwy402/desarrollo-seguro-ucp.git
cd desarrollo-seguro-ucp
docker compose -f lab-env/docker-compose.yml up -d
```

Abran <http://127.0.0.1:3000> en el navegador de la VM. Deben ver OWASP Juice Shop. Tomen la captura.

Para apagarlo:

```bash
docker compose -f lab-env/docker-compose.yml down
```

## 6. Verificar el entorno

```bash
bash setup/check-env.sh | tee check-env-$(whoami).txt
```

Todas las líneas deben salir en `OK`. Suban el archivo `check-env-*.txt` y la captura como comentario en el issue de su equipo.

## 7. Registrar el equipo

En GitHub, pestaña **Issues** → **New issue** → plantilla **Equipo y aplicación**. Un issue por equipo (2 a 3 personas).

## Plan B: equipos con 8 GB de RAM

Si la VM no arranca con fluidez, instalen Docker Desktop directamente en su sistema (<https://www.docker.com/products/docker-desktop/>) y las mismas herramientas en el host. El archivo `lab-env/docker-compose.yml` ya publica Juice Shop solo en `127.0.0.1`, así que no queda expuesto a la red. Avisen al docente que usan este plan.
