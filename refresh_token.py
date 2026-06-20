import requests
import json
from pathlib import Path

CLIENT_ID     = "3959231945649654"
CLIENT_SECRET = "PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG"
BASE = Path(__file__).parent

CUENTAS = [
    {"nombre": "Cuenta 1", "archivo": BASE / "tokens_cuenta1.json"},
    {"nombre": "Cuenta 2", "archivo": BASE / "tokens_cuenta2.json"},
    {"nombre": "Cuenta 3", "archivo": BASE / "tokens_cuenta3.json"},
]

def refresh_cuenta(nombre, archivo):
    if not archivo.exists():
        print(f"  {nombre}: archivo {archivo.name} no encontrado — omitiendo")
        return False

    tokens = json.loads(archivo.read_text())
    r = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data={
            "grant_type":    "refresh_token",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": tokens["refresh_token"],
        },
    )
    data = r.json()
    if r.ok:
        archivo.write_text(json.dumps(data, indent=2))
        print(f"  {nombre}: OK — user_id={data.get('user_id')} | expira en {data.get('expires_in')} seg")
        return True
    else:
        print(f"  {nombre}: ERROR — {data.get('message', data)}")
        return False

if __name__ == "__main__":
    print("Renovando tokens de las 3 cuentas...")
    for cuenta in CUENTAS:
        refresh_cuenta(cuenta["nombre"], cuenta["archivo"])
    print("Listo.")
