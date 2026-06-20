"""
Renueva los tokens de MercadoLibre para las 3 cuentas.
Ejecutar cada 5 horas via Windows Task Scheduler.
"""
import json
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent
CLIENT_ID = "3959231945649654"
CLIENT_SECRET = "PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG"

CUENTAS = [
    {"nombre": "C1", "file": BASE_DIR / "tokens_cuenta1.json"},
    {"nombre": "C2", "file": BASE_DIR / "tokens_cuenta2.json"},
    {"nombre": "C3", "file": BASE_DIR / "tokens_cuenta3.json"},
]


def renovar(cuenta):
    with open(cuenta["file"]) as f:
        datos = json.load(f)

    params = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": datos["refresh_token"],
    }).encode()

    req = urllib.request.Request(
        "https://api.mercadolibre.com/oauth/token",
        data=params,
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        nuevos = json.loads(r.read())

    with open(cuenta["file"], "w") as f:
        json.dump(nuevos, f, indent=2)

    print(f"{cuenta['nombre']}: token renovado (user_id={nuevos['user_id']})")


if __name__ == "__main__":
    for cuenta in CUENTAS:
        try:
            renovar(cuenta)
        except Exception as e:
            print(f"{cuenta['nombre']}: ERROR — {e}")
