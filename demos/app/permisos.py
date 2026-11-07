"""Servicio de permisos de juguete: ana (1) es editora del documento 10; nadie más edita nada."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

EDITORES = {("1", "10")}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        clave = (q.get("usuario", [""])[0], q.get("doc", [""])[0])
        cuerpo = json.dumps({"rol": "editor" if clave in EDITORES else "lector"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
