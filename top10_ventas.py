import requests, json, sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://api.mercadolibre.com"
DIAS = 120
FECHA_DESDE = (datetime.now() - timedelta(days=DIAS)).strftime("%Y-%m-%dT00:00:00.000-00:00")
FECHA_HASTA = datetime.now().strftime("%Y-%m-%dT23:59:59.000-00:00")

CUENTAS = [
    ("Cuenta 1", "tokens_cuenta1.json"),
    ("Cuenta 2", "tokens_cuenta2.json"),
    ("Cuenta 3", "tokens_cuenta3.json"),
]

for nombre, archivo in CUENTAS:
    token = json.loads(Path(archivo).read_text())["access_token"]
    H = {"Authorization": f"Bearer {token}"}

    me = requests.get(f"{BASE_URL}/users/me", headers=H).json()
    user_id = me["id"]
    nickname = me.get("nickname", "?")

    # Recopilar todas las órdenes pagadas de los últimos 120 días
    ventas = defaultdict(lambda: {"titulo": "", "unidades": 0, "ingresos": 0})
    offset = 0
    total = None

    while True:
        r = requests.get(f"{BASE_URL}/orders/search", headers=H, params={
            "seller": user_id,
            "order.status": "paid",
            "order.date_created.from": FECHA_DESDE,
            "order.date_created.to":   FECHA_HASTA,
            "offset": offset,
            "limit":  50,
        }).json()

        if total is None:
            total = r.get("paging", {}).get("total", 0)

        for order in r.get("results", []):
            for item in order.get("order_items", []):
                iid   = item.get("item", {}).get("id", "")
                title = item.get("item", {}).get("title", "")
                qty   = item.get("quantity", 0)
                price = item.get("unit_price", 0)
                ventas[iid]["titulo"]   = title
                ventas[iid]["unidades"] += qty
                ventas[iid]["ingresos"] += qty * price

        offset += 50
        if offset >= total:
            break

    # Top 10 por unidades
    top10 = sorted(ventas.items(), key=lambda x: x[1]["unidades"], reverse=True)[:10]

    print(f"\n{'='*65}")
    print(f"  {nombre} — {nickname}  |  Últimos {DIAS} días  |  {total} órdenes")
    print(f"{'='*65}")
    for rank, (iid, d) in enumerate(top10, 1):
        print(f"  {rank:2}. {d['unidades']:4} uds | ${d['ingresos']:>12,.0f} CLP | {iid}")
        print(f"      {d['titulo']}")
        print()
