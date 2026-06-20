"""
¿C1 y C2 pueden escribir sus advertisers? Listamos campañas de cada uno, y
probamos un PUT de prueba (sin cambiar nada real — usamos status=current value).
"""
import json
from pathlib import Path
import requests

ROOT = Path(__file__).parent
TOKENS = {
    "C1": (json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"], 78985),
    "C2": (json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"], 79006),
    "C3": (json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"], 79197),
}


def main():
    for token_name, (token, aid) in TOKENS.items():
        print(f"\n=== {token_name} | advertiser {aid} ===")
        h = {"Authorization": f"Bearer {token}"}

        # Listar campañas
        r = requests.get(
            f"https://api.mercadolibre.com/advertising/advertisers/{aid}/product_ads/campaigns",
            headers=h, timeout=15
        )
        if r.status_code != 200:
            print(f"  ✗ Listar campañas: [{r.status_code}] {r.text[:200]}")
            continue
        camps = r.json().get("results", [])
        print(f"  Campañas: {len(camps)}")
        for c in camps:
            print(f"    [{c['status']:8}] {c['name'][:40]} (id={c['id']}, items?)")

        if not camps:
            continue
        # Intentar PUT de items de la primera campaña activa (o cualquiera)
        active = [c for c in camps if c["status"] == "active"]
        if not active:
            active = camps[:1]
        cid = active[0]["id"]
        # Listar items
        r = requests.get(
            f"https://api.mercadolibre.com/advertising/advertisers/{aid}/product_ads/items",
            headers=h, params={"campaign_id": cid}, timeout=20
        )
        if r.status_code != 200:
            print(f"  ✗ Listar items camp {cid}: [{r.status_code}]")
            continue
        items = r.json().get("results", [])
        print(f"  Items en camp {cid}: {len(items)}")
        if not items:
            continue

        # Pick primer item ACTIVO con clicks=0 ó cost=0 (más seguro)
        safe = [it for it in items if it.get("status") == "active"]
        if not safe:
            safe = items
        target = safe[0]
        item_id = target["item_id"]
        current_status = target.get("status")
        print(f"  Item piloto: {item_id} ({target.get('title','')[:50]}) status={current_status}")

        # PUT idempotente: pedir el mismo status que ya tiene
        body = [{"item_id": item_id, "status": current_status}]
        r = requests.put(
            f"https://api.mercadolibre.com/advertising/advertisers/{aid}/product_ads/items",
            headers={**h, "Content-Type": "application/json"},
            json=body, timeout=20
        )
        print(f"  PUT idempotente: [{r.status_code}] {r.text[:300]}")


if __name__ == "__main__":
    main()
