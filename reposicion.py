import requests, json, sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL   = "https://api.mercadolibre.com"
DIAS       = 120
LEAD_TIME  = 15   # días desde pedido hasta recibir mercadería
META_DIAS  = 60   # días de cobertura objetivo tras reponer
ALERTA     = 30   # días de cobertura — umbral urgente
ADVERTENCIA = 45  # días de cobertura — umbral precaución

FECHA_DESDE = (datetime.now() - timedelta(days=DIAS)).strftime("%Y-%m-%dT00:00:00.000-00:00")
FECHA_HASTA = datetime.now().strftime("%Y-%m-%dT23:59:59.000-00:00")

CUENTAS = [
    ("Cuenta 1", "tokens_cuenta1.json"),
    ("Cuenta 2", "tokens_cuenta2.json"),
    ("Cuenta 3", "tokens_cuenta3.json"),
]

for nombre, archivo in CUENTAS:
    token   = json.loads(Path(archivo).read_text())["access_token"]
    H       = {"Authorization": f"Bearer {token}"}
    me      = requests.get(f"{BASE_URL}/users/me", headers=H).json()
    user_id = me["id"]
    nickname = me.get("nickname", "?")

    # 1. Ventas últimos 120 días
    ventas = defaultdict(lambda: {"titulo": "", "uds": 0})
    offset, total = 0, None
    while True:
        r = requests.get(f"{BASE_URL}/orders/search", headers=H, params={
            "seller": user_id, "order.status": "paid",
            "order.date_created.from": FECHA_DESDE,
            "order.date_created.to":   FECHA_HASTA,
            "offset": offset, "limit": 50,
        }).json()
        if total is None:
            total = r.get("paging", {}).get("total", 0)
        for order in r.get("results", []):
            for it in order.get("order_items", []):
                iid = it.get("item", {}).get("id", "")
                ventas[iid]["titulo"] = it.get("item", {}).get("title", "")
                ventas[iid]["uds"]   += it.get("quantity", 0)
        offset += 50
        if offset >= total:
            break

    # Top 10
    top10_ids = [iid for iid, _ in
                 sorted(ventas.items(), key=lambda x: x[1]["uds"], reverse=True)[:10]]

    # 2. Stock actual de los top 10
    stock_map = {}
    chunk = ",".join(top10_ids)
    items = requests.get(f"{BASE_URL}/items", headers=H, params={"ids": chunk}).json()
    for entry in items:
        if entry.get("code") == 200:
            b = entry["body"]
            stock_map[b["id"]] = b.get("available_quantity", 0)

    # 3. Análisis
    print(f"\n{'='*72}")
    print(f"  {nombre} — {nickname}  |  Lead time: {LEAD_TIME}d  |  Meta cobertura: {META_DIAS}d")
    print(f"{'='*72}")
    print(f"  {'#':>2}  {'Vel/día':>7}  {'Stock':>6}  {'Cobertura':>10}  {'Reponer?':>10}  {'Cuánto':>6}  Producto")
    print(f"  {'-'*68}")

    for rank, iid in enumerate(top10_ids, 1):
        d        = ventas[iid]
        stock    = stock_map.get(iid, 0)
        vel      = d["uds"] / DIAS          # unidades/día
        cobertura = (stock / vel) if vel > 0 else 9999
        # Punto de reposición: stock cubre lead_time + 50% buffer
        reorder_point = vel * LEAD_TIME * 1.5
        # Cantidad a pedir: llegar a META_DIAS de cobertura
        qty_pedir = max(0, round(vel * META_DIAS - stock))

        if cobertura <= ALERTA:
            urgencia = "URGENTE"
        elif cobertura <= ADVERTENCIA:
            urgencia = "PRONTO"
        elif stock <= reorder_point:
            urgencia = "REVISAR"
        else:
            urgencia = "OK"

        titulo_corto = d["titulo"][:38] + "…" if len(d["titulo"]) > 38 else d["titulo"]
        print(f"  {rank:>2}  {vel:>6.2f}/d  {stock:>6}  {cobertura:>8.0f}d  {urgencia:>10}  {qty_pedir:>6}  {titulo_corto}")

    print()
    print(f"  Leyenda urgencia:  URGENTE=cobertura≤{ALERTA}d | PRONTO=cobertura≤{ADVERTENCIA}d | OK=sin acción")
    print(f"  'Cuánto': unidades para alcanzar {META_DIAS}d de cobertura desde hoy")
