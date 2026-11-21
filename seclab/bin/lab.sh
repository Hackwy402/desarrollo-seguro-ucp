#!/usr/bin/env bash
# lab.sh — Laboratorio guiado "Log4Shell + Security Gate" para estudiantes.
# Un solo comando: arma la app vulnerable, corre el gate en ROJO (con triage de
# IA), espera a que apliques el parche y lo vuelve a correr en VERDE.
#
#   bash seclab/bin/lab.sh
#
# Requisitos: docker (corriendo) y bash. Funciona en Ubuntu y macOS.
# La API key de IA se pide OCULTA y se guarda en seclab/.env (ignorado por git).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECLAB="$(cd "$HERE/.." && pwd)"
APP="$SECLAB/ci-demo-app"
VULN="2.14.1"; FIX="2.26.1"

G=$'\033[38;5;46m'; Y=$'\033[38;5;226m'; C=$'\033[38;5;51m'; R=$'\033[38;5;196m'
B=$'\033[1m'; D=$'\033[2m'; X=$'\033[0m'

# sed -i portatil (GNU en Ubuntu vs BSD en macOS)
sedi() { if sed --version >/dev/null 2>&1; then sed -i "$@"; else sed -i '' "$@"; fi; }

say() { printf "\n${B}${C}▶ %s${X}\n" "$1"; }
pause() { [ -t 0 ] && { printf "\n${D}   (Enter para continuar)${X} "; read -r _; } || true; }

# 0) checks
command -v docker >/dev/null 2>&1 || { printf "${R}Falta docker. Instala Docker y vuelve a correr.${X}\n"; exit 1; }
docker info >/dev/null 2>&1 || { printf "${R}Docker no responde. Arranca el servicio:${X}  sudo systemctl start docker\n"; exit 1; }

# 1) andamiar la app vulnerable si no existe
if [ ! -f "$APP/pom.xml" ]; then
  say "Creando la app de ejemplo con log4j $VULN (vulnerable)"
  mkdir -p "$APP/src/main/java/com/ucp/demo"
  cat > "$APP/pom.xml" <<POM
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.ucp.demo</groupId>
  <artifactId>app-pedidos</artifactId>
  <version>1.0.0</version>
  <packaging>jar</packaging>
  <properties>
    <maven.compiler.source>8</maven.compiler.source>
    <maven.compiler.target>8</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <dependencies>
    <!-- log4j $VULN arrastra CVE-2021-44228 (Log4Shell). El gate debe cazarlo. -->
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-api</artifactId>
      <version>$VULN</version>
    </dependency>
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-core</artifactId>
      <version>$VULN</version>
    </dependency>
  </dependencies>
</project>
POM
  cat > "$APP/src/main/java/com/ucp/demo/App.java" <<'JAVA'
package com.ucp.demo;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

// Feature: registrar la version de API que manda el cliente (cabecera X-Api-Version).
// Ojo: loggear texto controlado por el cliente con log4j vulnerable = vector Log4Shell.
public class App {
  private static final Logger log = LogManager.getLogger(App.class);
  public static void main(String[] args) {
    String apiVersion = args.length > 0 ? args[0] : "v1";
    log.info("Pedido recibido. X-Api-Version={}", apiVersion);
  }
}
JAVA
  printf "${G}   app creada en %s${X}\n" "$APP"
else
  say "Restaurando la app a la version vulnerable ($VULN)"
  sedi "s/>2\.[0-9][0-9]*\.[0-9][0-9]*</>$VULN</g" "$APP/pom.xml"
fi

# 2) ROJO
say "PASO 1 — Escaneo con el Security Gate (esperamos ROJO)"
printf "${D}   El gate corre secretos + SAST + SCA en Docker y pide la IA para explicar.${X}\n"
bash "$HERE/scan.sh" --with-trivy --ai "$APP"; rc=$?
printf "\n${B}Resultado del gate: exit %s${X}  ${D}(1 = bloqueado por hallazgos)${X}\n" "$rc"

pause
# 3) PARCHE
say "PASO 2 — Aplicando el parche: log4j $VULN -> $FIX"
sedi "s/>$VULN</>$FIX</g" "$APP/pom.xml"
grep -m1 "<version>$FIX" "$APP/pom.xml" >/dev/null && printf "${G}   pom.xml actualizado a $FIX${X}\n"

# 4) VERDE
say "PASO 3 — Re-escaneo (esperamos VERDE)"
bash "$HERE/scan.sh" --with-trivy --ai "$APP"; rc=$?
printf "\n${B}Resultado del gate: exit %s${X}  ${D}(0 = sin hallazgos, pasa)${X}\n" "$rc"

say "Lab completo ✅  rojo (bloquea + IA explica) -> parche -> verde"
printf "${D}   Lección: 2.17.1 corrige los CVE de 2021, pero hoy el gate exige %s (CVEs 2025/2026).${X}\n" "$FIX"
