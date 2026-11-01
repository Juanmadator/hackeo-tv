"""Servidor web local de Hackeo TV (opcional: la página queda guardada dentro de la tele).
Sirve docs/ en la IP de este PC y expone:
  GET /hackeo.appcache     -> manifiesto de caché offline: la tele guarda la página y funciona sin el PC
  GET /api/estado          -> ¿está el PC? (si responde, la página activa extras)
  GET /api/app?n=netflix   -> abre esa app en la tele desde el PC (Prime Video, Disney+…)
  GET /api/tecla?k=HOME    -> envía una tecla del mando
  GET /api/log?m=...       -> telemetría de la página (se guarda en telemetria.log)
"""
import hashlib
import json
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import panasonic_viera as pv

import tv

AQUI = Path(__file__).parent
CARPETA = AQUI / "docs"
TELEMETRIA = AQUI / "telemetria.log"
IP = sys.argv[1] if len(sys.argv) > 1 else tv.ip_local()
PUERTO = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
EXCLUIR = ("sonda", "prueba_web", "manifest.webapp")


def ficheros_cache():
    return [p for p in sorted(CARPETA.rglob("*"))
            if p.is_file() and p.suffix != ".appcache" and not any(x in p.name for x in EXCLUIR)]


def manifiesto():
    """Lista todo lo que la tele debe guardar. La versión cambia sola cuando cambia cualquier fichero."""
    fs = ficheros_cache()
    h = hashlib.sha1()
    for p in fs:
        h.update(p.relative_to(CARPETA).as_posix().encode())
        h.update(p.read_bytes())
    lineas = ["CACHE MANIFEST", f"# version {h.hexdigest()[:12]}", "", "CACHE:"]
    lineas += [p.relative_to(CARPETA).as_posix() for p in fs]
    lineas += ["", "NETWORK:", "*", ""]
    return "\n".join(lineas).encode()


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".appcache": "text/cache-manifest", ".svg": "image/svg+xml",
                      ".webapp": "application/x-web-app-manifest+json"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        if getattr(self, "path", "").startswith(("/api/estado", "/api/log")):
            return
        cab = getattr(self, "headers", None)
        ua = cab.get("User-Agent", "") if cab else ""
        print(self.client_address[0], fmt % args, "|", ua[:60], flush=True)

    def _enviar(self, code, datos=b"", tipo="application/json"):
        self.send_response(code)
        if datos:
            self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        if datos:
            self.wfile.write(datos)

    def _json(self, obj, code=200):
        self._enviar(code, json.dumps(obj).encode())

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if u.path == "/hackeo.appcache":
            return self._enviar(200, manifiesto(), "text/cache-manifest")
        if u.path == "/api/log":
            linea = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {self.client_address[0]} #{q.get('n', '')} {q.get('m', '')}"
            print("TEL", linea, flush=True)
            with TELEMETRIA.open("a", encoding="utf-8") as f:
                f.write(linea + "\n")
            return self._enviar(204)
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
