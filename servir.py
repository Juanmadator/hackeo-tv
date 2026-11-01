"""Servidor web local para la pantalla de inicio de la tele.
Sirve la carpeta docs/ en la IP de este PC y expone una API mínima que los botones de la página usan:
  GET /api/app?n=netflix   -> abre esa app en la tele
  GET /api/tecla?k=HOME    -> envía una tecla del mando
  GET /api/estado          -> hora del PC y si la tele responde
"""
import json
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import panasonic_viera as pv

import tv

CARPETA = Path(__file__).parent / "docs"
IP = sys.argv[1] if len(sys.argv) > 1 else tv.ip_local()
PUERTO = int(sys.argv[2]) if len(sys.argv) > 2 else 8765


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".webapp": "application/x-web-app-manifest+json", ".appcache": "text/cache-manifest"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        ua = self.headers.get("User-Agent", "") if hasattr(self, "headers") else ""
        print(self.client_address[0], fmt % args, "|", ua[:90], flush=True)

    def _json(self, obj, code=200):
        datos = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/api/app":
            n = q.get("n", "")
            if n not in tv.APPS:
                return self._json({"ok": False, "error": "app desconocida"}, 400)
            # Respondemos ya y lanzamos aparte: la tele cambia de app y cerraría la conexión.
            threading.Thread(target=self._abrir, args=(n,), daemon=True).start()
            return self._json({"ok": True, "app": n})
        if u.path == "/api/tecla":
            k = q.get("k", "").upper()
            if not hasattr(pv.Keys, k):
                return self._json({"ok": False, "error": "tecla desconocida"}, 400)
            threading.Thread(target=lambda: tv.conectar().send_key(getattr(pv.Keys, k)), daemon=True).start()
            return self._json({"ok": True, "tecla": k})
        if u.path == "/api/estado":
            return self._json({"ok": True, "tv": tv.encendida()})
        return super().do_GET()

    @staticmethod
    def _abrir(n):
        try:
            tv.abrir_app(n)
            print("abierta", n, flush=True)
        except Exception as e:  # noqa: BLE001
            print("error abriendo", n, type(e).__name__, e, flush=True)


if __name__ == "__main__":
    CARPETA.mkdir(exist_ok=True)
    srv = ThreadingHTTPServer((IP, PUERTO), partial(Handler, directory=str(CARPETA)))
    print(f"Sirviendo {CARPETA} en http://{IP}:{PUERTO}/", flush=True)
    srv.serve_forever()
