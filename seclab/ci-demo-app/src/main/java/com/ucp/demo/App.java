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
