"""
Análisis consolidado de los 3 snapshots ML — produce dataframes con KPIs,
health score, issues y prioridades. Lo consume el script de reporting.

Salida en memoria + opcional pickle en data/auditoria/analisis.pkl.
"""
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
SNAP_DIR = ROOT / "data" / "auditoria"

CUENTAS = [
    ("C1", "PREMIUMGRIFERIAS1", SNAP_DIR / "snapshot_c1.json"),
    ("C2", "VICTTORINOOFICIAL2", SNAP_DIR / "snapshot_c2.json"),
    ("C3", "NOVAGRIFERIAS3",    SNAP_DIR / "snapshot_c3.json"),
]

# Datos Defontana (muestra)
INV_PATH = ROOT / "data" / "excel" / "inventario.xlsx"
FIN_PATH = ROOT / "data" / "excel" / "finanzas.xlsx"


def load_defontana():
    """Carga muestra Defontana (16 SKUs) para cruce de costos."""
    margenes = pd.read_excel(FIN_PATH, sheet_name="Margenes_SKU")
    margenes = margenes[["SKU","Descripción","Precio_Venta","Costo","Margen_%","Comisión_ML_%","Margen_Neto_ML"]]
    stock = pd.read_excel(INV_PATH, sheet_name="Stock_Actual")
    stock = stock[["SKU","Stock_Actual","Stock_Mínimo","Stock_Estado","Días_Stock_Estimado"]]
    return margenes, stock


def health_score(item, pics_count, visits, sold_180d):
    """
    Score 0-100 sobre completitud y performance:
    - fotos (0-20): >=6 full, 4-5 medio, <=3 cero
    - listing type (0-10): gold_pro > gold_special > free
    - título (0-15): >40 chars
    - precio cero / coherencia (0-5): excluye base_price<=0
    - visibilidad 30d (0-20): >100 full, 20-100 medio, 1-19 medio bajo, 0 cero
    - conversion 30d (0-20): proxy ventas/visitas >2% full, 0% cero
    - reputación item ML (0-10): si health field >0.8 full
    """
    s = 0
    if pics_count >= 6: s += 20
    elif pics_count >= 4: s += 12
    elif pics_count >= 2: s += 6

    lt = item.get("listing_type_id") or ""
    if lt == "gold_pro": s += 10
    elif lt == "gold_special": s += 6

    title = item.get("title") or ""
    if len(title) >= 50: s += 15
    elif len(title) >= 40: s += 10
    elif len(title) >= 30: s += 5

    if (item.get("price") or 0) > 0: s += 5

    if visits >= 100: s += 20
    elif visits >= 20: s += 14
    elif visits >= 5: s += 8
    elif visits >= 1: s += 3

    conv = (sold_180d / visits * 100) if visits > 0 else 0
    if conv >= 5: s += 20
    elif conv >= 2: s += 14
    elif conv >= 1: s += 8
    elif sold_180d > 0: s += 4

    h = item.get("health")
    if h is not None and h >= 0.8: s += 10
    elif h is not None and h >= 0.5: s += 5

    return min(s, 100)


def detect_issues(item, pics, stock, visits, sold_180d, lt):
    issues = []
    if (item.get("available_quantity") or 0) == 0:
        issues.append(("CRITICO","Sin stock","Pausar o reabastecer"))
    elif (item.get("available_quantity") or 0) < 3:
        issues.append(("MEDIO",f"Stock bajo ({item.get('available_quantity')} u)","Reabastecer"))

    if pics < 4:
        issues.append(("ALTO",f"Pocas fotos ({pics})","Subir hasta 6+ fotos"))

    title = item.get("title") or ""
    if len(title) < 40:
        issues.append(("MEDIO",f"Título corto ({len(title)} chars)","Reescribir para SEO ML"))
    if len(title) > 60:
        issues.append(("BAJO",f"Título demasiado largo ({len(title)} chars)","Recortar a 60 chars"))

    if lt == "free":
        issues.append(("ALTO","Listing Free","Migrar a Gold Pro/Special"))

    if visits == 0:
        issues.append(("ALTO","0 visitas 30d","Optimizar SEO, fotos, precio"))
    elif visits > 50 and sold_180d == 0:
        issues.append(("CRITICO",f"Alta visibilidad ({visits} visitas) 0 ventas",
                       "Revisar precio/ficha/competencia"))
    elif visits > 100 and sold_180d > 0:
        conv = sold_180d/visits*100
        if conv < 1:
            issues.append(("ALTO",f"Conv {conv:.2f}% baja con {visits} visitas",
                           "Revisar precio, ofertas, descripción"))

    if (item.get("price") or 0) <= 0:
        issues.append(("CRITICO","Precio cero o nulo","Revisar precio urgente"))

    return issues


def severidad_score(issues):
    """Mapeo severidad → número para ordenar."""
    weights = {"CRITICO":4,"ALTO":3,"MEDIO":2,"BAJO":1}
    return sum(weights.get(i[0],0) for i in issues)


def build_publicaciones_df(cuenta, snap):
    """DataFrame de publicaciones activas con KPIs e issues."""
    visits_map = snap.get("visitas_30d") or {}
    # Ventas 180d por item
    sold_180d = defaultdict(int)
    revenue_180d = defaultdict(float)
    for o in snap.get("orders", []):
        if o.get("status") != "paid": pass  # contamos todas las completadas también
        for oi in o.get("order_items", []):
            iid = (oi.get("item") or {}).get("id")
            if not iid: continue
            qty = oi.get("quantity") or 0
            unit = oi.get("unit_price") or 0
            sold_180d[iid] += qty
            revenue_180d[iid] += qty * unit

    rows = []
    for it in snap.get("items", []):
        if it.get("status") != "active": continue
        iid = it["id"]
        pics = len(it.get("pictures") or [])
        v = visits_map.get(iid, 0) or 0
        sold = sold_180d.get(iid, 0)
        rev = revenue_180d.get(iid, 0)
        lt = it.get("listing_type_id") or ""
        conv = (sold/v*100) if v>0 else 0
        hs = health_score(it, pics, v, sold)
        issues = detect_issues(it, pics, it.get("available_quantity",0), v, sold, lt)
        sev = severidad_score(issues)
        sku = it.get("seller_custom_field") or ""
        rows.append({
            "Cuenta": cuenta,
            "ItemID": iid,
            "SKU": sku,
            "Título": it.get("title"),
            "Categoría": it.get("category_id"),
            "Precio": it.get("price"),
            "PrecioBase": it.get("base_price"),
            "Stock": it.get("available_quantity"),
            "ListingType": lt,
            "Fotos": pics,
            "Visitas30d": v,
            "Vendidos180d": sold,
            "Revenue180d": int(rev),
            "ConvRate%": round(conv,2),
            "HealthCalc": hs,
            "HealthML": it.get("health"),
            "Severidad": sev,
            "NumIssues": len(issues),
            "Issues": " | ".join(f"[{s}] {m}" for s,m,_ in issues),
            "Acciones": " | ".join(a for _,_,a in issues),
            "Permalink": it.get("permalink"),
            "FechaInicio": (it.get("start_time") or "")[:10],
        })
    return pd.DataFrame(rows)


def build_resumen_cuenta(cuenta, alias, snap, df_pub):
    activas = df_pub.shape[0]
    visitas = int(df_pub["Visitas30d"].sum())
    items_con_trafico = int((df_pub["Visitas30d"]>0).sum())
    vendidos = int(df_pub["Vendidos180d"].sum())
    revenue = int(df_pub["Revenue180d"].sum())
    orders = len(snap.get("orders",[]))
    gmv = sum((o.get("total_amount") or 0) for o in snap.get("orders",[]))
    aov = (gmv/orders) if orders>0 else 0
    conv_global = (vendidos/visitas*100) if visitas>0 else 0
    health_avg = round(df_pub["HealthCalc"].mean(),1) if activas else 0
    rep = snap.get("reputacion") or {}
    metrics = rep.get("metrics") or {}
    tx = rep.get("transactions") or {}
    qs = snap.get("preguntas") or {}
    return {
        "Cuenta": cuenta,
        "Alias": alias,
        "UserID": rep.get("user_id"),
        "Activas": activas,
        "Visitas30d": visitas,
        "ItemsConTrafico": items_con_trafico,
        "Ordenes180d": orders,
        "GMV180d": int(gmv),
        "TicketProm": int(aov),
        "Vendidos180d (unidades en items vivos)": vendidos,
        "RevenueItemsVivos180d": revenue,
        "ConvGlobal%": round(conv_global,2),
        "HealthAvg": health_avg,
        "ListingsGoldPro": int((df_pub["ListingType"]=="gold_pro").sum()),
        "ListingsGoldSpecial": int((df_pub["ListingType"]=="gold_special").sum()),
        "ListingsFree": int((df_pub["ListingType"]=="free").sum()),
        "FotosMenos4": int((df_pub["Fotos"]<4).sum()),
        "TitulosCortos<40": int((df_pub["Título"].str.len()<40).sum()),
        "SinStock": int((df_pub["Stock"]==0).sum()),
        "StockCritico<3": int(((df_pub["Stock"]>0)&(df_pub["Stock"]<3)).sum()),
        "RepNivel": rep.get("level_id"),
        "PowerSeller": rep.get("power_seller_status"),
        "TxCompletadas": tx.get("completed"),
        "TxCanceladas": tx.get("canceled"),
        "PreguntasResp180d": qs.get("answered_180d"),
        "PreguntasPendientes": qs.get("unanswered_now"),
        "MetricaClaimsRate%": (metrics.get("claims") or {}).get("rate"),
        "MetricaCancRate%": (metrics.get("cancellations") or {}).get("rate"),
        "MetricaDelayedRate%": (metrics.get("delayed_handling_time") or {}).get("rate"),
    }


def cruzar_defontana(df_pub, margenes, stock_def):
    """
    Cruza SKU del item con Defontana. Solo aplica a publicaciones cuyo
    seller_custom_field coincide con un SKU del set Defontana (limitado a muestra).
    """
    m = df_pub.merge(margenes, on="SKU", how="left", suffixes=("","_def"))
    m = m.merge(stock_def, on="SKU", how="left")
    # margen unitario aplicado al revenue 180d
    m["MargenNetoUnit"] = m["Margen_Neto_ML"]
    m["MargenTotal180d"] = (m["Vendidos180d"].fillna(0) * m["MargenNetoUnit"].fillna(0)).astype("Int64")
    return m


def run():
    print("Cargando Defontana...")
    margenes, stock_def = load_defontana()
    print(f"  Defontana: {len(margenes)} SKUs con costos, {len(stock_def)} en inventario")

    all_pub = []
    resumen = []
    snapshots = {}
    for cuenta, alias, p in CUENTAS:
        snap = json.loads(p.read_text(encoding="utf-8"))
        snapshots[cuenta] = snap
        df_pub = build_publicaciones_df(cuenta, snap)
        all_pub.append(df_pub)
        r = build_resumen_cuenta(cuenta, alias, snap, df_pub)
        resumen.append(r)
        print(f"  {cuenta}: {len(df_pub)} activas, health avg {r['HealthAvg']}, visitas {r['Visitas30d']}, ordenes {r['Ordenes180d']}")

    df_pub_all = pd.concat(all_pub, ignore_index=True)
    df_pub_all_def = cruzar_defontana(df_pub_all, margenes, stock_def)
    df_res = pd.DataFrame(resumen)

    out = {
        "snapshots": snapshots,
        "df_publicaciones": df_pub_all_def,
        "df_resumen": df_res,
        "df_defontana_margenes": margenes,
        "df_defontana_stock": stock_def,
    }
    # Pickle para reuso
    import pickle
    (SNAP_DIR / "analisis.pkl").write_bytes(pickle.dumps(out))
    print(f"\nAnálisis guardado: {SNAP_DIR / 'analisis.pkl'}")
    return out


if __name__ == "__main__":
    run()
