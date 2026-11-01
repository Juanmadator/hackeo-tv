"""Vigila la tele: cuando pasa de apagada a encendida, abre la pantalla de inicio en su navegador.
Corre en segundo plano en el PC. Lleva un registro en vigilante.log.
"""
import datetime as dt
import sys
import time
from pathlib import Path

import tv

AQUI = Path(__file__).parent
LOG = AQUI / "vigilante.log"
PUERTO = 8765
ESPERA_ARRANQUE = 6  # segundos tras detectar el encendido, para que la tele termine de arrancar
INTERVALO = 2


def log(msg):
    linea = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(linea, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(linea + "\n")


def abrir_inicio():
    url = f"http://{tv.ip_local()}:{PUERTO}/"
    for intento in range(3):
        try:
            tv.abrir_web(url)
            log(f"inicio abierto ({url})")
            return True
        except Exception as e:  # noqa: BLE001
            log(f"fallo abriendo inicio (intento {intento + 1}): {type(e).__name__} {e}")
            time.sleep(3)
    return False


def main():
    forzar = "--ahora" in sys.argv
    estado = tv.encendida()
    log(f"arranque: tele {'encendida' if estado else 'apagada'}")
    if forzar and estado:
        abrir_inicio()
    while True:
        ahora = tv.encendida()
        if ahora and not estado:
            log("tele encendida -> esperando arranque")
            time.sleep(ESPERA_ARRANQUE)
            abrir_inicio()
        elif not ahora and estado:
            log("tele apagada")
        estado = ahora
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
