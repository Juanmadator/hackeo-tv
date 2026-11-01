"""Arranque automático: servidor web + vigilante en un solo proceso oculto (pythonw).
Se registra como tarea programada de Windows. Registro en vigilante.log y auto.log.
"""
import sys
import threading
import time
import traceback
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
LOG = AQUI / "auto.log"


def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


def servidor():
    import servir
    import tv

    while True:
        try:
            ip = tv.ip_local()
            srv = ThreadingHTTPServer((ip, servir.PUERTO), partial(servir.Handler, directory=str(servir.CARPETA)))
            log(f"servidor en http://{ip}:{servir.PUERTO}/")
            srv.serve_forever()
        except Exception as e:  # noqa: BLE001 - sin red aún, puerto ocupado, etc.
            log(f"servidor caído: {type(e).__name__} {e}; reintento en 10 s")
            time.sleep(10)


def vigilante():
    import vigilante as v

    while True:
        try:
            v.main()
        except Exception as e:  # noqa: BLE001
            log(f"vigilante caído: {type(e).__name__} {e}; reintento en 10 s")
            time.sleep(10)


if __name__ == "__main__":
    log("arranque auto.py")
    try:
        threading.Thread(target=servidor, daemon=True).start()
        vigilante()
    except Exception:
        log(traceback.format_exc())
        raise
