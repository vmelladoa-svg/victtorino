"""
Auditoría completa de Mercado Ads C3 (advertiser 79197).
Trae todas las campañas + 154 items de la campaña activa con métricas reales
(clicks, cost, ventas directas/orgánicas, SOV) y genera Excel ranqueado por ROAS.
"""
import json
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).parent
TOK = json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"]
H = {"Authorization": f"Bearer {TOK}"}
AID = 79197
BASE = f"https://api.mercadolibre.com/advertising/advertisers/{AID}/product_ads"

# Período: últimos 7 días (calibrable)
DATE_TO = date.today().isoformat()
DATE_FROM = (date.today() - timedelta(days=7)).isoformat()

OUT = ROOT / f"auditoria_ads_c3_{DATE_TO}.xlsx"


def fetch_campaigns():
    r = requests.get(f"{BASE}/campaigns", headers=H, timeout=20)
    return r.json()["results"]


def fetch_items(cid):
    all_items = []
    offset = 0
    while True:
        r = requests.get(f"{BASE}/items", headers=H, params={
            "campaign_id": cid,
            "metrics": "clicks,cost,direct_units_quantity,organic_units_quantity,sov",
            "date_from": DATE_FROM, "date_to": DATE_TO,
            "limit": 50, "offset": offset,
        }, timeout=30)
        if r.status_code != 200:
            print(f"  ERROR {r.status_code}: {r.text[:300]}")
            break
        d = r.json()
        all_items.extend(d["results"])
        total = d["paging"]["total"]
        offset += 50
        if offset >= total: break
    return all_items


def main():
    print(f"Auditoría Ads C3 · período {DATE_FROM} → {DATE_TO}\n")
    campaigns = fetch_campaigns()
    print(f"Campañas: {len(campaigns)}")
    rows_camp = []
    rows_items = []

    for c in campaigns:
        print(f"\n─── {c['name']} (id={c['id']}, status={c['status']}) ───")
        items = fetch_items(c["id"])
        print(f"  Items: {len(items)}")
        # Agregados
        total_clicks = 0; total_cost = 0; total_direct = 0; total_organic = 0; total_revenue_direct = 0
        for it in items:
            m = it.get("metrics", {})
            clicks = m.get("clicks", 0) or 0
            cost = m.get("cost", 0) or 0
            direct = m.get("direct_units_quantity", 0) or 0
            organic = m.get("organic_units_quantity", 0) or 0
            sov = m.get("sov", 0) or 0
            precio = it.get("price", 0) or 0
            rev_direct = direct * precio
            total_clicks += clicks; total_cost += cost; total_direct += direct
            total_organic += organic; total_revenue_direct += rev_direct
            rows_items.append({
                "Campaña": c["name"], "Campaign ID": c["id"],
                "Item ID": it.get("item_id"),
                "Título": (it.get("title") or "")[:60],
                "Precio": int(precio),
                "Listing": it.get("listing_type_id"),
                "Catalog?": "Sí" if it.get("catalog_listing") else "No",
                "Buy Box": "✓" if it.get("buy_box_winner") else "—",
                "Nivel": it.get("current_level"),
                "Marca": it.get("brand_value_name"),
                "Clicks 7d": clicks,
                "Cost 7d CLP": int(cost),
                "CPC promedio": int(cost / clicks) if clicks else 0,
                "Ventas directas (atribuidas)": direct,
                "Ventas orgánicas": organic,
                "Revenue directo CLP": int(rev_direct),
                "ROAS (rev/cost)": round(rev_direct / cost, 2) if cost else 0,
                "ACOS %": round(cost / rev_direct * 100, 2) if rev_direct else 0,
                "SOV %": round(sov, 2),
                "Status": it.get("status"),
                "Permalink": it.get("permalink"),
            })
        # Resumen campaña
        roas_camp = total_revenue_direct / total_cost if total_cost else 0
        acos_camp = total_cost / total_revenue_direct * 100 if total_revenue_direct else 0
        rows_camp.append({
            "Campaña": c["name"], "ID": c["id"], "Status": c["status"],
            "Estrategia": c.get("strategy"),
            "Presupuesto CLP/día": int(c.get("budget", 0)),
            "ACOS target %": c.get("acos_target"),
            "ROAS target": c.get("roas_target"),
            "Items totales": len(items),
            "Items con clicks 7d": sum(1 for r in rows_items if r["Campaign ID"]==c["id"] and r["Clicks 7d"]>0),
            "Items con ventas directas 7d": sum(1 for r in rows_items if r["Campaign ID"]==c["id"] and r["Ventas directas (atribuidas)"]>0),
            "Clicks totales 7d": total_clicks,
            "Cost total 7d CLP": int(total_cost),
            "Ventas directas 7d": total_direct,
            "Ventas orgánicas 7d": total_organic,
            "Revenue directo 7d CLP": int(total_revenue_direct),
            "ROAS campaña": round(roas_camp, 2),
            "ACOS campaña %": round(acos_camp, 2),
            "Created": c.get("date_created", "")[:10],
            "Last updated": c.get("last_updated", "")[:10],
        })
        print(f"  Clicks: {total_clicks} | Cost: ${int(total_cost):,} | Ventas directas: {total_direct} | Revenue directo: ${int(total_revenue_direct):,}")
        print(f"  ROAS: {roas_camp:.2f}x (target {c.get('roas_target')}x) | ACOS: {acos_camp:.1f}% (target {c.get('acos_target')}%)")

    # Excel
    df_camp = pd.DataFrame(rows_camp)
    df_items = pd.DataFrame(rows_items)

    # Top y bottom rankings
    activas = df_items[df_items["Cost 7d CLP"] > 0].copy()
    top_roas = activas.sort_values("ROAS (rev/cost)", ascending=False).head(20)
    bottom_roas = activas.sort_values("ROAS (rev/cost)", ascending=True).head(20)
    sin_clicks = df_items[df_items["Clicks 7d"] == 0]
    con_clicks_sin_venta = activas[(activas["Clicks 7d"] >= 5) & (activas["Ventas directas (atribuidas)"] == 0)]

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        df_camp.to_excel(writer, sheet_name="1. Campañas", index=False)
        df_items.sort_values("Cost 7d CLP", ascending=False).to_excel(writer, sheet_name="2. Items (por gasto)", index=False)
        top_roas.to_excel(writer, sheet_name="3. Top 20 ROAS", index=False)
        bottom_roas.to_excel(writer, sheet_name="4. Bottom 20 ROAS (revisar)", index=False)
        con_clicks_sin_venta.sort_values("Cost 7d CLP", ascending=False).to_excel(writer, sheet_name="5. Con clicks sin venta", index=False)
        sin_clicks.to_excel(writer, sheet_name="6. Sin clicks 7d", index=False)
    print(f"\n=== Excel: {OUT} ===")
    print(f"Items totales: {len(df_items)}")
    print(f"  Con clicks 7d: {(df_items['Clicks 7d']>0).sum()}")
    print(f"  Con ventas directas: {(df_items['Ventas directas (atribuidas)']>0).sum()}")
    print(f"  Cost total 7d: ${df_items['Cost 7d CLP'].sum():,}")
    print(f"  Revenue directo 7d: ${df_items['Revenue directo CLP'].sum():,}")
    if df_items['Cost 7d CLP'].sum() > 0:
        roas_global = df_items['Revenue directo CLP'].sum() / df_items['Cost 7d CLP'].sum()
        print(f"  ROAS global: {roas_global:.2f}x")


if __name__ == "__main__":
    main()
