"""Listar advertisers a los que cada usuario tiene acceso, y verificar rol."""
import json
from pathlib import Path
import requests

ROOT = Path(__file__).parent
TOKENS = {
    "C1": (json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"], 483903060),
    "C2": (json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"], 483904870),
    "C3": (json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"], 1194418785),
}

PRODUCT_IDS = ["PADS", "ADS", "BRAND_ADS", "PA", "DA", "MS", "CPG"]


def main():
    for token_name, (token, user_id) in TOKENS.items():
        print(f"\n=== Token {token_name} (uid={user_id}) ===")
        h = {"Authorization": f"Bearer {token}"}

        for pid in PRODUCT_IDS:
            url = f"https://api.mercadolibre.com/advertising/advertisers?product_id={pid}"
            try:
                r = requests.get(url, headers=h, timeout=15)
                if r.status_code == 200:
                    d = r.json()
                    print(f"  product_id={pid}: {json.dumps(d, indent=2)[:1500]}")
                elif r.status_code == 400:
                    pass  # validation
                else:
                    print(f"  product_id={pid}: [{r.status_code}] {r.text[:200]}")
            except Exception as e:
                pass

        # Probemos sin parámetro user_id, y con user_id
        for params in [
            {"product_id": "PADS"},
            {"product_id": "PADS", "user_id": user_id},
            {"site_id": "MLC", "product_id": "PADS"},
        ]:
            url = "https://api.mercadolibre.com/advertising/advertisers"
            r = requests.get(url, headers=h, params=params, timeout=15)
            if r.status_code == 200:
                d = r.json()
                print(f"  params {params} → {json.dumps(d, indent=2)[:1500]}")


if __name__ == "__main__":
    main()
