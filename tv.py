"""Control de la Panasonic TX-55FX600E por red. Usa las credenciales de tv.json."""
import json
import socket
from pathlib import Path

import panasonic_viera as pv

AQUI = Path(__file__).parent
CREDS = json.loads((AQUI / "tv.json").read_text())

APPS = {
    "netflix": "0010000200000001",
    "youtube": "0070000200180001",
    "prime": "0010000100180001",
    "disney": "0070002900000002",
    "browser": "0077777700160002",
    "plex": "0076010507000001",
    "appletv": "0070003000000001",
    "rtve": "0020016700000001",
    "atresplayer": "0020016500000001",
}


def conectar():
    return pv.RemoteControl(CREDS["ip"], app_id=CREDS["app_id"], encryption_key=CREDS["enc_key"])


def encendida(timeout=0.6):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        return s.connect_ex((CREDS["ip"], 55000)) == 0
    finally:
        s.close()


def abrir_app(nombre):
    conectar().launch_app(APPS[nombre])


def abrir_web(url):
    conectar().open_webpage(url)


def ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((CREDS["ip"], 55000))
        return s.getsockname()[0]
    finally:
        s.close()


def wake_on_lan():
    mac = bytes.fromhex(CREDS["mac"].replace(":", ""))
    pkt = b"\xff" * 6 + mac * 16
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(pkt, ("255.255.255.255", 9))
    s.close()


if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "estado"
    if cmd == "estado":
        print("encendida" if encendida() else "apagada")
    elif cmd == "app":
        abrir_app(sys.argv[2])
    elif cmd == "web":
        abrir_web(sys.argv[2])
    elif cmd == "tecla":
        conectar().send_key(getattr(pv.Keys, sys.argv[2].upper()))
    elif cmd == "wol":
        wake_on_lan()
    elif cmd == "apagar":
        conectar().turn_off()
