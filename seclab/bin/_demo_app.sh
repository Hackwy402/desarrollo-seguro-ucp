# _demo_app.sh — crea la app de ejemplo VULNERABLE (log4j 2.14.1). Se sourcea.
#   scaffold_vuln_app <directorio>
# Misma app para el lab local (lab.sh) y para el PR (lab-pr.sh).
scaffold_vuln_app() {
  local app="$1"
  mkdir -p "$app/src/main/java/com/ucp/demo"
  cat > "$app/pom.xml" <<'POM'
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
    <!-- log4j 2.14.1 arrastra CVE-2021-44228 (Log4Shell). El gate debe cazarlo. -->
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-api</artifactId>
      <version>2.14.1</version>
    </dependency>
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-core</artifactId>
      <version>2.14.1</version>
    </dependency>
  </dependencies>
</project>
POM
  cat > "$app/src/main/java/com/ucp/demo/App.java" <<'JAVA'
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
}
