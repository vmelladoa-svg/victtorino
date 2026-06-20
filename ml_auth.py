"""
Genera access token para una cuenta de MercadoLibre via OAuth.
Uso:
  python ml_auth.py 1              -> muestra URL para C1
  python ml_auth.py 1 <codigo>     -> intercambia codigo por token y guarda en .env
"""
import requests
import os
import re
import sys
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = "3959231945649654"
CLIENT_SECRET = "PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG"
REDIRECT_URI = "http://localhost:8080"
AUTH_URL = (
    f"https://auth.mercadolibre.cl/authorization"
    f"?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
)


def get_token(code):
    resp = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
    )
    resp.raise_for_status()
    return resp.json()


def update_env(key_access, key_refresh, access_token, refresh_token):
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    def set_var(text, key, value):
        pattern = rf"^{re.escape(key)}=.*$"
        replacement = f"{key}={value}"
        if re.search(pattern, text, re.MULTILINE):
            return re.sub(pattern, replacement, text, flags=re.MULTILINE)
        return text + f"\n{replacement}"

    content = set_var(content, key_access, access_token)
    content = set_var(content, key_refresh, refresh_token)

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("1", "2", "3"):
        print("Uso: python ml_auth.py 1              -> muestra URL")
        print("     python ml_auth.py 1 <codigo>     -> guarda token")
        sys.exit(1)

    num = sys.argv[1]
    label = f"Cuenta {num} (C{num})"
    key_access = f"ML_ACCESS_TOKEN_C{num}"
    key_refresh = f"ML_REFRESH_TOKEN_C{num}"

    if len(sys.argv) == 2:
        # Paso 1: mostrar URL
        print(f"\n=== {label} ===")
        print("1. Abre esta URL en tu navegador (asegurate de estar logueado con la cuenta correcta):")
        print(f"\n   {AUTH_URL}\n")
        print("2. Autoriza la aplicacion.")
        print("3. El navegador intentara abrir localhost:8080 y mostrara un error — eso es normal.")
        print("4. Copia el parametro 'code' de la URL. Ejemplo:")
        print("   http://localhost:8080/?code=TG-XXXXXXXXX")
        print("                               ^^^^^^^^^^^^ esto es el codigo")
        print(f"\n5. Ejecuta: python ml_auth.py {num} TG-XXXXXXXXX\n")

    else:
        # Paso 2: intercambiar codigo
        code = sys.argv[2]
        print(f"Obteniendo token para {label} con codigo: {code[:10]}...")
        try:
            data = get_token(code)
        except requests.HTTPError as e:
            print(f"ERROR HTTP: {e.response.status_code} - {e.response.text}")
            sys.exit(1)

        access = data.get("access_token")
        refresh = data.get("refresh_token")
        user_id = data.get("user_id")

        if not access:
            print(f"ERROR: {data}")
            sys.exit(1)

        update_env(key_access, key_refresh, access, refresh)
        print(f"OK - user_id: {user_id}")
        print(f"Token guardado en .env como {key_access}")
