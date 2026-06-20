import requests, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://api.mercadolibre.com"

CUENTAS = [
    ("Cuenta 1", "tokens_cuenta1.json"),
    ("Cuenta 2", "tokens_cuenta2.json"),
    ("Cuenta 3", "tokens_cuenta3.json"),
]

STATUS_LABEL = {
    "active":       "Activa",
    "paused":       "Pausada",
    "closed":       "Cerrada",
    "under_review": "En revision",
    "inactive":     "Inactiva",
}

for nombre, archivo in CUENTAS:
    token = json.loads(Path(archivo).read_text())["access_token"]
    H = {"Authorization": f"Bearer {token}"}

    me = requests.get(f"{BASE_URL}/users/me", headers=H).json()
    user_id = me["id"]
    nickname = me.get("nickname", "?")

    ids = []
    offset = 0
    while True:
        r = requests.get(f"{BASE_URL}/users/{user_id}/items/search", headers=H,
                         params={"offset": offset, "limit": 50, "status": "active"}).json()
        ids.extend(r.get("results", []))
        offset += 50
        if offset >= r.get("paging", {}).get("total", 0):
            break

    print(f"\n{'='*65}")
    print(f"  {nombre} — {nickname} (ID: {user_id})")
    print(f"{'='*65}")

    activas = []
    for i in range(0, len(ids), 20):
        chunk = ",".join(ids[i:i+20])
        items = requests.get(f"{BASE_URL}/items", headers=H, params={"ids": chunk}).json()
        for entry in items:
            if entry.get("code") == 200:
                it = entry["body"]
                if it.get("status") == "active" and it.get("available_quantity", 0) > 0:
                    activas.append(it)

    activas.sort(key=lambda x: x.get("sold_quantity", 0), reverse=True)
    print(f"  Activas con stock: {len(activas)}")
    print()
    for it in activas:
        precio = f"${it.get('price', 0):,.0f}"
        print(f"  {it['id']} | Stock: {it.get('available_quantity',0):3} | Vendidos: {it.get('sold_quantity',0):4} | {precio} CLP")
        print(f"    {it.get('title','')}")
        print()
