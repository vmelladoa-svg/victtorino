import requests, json, sys, re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL    = "https://api.mercadolibre.com"
DIAS        = 120
LEAD_TIME   = 7
META_DIAS   = 60
ALERTA      = 30
ADVERTENCIA = 45

FECHA_DESDE = (datetime.now() - timedelta(days=DIAS)).strftime("%Y-%m-%dT00:00:00.000-00:00")
FECHA_HASTA = datetime.now().strftime("%Y-%m-%dT23:59:59.000-00:00")

CUENTAS = [
    ("Cuenta 1", "tokens_cuenta1.json"),
    ("Cuenta 2", "tokens_cuenta2.json"),
    ("Cuenta 3", "tokens_cuenta3.json"),
]

STOPWORDS = {
    "de","del","la","el","los","las","y","o","con","para","al","en","un","una",
    "color","plateado","cromado","brillante","acabado","acero","inoxidable",
    "cm","mm","ml","lts","l","kg","g","x","//","–","-","+"
}

def normalizar(titulo):
    titulo = titulo.lower()
    titulo = re.sub(r"[^\w\s]", " ", titulo)
    tokens = [t for t in titulo.split() if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens[:6])

# ── 1. Recopilar ventas y stock por ítem en cada cuenta ──────────────
todos = {}   # iid -> {titulo, vel, stock, cuentas}

for nombre, archivo in CUENTAS:
    token   = json.loads(Path(archivo).read_text())["access_token"]
    H       = {"Authorization": f"Bearer {token}"}
    me      = requests.get(f"{BASE_URL}/users/me", headers=H).json()
    user_id = me["id"]
    print(f"Procesando {nombre} ({me.get('nickname')})...")

    # Ventas
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
        if offset >= (total or 0):
            break

    # Stock actual solo de ítems con ventas
    ids_con_ventas = list(ventas.keys())
    stock_map = {}
    for i in range(0, len(ids_con_ventas), 20):
        chunk = ",".join(ids_con_ventas[i:i+20])
        items = requests.get(f"{BASE_URL}/items", headers=H, params={"ids": chunk}).json()
        for entry in items:
            if entry.get("code") == 200:
                b = entry["body"]
                stock_map[b["id"]] = b.get("available_quantity", 0)

    for iid, d in ventas.items():
        if iid not in todos:
            todos[iid] = {"titulo": d["titulo"], "vel": 0, "stock": 0, "cuentas": []}
        todos[iid]["vel"]   += d["uds"] / DIAS
        todos[iid]["stock"] += stock_map.get(iid, 0)
        todos[iid]["cuentas"].append(nombre)

# ── 2. Agrupar por producto normalizado ──────────────────────────────
grupos = defaultdict(lambda: {"titulo": "", "vel": 0.0, "stock": 0, "ids": [], "cuentas": set()})

for iid, d in todos.items():
    clave = normalizar(d["titulo"])
    g = grupos[clave]
    if not g["titulo"] or len(d["titulo"]) < len(g["titulo"]):
        g["titulo"] = d["titulo"]
    g["vel"]    += d["vel"]
    g["stock"]  += d["stock"]
    g["ids"].append(iid)
    g["cuentas"].update(d["cuentas"])

# ── 3. Filtrar y ordenar por velocidad ───────────────────────────────
ranking = sorted(
    [(k, v) for k, v in grupos.items() if v["vel"] > 0],
    key=lambda x: x[1]["vel"],
    reverse=True
)

# ── 4. Imprimir análisis ─────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"  REPOSICIÓN GLOBAL — Inventario consolidado 3 cuentas")
print(f"  Periodo: últimos {DIAS} días | Lead time: {LEAD_TIME}d | Meta: {META_DIAS}d cobertura")
print(f"{'='*80}")
print(f"  {'Vel/d':>6}  {'Stock':>6}  {'Cob.':>7}  {'Estado':>10}  {'Pedir':>6}  Producto")
print(f"  {'-'*74}")

urgentes  = []
prontos   = []

for clave, g in ranking[:30]:
    vel      = g["vel"]
    stock    = g["stock"]
    cob      = (stock / vel) if vel > 0 else 9999
    qty      = max(0, round(vel * META_DIAS - stock))
    nc       = len(g["cuentas"])

    if cob <= ALERTA:
        estado = "URGENTE"
        urgentes.append((g["titulo"], stock, qty, vel, cob))
    elif cob <= ADVERTENCIA:
        estado = "PRONTO"
        prontos.append((g["titulo"], stock, qty, vel, cob))
    elif qty > 0:
        estado = "REVISAR"
    else:
        estado = "OK"

    titulo_c = g["titulo"][:42] + "…" if len(g["titulo"]) > 42 else g["titulo"]
    print(f"  {vel:>5.2f}/d  {stock:>6}  {cob:>6.0f}d  {estado:>10}  {qty:>6}  {titulo_c}")

print(f"\n{'='*80}")
print(f"  ACCIÓN INMEDIATA — URGENTE (cobertura ≤ {ALERTA} días)")
print(f"{'='*80}")
for t, s, q, v, c in urgentes:
    dias_hasta_cero = round(s / v) if v > 0 else 0
    fecha_cero = (datetime.now() + timedelta(days=dias_hasta_cero)).strftime("%d/%m/%Y")
    print(f"  Stock: {s:>3} uds | Se agota: {fecha_cero} | Pedir: {q:>3} uds | {t}")

if prontos:
    print(f"\n{'='*80}")
    print(f"  PRÓXIMAMENTE — PRONTO (cobertura {ALERTA+1}-{ADVERTENCIA} días)")
    print(f"{'='*80}")
    for t, s, q, v, c in prontos:
        fecha_rep = (datetime.now() + timedelta(days=max(0, round(s/v) - LEAD_TIME))).strftime("%d/%m/%Y")
        print(f"  Stock: {s:>3} uds | Pedir antes del: {fecha_rep} | Pedir: {q:>3} uds | {t}")
