"""Prueba teclas del mando (por red) con Hackeo TV delante y lee la telemetría de la página:
busca alguna tecla que active la pantalla completa propia del navegador (la barra desaparece).
"""
import sys
import time
from pathlib import Path

import tv

AQUI = Path(__file__).parent
LOG = AQUI / "telemetria.log"
NAVEGADOR = "0077777700160002"
URN = "panasonic-com:service:p00NetworkControl:1"

CANDIDATAS = sys.argv[1:] or [
    "NRC_RED-ONOFF", "NRC_GREEN-ONOFF", "NRC_YELLOW-ONOFF", "NRC_BLUE-ONOFF",
    "NRC_ASPECT-ONOFF", "NRC_DISP_MODE-ONOFF", "NRC_VTOOLS-ONOFF", "NRC_R_SCREEN-ONOFF",
    "NRC_HOLD-ONOFF", "NRC_INDEX-ONOFF", "NRC_FAVORITE-ONOFF", "NRC_P_NR-ONOFF",
    "NRC_SPLIT-ONOFF", "NRC_SWAP-ONOFF", "NRC_CHAT_MODE-ONOFF", "NRC_STTL-ONOFF",
    "NRC_PLAY-ONOFF", "NRC_PAUSE-ONOFF", "NRC_STOP-ONOFF", "NRC_FF-ONOFF", "NRC_REW-ONOFF",
    "NRC_SKIP_NEXT-ONOFF", "NRC_SKIP_PREV-ONOFF", "NRC_TEXT-ONOFF", "NRC_GUIDE-ONOFF",
    "NRC_INFO-ONOFF", "NRC_SUBMENU-ONOFF",
]


def lineas():
    return LOG.read_text(encoding="utf-8", errors="ignore").splitlines() if LOG.exists() else []


def de_la_tele(desde):
    return [l.split("192.168.1.139 ", 1)[1] for l in lineas()[desde:] if "192.168.1.139 " in l]


rc = tv.conectar()


def tecla(codigo):
    global rc
    for _ in range(2):
        try:
            rc.soap_request("nrc/control_0", URN, "X_SendKey", f"<X_KeyEvent>{codigo}</X_KeyEvent>")
            return
        except Exception:  # noqa: BLE001 - sesión caducada: reconectar y reintentar
            rc = tv.conectar()


def al_frente():
    n0 = len(lineas())
    tv.conectar().launch_app(NAVEGADOR)
    time.sleep(4)
    return de_la_tele(n0)


print("al frente:", al_frente(), flush=True)
encontradas = []
for c in CANDIDATAS:
    n0 = len(lineas())
    tecla(c)
    time.sleep(2.6)
    nuevas = de_la_tele(n0)
    marca = ""
    if any("tamaño" in l for l in nuevas):
        marca = "  <<< CAMBIA EL TAMAÑO"
        encontradas.append(c)
    print(f"{c:24s} -> {nuevas}{marca}", flush=True)
    if any("visible=false" in l for l in nuevas):
        print("   (la página quedó oculta: vuelvo al navegador)", al_frente(), flush=True)
print("ENCONTRADAS:", encontradas, flush=True)
