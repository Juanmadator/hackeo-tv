"""Busca la tele Panasonic en la red local: puerto 55000 (control) y descubrimiento SSDP."""
import socket
import sys
from concurrent.futures import ThreadPoolExecutor

RED = sys.argv[1] if len(sys.argv) > 1 else "192.168.1"


def puerto_abierto(ip, puerto=55000, timeout=0.6):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        return s.connect_ex((ip, puerto)) == 0
    finally:
        s.close()


def escanear():
    ips = [f"{RED}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=64) as ex:
        res = list(ex.map(puerto_abierto, ips))
    return [ip for ip, ok in zip(ips, res) if ok]


def ssdp():
    msg = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        'MAN: "ssdp:discover"\r\n'
        "MX: 2\r\n"
        "ST: ssdp:all\r\n\r\n"
    ).encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.settimeout(3)
    s.sendto(msg, ("239.255.255.250", 1900))
    vistos = {}
    try:
        while True:
            data, addr = s.recvfrom(4096)
            txt = data.decode(errors="ignore")
            vistos.setdefault(addr[0], set()).add(txt)
    except socket.timeout:
        pass
    return vistos


if __name__ == "__main__":
    print("== Puerto 55000 abierto en:")
    for ip in escanear():
        print("  ", ip)
    print("== SSDP:")
    for ip, resps in ssdp().items():
        lineas = set()
        for r in resps:
            for l in r.splitlines():
                if l.upper().startswith(("SERVER", "ST:", "LOCATION", "USN")):
                    lineas.add(l.strip())
        print("  ", ip)
        for l in sorted(lineas):
            print("      ", l)
