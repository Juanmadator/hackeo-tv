"""Ayuda a entrar en el menú de modo hotel: envía por red ráfagas de AV x3 a la tele en bucle.
Mientras corre, la persona toca (o mantiene) el botón de bajar volumen de la propia tele.
Se detiene al pasar la duración o al crear el fichero stop_hotel.txt.
"""
import sys
import time
from pathlib import Path

import panasonic_viera as pv

import tv

AQUI = Path(__file__).parent
STOP = AQUI / "stop_hotel.txt"
STOP.unlink(missing_ok=True)
DURACION = float(sys.argv[1]) if len(sys.argv) > 1 else 300

rc = tv.conectar()


def tecla(k):
    global rc
    try:
        rc.send_key(k)
    except Exception as e:  # noqa: BLE001 - la sesión cifrada puede caducar; reconectamos
        print("reconecto:", type(e).__name__, e, flush=True)
        rc = tv.conectar()
        rc.send_key(k)


print(time.strftime("%H:%M:%S"), "volumen inicial:", rc.get_volume(), flush=True)
tecla(pv.Keys.TV)
time.sleep(2.5)
t0 = time.time()
n = 0
while time.time() - t0 < DURACION and not STOP.exists():
    for _ in range(3):
        tecla(pv.Keys.INPUT_KEY)
        time.sleep(0.12)
    n += 1
    print(time.strftime("%H:%M:%S"), "ráfaga AV x3 n.º", n, flush=True)
    time.sleep(1.2)
print(time.strftime("%H:%M:%S"), "fin", "(parado a mano)" if STOP.exists() else "(tiempo cumplido)", flush=True)
