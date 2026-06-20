"""
¿Quién es OWNER del advertiser 79197?
Si fuera C1 o C2, sus tokens deberían haber funcionado en el PUT. Pero todos
fallaron (401), lo que sugiere que el owner es OTRO usuario.

Probamos endpoints que listan usuarios/miembros del advertiser:
  - /advertising/advertisers/{aid}/users
  - /advertising/advertisers/{aid}/members
  - /advertising/advertisers/{aid}
  - /advertising/users
  - /advertising/users/me/advertisers
  - /advertising/users/me

Y también con cada token: /advertising/users/me/advertisers (lista advertisers
donde el user tiene rol cualquiera).
"""
import json
from pathlib import Path
import requests

ROOT = Path(__file__).parent
TOKENS = {
    "C1": (json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"], 483903060),
    "C2": (json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"], 483904870),
    "C3": (json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"], 1194418785),
    "JOSE": (json.loads((ROOT / "tokens_joseruben2.json").read_text())["access_token"], 1194418785),
}
AID = 79197

URLS = [
    f"/advertising/advertisers/{AID}",
    f"/advertising/advertisers/{AID}/users",
    f"/advertising/advertisers/{AID}/members",
    f"/advertising/advertisers/{AID}/roles",
    f"/advertising/advertisers",
    f"/advertising/users",
    f"/advertising/users/me",
    f"/advertising/users/me/advertisers",
    f"/advertising/users/me/roles",
    f"/users/me",  # endpoint general ML
]


def main():
    print(f"\n=== Descubrir OWNER de advertiser {AID} ===\n")
    for token_name, (token, user_id) in TOKENS.items():
        print(f"\n--- Token {token_name} (user_id={user_id}) ---")
        h = {"Authorization": f"Bearer {token}"}
        for path in URLS:
            url = f"https://api.mercadolibre.com{path}"
            try:
                r = requests.get(url, headers=h, timeout=15)
                if r.status_code == 200:
                    body = r.text[:400]
                    print(f"  ✓ [200] {path}")
                    print(f"      {body}")
                elif r.status_code == 401:
                    pass  # silencio (esperado)
                elif r.status_code == 403:
                    print(f"  ! [403] {path}  — {r.text[:100]}")
                elif r.status_code == 404:
                    pass  # silencio
                else:
                    print(f"  ? [{r.status_code}] {path}  — {r.text[:100]}")
            except Exception as e:
                pass

    # Probemos endpoints ML típicos para perfil de usuario y advertiser membership
    print(f"\n\n=== /users/me con cada token ===")
    for token_name, (token, user_id) in TOKENS.items():
        h = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"https://api.mercadolibre.com/users/me", headers=h, timeout=15)
        if r.status_code == 200:
            d = r.json()
            print(f"  [{token_name}] uid={d.get('id')} nick={d.get('nickname')} email={d.get('email')}")


if __name__ == "__main__":
    main()
