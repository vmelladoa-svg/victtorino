"""
Generador de token OAuth para la cuenta JOSERUBEN2 (admin del advertiser 79197).

Flujo:
  1. Ejecutá este script con argumento "url" para obtener el link de autorización.
  2. Abrí el link EN VENTANA INCÓGNITO (o tras logout) — necesitás loguear como JOSERUBEN2,
     no como NOVAGRIFERIAS3.
  3. ML te redirige a https://victtorino.cl/callback?code=TG-xxxxx — copiá ese código.
  4. Ejecutá con: python get_token_joseruben.py code TG-xxxxx
  5. Token queda guardado en tokens_joseruben2.json.
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlencode
import requests

CLIENT_ID = "3959231945649654"
CLIENT_SECRET = "PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG"
REDIRECT_URI = "https://victtorino.cl/callback"

# Scopes amigables ML — incluye ads_read + ads_write
SCOPES_FRIENDLY = "offline_access read write ads_read ads_write"

ROOT = Path(__file__).parent
OUT = ROOT / "tokens_joseruben2.json"


def url():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES_FRIENDLY,
    }
    auth_url = "https://auth.mercadolibre.cl/authorization?" + urlencode(params)
    print("PASO 1 — Abrí este link EN VENTANA INCÓGNITO (Ctrl+Shift+N en Chrome):")
    print()
    print(auth_url)
    print()
    print("PASO 2 — Logueate con la cuenta JOSERUBEN2 (la admin del advertiser Ads C3)")
    print("PASO 3 — ML te va a redirigir a https://victtorino.cl/callback?code=TG-xxxxx")
    print("         (la página va a dar error 404 porque victtorino.cl/callback no existe — está OK)")
    print("PASO 4 — Copiá TODO el code (el TG-xxxx-yyyy de la barra de direcciones)")
    print("PASO 5 — Pasámelo, yo lo intercambio por el token")


def exchange(code):
    print(f"Intercambiando code → token...")
    response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        timeout=30,
    )
    data = response.json()
    if not response.ok:
        print(f"❌ Error: {data}")
        return False
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✓ Token guardado en {OUT}")
    print(f"  user_id: {data.get('user_id')}")
    print(f"  scope: {data.get('scope')[:200]}...")
    print(f"  expires_in: {data.get('expires_in')} seg ({data.get('expires_in', 0) // 3600}h)")
    return True


def verify():
    if not OUT.exists():
        print(f"No existe {OUT}")
        return
    tok = json.loads(OUT.read_text())
    h = {"Authorization": f"Bearer {tok['access_token']}"}
    # GET /users/me
    r = requests.get("https://api.mercadolibre.com/users/me", headers=h, timeout=15)
    me = r.json() if r.status_code == 200 else None
    if me:
        print(f"✓ Token válido")
        print(f"  nickname: {me.get('nickname')}")
        print(f"  user_id: {me.get('id')}")
    # GET advertisers
    r = requests.get("https://api.mercadolibre.com/advertising/advertisers",
                    params={"product_id": "PADS"}, headers=h, timeout=15)
    if r.status_code == 200:
        advs = r.json().get("advertisers", [])
        print(f"  advertisers visibles: {len(advs)}")
        for a in advs:
            print(f"    - {a.get('advertiser_id')}: {a.get('advertiser_name')}")
    else:
        print(f"  ✗ no se pudo listar advertisers: {r.status_code} {r.text[:200]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        url()
    elif sys.argv[1] == "url":
        url()
    elif sys.argv[1] == "code" and len(sys.argv) >= 3:
        if exchange(sys.argv[2]):
            verify()
    elif sys.argv[1] == "verify":
        verify()
    else:
        print("Uso:\n  python get_token_joseruben.py url\n  python get_token_joseruben.py code TG-xxxxx\n  python get_token_joseruben.py verify")
