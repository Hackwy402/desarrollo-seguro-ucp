package com.ucp.demo;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * app-pedidos — servicio de ejemplo del curso.
 *
 * La "feature" de este PR: registrar en el log la version de API que manda el
 * cliente en la cabecera X-Api-Version. Inocente... salvo que log4j 2.14.1
 * interpreta ${jndi:...} dentro de ese texto -> CVE-2021-44228 (Log4Shell).
 *
 * No hace falta ejecutar nada: el gate detecta la vulnerabilidad por la
 * DEPENDENCIA (SCA), no por el codigo. El lab 01-log4shell muestra el RCE real.
 */
public class App {
    private static final Logger log = LogManager.getLogger(App.class);

    public static void main(String[] args) {
        String apiVersion = (args.length > 0) ? args[0] : "2.3.1";
        // Dato NO confiable (viene del cliente) tratado como texto de log:
        log.info("Peticion recibida. X-Api-Version: {}", apiVersion);
        System.out.println("app-pedidos arriba.");
    }
}
