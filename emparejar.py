"""Empareja con la tele: pide el PIN, espera a que se escriba en pin.txt y guarda las credenciales en tv.json."""
import json
import logging
import sys
import time
from pathlib import Path

import panasonic_viera as pv

AQUI = Path(__file__).parent
IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.139"
NOMBRE = sys.argv[2] if len(sys.argv) > 2 else "Hackeo TV"
PIN_TXT = AQUI / "pin.txt"
CREDS = AQUI / "tv.json"

logging.basicConfig(level=logging.DEBUG, format="%(message)s")
PIN_TXT.unlink(missing_ok=True)
rc = pv.RemoteControl(IP)
rc.request_pin_code(name=NOMBRE)
print(f"PIN solicitado como '{NOMBRE}'. Esperando pin.txt...", flush=True)

t0 = time.time()
while time.time() - t0 < 300:
    if PIN_TXT.exists():
        pin = PIN_TXT.read_text().strip()
        if pin:
            break
    time.sleep(1)
else:
    print("Tiempo agotado sin PIN", flush=True)
    raise SystemExit(1)

rc.authorize_pin_code(pincode=pin)
CREDS.write_text(json.dumps({"ip": IP, "mac": "D8:61:62:C9:E3:55", "app_id": rc.app_id, "enc_key": rc.enc_key}, indent=1))
PIN_TXT.unlink(missing_ok=True)
print("Emparejado OK. Credenciales en tv.json", flush=True)
logging.getLogger().setLevel(logging.WARNING)
apps = rc.get_apps()
print(json.dumps(apps, indent=1, ensure_ascii=False), flush=True)
print("entradas:", rc.list_inputs(), flush=True)
