"""
Auditoría Ads en las 3 cuentas. Maneja:
  - Cuenta sin advertiser → reporta vacío
  - Cuenta con campañas activas/pausadas → trae items + métricas
  - Genera Excel multi-cuenta para análisis comparativo
"""
import json
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).parent
DATE_TO = date.today().isoformat()
DATE_FROM = (date.today() - timedelta(days=7)).isoformat()
OUT = ROOT / f"auditoria_ads_3cuentas_{DATE_TO}.xlsx"

CUENTAS = [
    ("C1", "tokens_cuenta1.json"),
    ("C2", "tokens_cuenta2.json"),
    ("C3", "tokens_cuenta3.json"),
]


def get(token, url, params=None):
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=h, params=params or {}, timeout=20)
    return r


def audit_cuenta(cuenta, tok_file):
    print(f"\n=== {cuenta} ===")
    tok = json.loads((ROOT / tok_file).read_text())["access_token"]
    # Advertiser
    r = get(tok, "https://api.mercadolibre.com/advertising/advertisers", params={"product_id": "PADS"})
    if r.status_code != 200:
        return {"cuenta": cuenta, "error": f"advertisers HTTP {r.status_code}"}
    advs = r.json().get("advertisers", [])
    if not advs:
        return {"cuenta": cuenta, "error": "sin advertiser"}
    adv = advs[0]
    aid = adv["advertiser_id"]
    print(f"  Advertiser {aid} ({adv['advertiser_name']})")
    base = f"https://api.mercadolibre.com/advertising/advertisers/{aid}/product_ads"

    # Campañas
    r = get(tok, f"{base}/campaigns")
    if r.status_code != 200:
        return {"cuenta": cuenta, "advertiser_id": aid, "advertiser_name": adv["advertiser_name"],
                "error": f"campañas HTTP {r.status_code}", "campañas": []}
    camps = r.json().get("results", [])
    print(f"  Campañas: {len(camps)}")
    out_camps = []
    out_items = []
    for c in camps:
        cid = c["id"]
        print(f"    [{c['status']}] {c['name']}  budget=${int(c.get('budget',0)):,}")
        items = []
        if c["status"] == "active":
            # Solo items de la activa (las pausadas no generan métricas)
            offset = 0
            while True:
                r = get(tok, f"{base}/items", params={
                    "campaign_id": cid,
                    "metrics": "clicks,cost,direct_units_quantity,organic_units_quantity,sov",
                    "date_from": DATE_FROM, "date_to": DATE_TO,
                    "limit": 50, "offset": offset,
                })
                if r.status_code != 200:
                    print(f"      items HTTP {r.status_code}")
                    break
                d = r.json()
                items.extend(d["results"])
                offset += 50
                if offset >= d["paging"]["total"]: break
            print(f"      {len(items)} items")
        total_cost = total_rev = total_clicks = total_direct = 0
        for it in items:
            m = it.get("metrics", {})
            clk = m.get("clicks", 0) or 0
            cost = m.get("cost", 0) or 0
            direct = m.get("direct_units_quantity", 0) or 0
            organic = m.get("organic_units_quantity", 0) or 0
            sov = m.get("sov", 0) or 0
            precio = it.get("price", 0) or 0
            rev = direct * precio
            total_cost += cost; total_rev += rev; total_clicks += clk; total_direct += direct
            out_items.append({
                "Cuenta": cuenta, "Campaña": c["name"], "Campaign ID": cid,
                "Item ID": it.get("item_id"),
                "Título": (it.get("title") or "")[:60],
                "Precio": int(precio), "Listing": it.get("listing_type_id"),
                "Marca": it.get("brand_value_name"),
                "Clicks 7d": clk, "Cost 7d CLP": int(cost),
                "CPC": int(cost/clk) if clk else 0,
                "Ventas directas": direct, "Ventas orgánicas": organic,
                "Revenue directo CLP": int(rev),
                "ROAS": round(rev/cost, 2) if cost else 0,
                "ACOS %": round(cost/rev*100, 2) if rev else 0,
                "SOV %": round(sov, 2),
                "Buy Box": "✓" if it.get("buy_box_winner") else "—",
            })
        out_camps.append({
            "Cuenta": cuenta, "Campaña": c["name"], "ID": cid, "Status": c["status"],
            "Estrategia": c.get("strategy"),
            "Budget CLP/día": int(c.get("budget", 0)),
            "ACOS target %": c.get("acos_target"), "ROAS target": c.get("roas_target"),
            "Items": len(items),
            "Items con clicks 7d": sum(1 for x in out_items if x["Campaign ID"]==cid and x["Clicks 7d"]>0),
            "Items con ventas 7d": sum(1 for x in out_items if x["Campaign ID"]==cid and x["Ventas directas"]>0),
            "Clicks 7d": total_clicks, "Cost 7d CLP": int(total_cost),
            "Ventas directas 7d": total_direct, "Revenue directo 7d CLP": int(total_rev),
            "ROAS real": round(total_rev/total_cost, 2) if total_cost else 0,
            "ACOS real %": round(total_cost/total_rev*100, 2) if total_rev else 0,
            "Creada": c.get("date_created", "")[:10],
            "Última act.": c.get("last_updated", "")[:10],
        })
    return {"cuenta": cuenta, "advertiser_id": aid, "advertiser_name": adv["advertiser_name"],
            "campañas": out_camps, "items": out_items}


def main():
    all_camps = []
    all_items = []
    resumen_cuentas = []
    for cuenta, tf in CUENTAS:
        res = audit_cuenta(cuenta, tf)
        if "error" in res:
            resumen_cuentas.append({"Cuenta": cuenta, "Advertiser": res.get("advertiser_name", "—"),
                                    "Estado": res["error"], "Campañas": 0, "Items": 0,
                                    "Cost 7d": 0, "Revenue 7d": 0, "ROAS": 0})
            continue
        all_camps.extend(res["campañas"])
        all_items.extend(res["items"])
        # Agregado por cuenta
        active_camps = [c for c in res["campañas"] if c["Status"] == "active"]
        total_cost = sum(c["Cost 7d CLP"] for c in active_camps)
        total_rev = sum(c["Revenue directo 7d CLP"] for c in active_camps)
        resumen_cuentas.append({
            "Cuenta": cuenta,
            "Advertiser": res.get("advertiser_name"),
            "Advertiser ID": res["advertiser_id"],
            "Estado": "OK",
            "Campañas total": len(res["campañas"]),
            "Activas": len(active_camps),
            "Pausadas": sum(1 for c in res["campañas"] if c["Status"] == "paused"),
            "Items con métricas": len(res["items"]),
            "Cost 7d CLP": total_cost,
            "Revenue 7d CLP": total_rev,
            "ROAS real": round(total_rev/total_cost, 2) if total_cost else 0,
            "ACOS real %": round(total_cost/total_rev*100, 2) if total_rev else 0,
            "Budget total CLP/día": sum(c["Budget CLP/día"] for c in active_camps),
        })

    df_resumen = pd.DataFrame(resumen_cuentas)
    df_camps = pd.DataFrame(all_camps)
    df_items = pd.DataFrame(all_items)

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        df_resumen.to_excel(writer, sheet_name="1. Resumen 3 cuentas", index=False)
        df_camps.to_excel(writer, sheet_name="2. Campañas detalle", index=False)
        if not df_items.empty:
            df_items.sort_values(["Cuenta", "Cost 7d CLP"], ascending=[True, False]).to_excel(
                writer, sheet_name="3. Items todos", index=False)
            # Top performers
            top = df_items[df_items["Ventas directas"] > 0].sort_values("ROAS", ascending=False)
            top.to_excel(writer, sheet_name="4. Top performers", index=False)
            # Sin venta gastando
            sin_v = df_items[(df_items["Clicks 7d"] >= 3) & (df_items["Ventas directas"] == 0)]
            sin_v.sort_values("Cost 7d CLP", ascending=False).to_excel(writer, sheet_name="5. Clicks sin venta", index=False)
            # Sin clicks
            df_items[df_items["Clicks 7d"] == 0].to_excel(writer, sheet_name="6. Sin clicks 7d", index=False)

    print(f"\nOK Excel: {OUT}")
    print("\n=== Resumen ===")
    print(df_resumen.to_string(index=False))


if __name__ == "__main__":
    main()
