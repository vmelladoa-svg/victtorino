"""
Rescata en vivo los atributos de TODAS las publicaciones activas de C3 (NOVAGRIFERIAS3)
y los guarda en atributos_c3_live.json para la sincronizacion de filtros con la web.
"""
import json, time, requests
from pathlib import Path

TOK = json.load(open(Path(__file__).parent / "tokens_cuenta3.json"))
H = {"Authorization": f"Bearer {TOK['access_token']}"}
UID = TOK["user_id"]
BASE = "https://api.mercadolibre.com"
OUT = Path(__file__).parent / "atributos_c3_live.json"

ATTRS = "id,title,status,category_id,price,available_quantity,seller_custom_field,attributes"


def all_active_ids():
    ids, scroll = [], None
    while True:
        params = {"search_type": "scan", "limit": 100, "status": "active"}
        if scroll:
            params["scroll_id"] = scroll
        r = requests.get(f"{BASE}/users/{UID}/items/search", headers=H, params=params)
        r.raise_for_status()
        d = r.json()
        batch = d.get("results", [])
        if not batch:
            break
        ids.extend(batch)
        scroll = d.get("scroll_id")
        if not scroll:
            break
        print(f"  ...{len(ids)} ids", end="\r")
    return ids


def fetch(ids):
    out = []
    for i in range(0, len(ids), 20):
        chunk = ids[i:i + 20]
        r = requests.get(f"{BASE}/items", headers=H,
                         params={"ids": ",".join(chunk), "attributes": ATTRS})
        if r.ok:
            for row in r.json():
                if row.get("code") == 200:
                    out.append(row["body"])
        print(f"  fetched {len(out)}/{len(ids)}", end="\r")
        time.sleep(0.12)
    return out


if __name__ == "__main__":
    print("Listando activos C3...")
    ids = all_active_ids()
    print(f"\nActivos: {len(ids)}")
    items = fetch(ids)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    con = sum(1 for it in items if it.get("attributes"))
    print(f"\nGuardados {len(items)} items ({con} con atributos) -> {OUT.name}")
