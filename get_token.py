import requests
from urllib.parse import urlencode

CLIENT_ID     = "3959231945649654"
CLIENT_SECRET = "PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG"
REDIRECT_URI  = "https://victtorino.cl/callback"
SCOPES        = "read write orders ads_read"

# ── PASO 1: Genera este link y ábrelo en el navegador ─────────────────────────
params = {
    "response_type": "code",
    "client_id":     CLIENT_ID,
    "redirect_uri":  REDIRECT_URI,
    "scope":         SCOPES,
}
AUTH_URL = "https://auth.mercadolibre.cl/authorization?" + urlencode(params)
print("Abre este link en tu navegador para autorizar:")
print()
print(AUTH_URL)
print()
print("Luego copia el código TG de la URL de callback y pégalo abajo.")
print()

# ── PASO 2: Pega aquí el código TG que recibirás ──────────────────────────────
CODE = "TG-6a01d95d2603760001447381-483903060"

if "XXXX" in CODE:
    print("Reemplaza CODE con el código TG antes de continuar.")
else:
    response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data={
            "grant_type":    "authorization_code",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code":          CODE,
            "redirect_uri":  REDIRECT_URI,
        },
    )

    data = response.json()

    if response.ok:
        import json
        from pathlib import Path
        Path("tokens_cuenta3.json").write_text(json.dumps(data, indent=2))
        print("Access Token :", data.get("access_token"))
        print("Refresh Token:", data.get("refresh_token"))
        print("Expira en    :", data.get("expires_in"), "seg")
        print("Scopes       :", data.get("scope"))
        print()
        print("tokens.json actualizado con acceso a publicidad.")
    else:
        print("Error:", data)
