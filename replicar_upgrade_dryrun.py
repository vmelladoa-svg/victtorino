"""
Dry-run del upgrade gold_special → gold_pro en los 13 perdedores.
Para cada uno:
  - GET /sites/MLC/listing_prices con price del item y category_id
    → obtiene fee % de cada tipo de listing
  - Calcula Δ costo por venta unitaria
  - Compara contra brecha de unidades del ganador (proxy upside)
  - Output: replicacion_upgrade_dryrun.xlsx

NO ejecuta el PUT — solo proyecta. La ejecución va en otro script.
"""
import json
from pathlib import Path
import pandas as pd
import requests
import time

ROOT = Path(__file__).parent
PLAN_FILE = ROOT / "plan_replicacion_top15.xlsx"
FICHAS = json.loads((ROOT / "data" / "auditoria" / "raw_fichas.json").read_text(encoding="utf-8"))
OUT = ROOT / "replicacion_upgrade_dryrun.xlsx"

TOK_C1 = json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"]
TOK_C2 = json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"]
TOK_C3 = json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"]
TOKENS = {"C1": TOK_C1, "C2": TOK_C2, "C3": TOK_C3}


def listing_prices(category_id, price, cuenta="C1"):
    h = {"Authorization": f"Bearer {TOKENS[cuenta]}"}
    r = requests.get(
        "https://api.mercadolibre.com/sites/MLC/listing_prices",
        params={"price": price, "category_id": category_id},
        headers=h, timeout=15,
    )
    if r.status_code != 200:
        return None
    return r.json()


def main():
    plan = pd.read_excel(PLAN_FILE)
    rows = []
    for _, p in plan.iterrows():
        lose_id = p["Lose_ID"]
        win_id = p["Win_ID"]
        lose_cuenta = p["Lose_Cuenta"]
        lose = FICHAS[lose_id]
        win = FICHAS[win_id]

        cat = lose["category_id"]
        price = lose["price"]
        win_lt = win["listing_type_id"]
        lose_lt = lose["listing_type_id"]

        # Solo procesar pares donde el upgrade tenga sentido
        needs_upgrade = (lose_lt == "gold_special" and win_lt == "gold_pro")

        prices = listing_prices(cat, price, cuenta=lose_cuenta)
        time.sleep(0.1)

        fees = {}
        if prices:
            for entry in prices:
                lt_id = entry.get("listing_type_id")
                fee_amount = entry.get("sale_fee_amount", 0)
                fee_pct = entry.get("sale_fee_details", {}).get("percentage_fee", None)
                fees[lt_id] = {"amount": fee_amount, "pct": fee_pct}

        gs_fee = fees.get("gold_special", {}).get("amount", None)
        gp_fee = fees.get("gold_pro", {}).get("amount", None)
        gs_pct = fees.get("gold_special", {}).get("pct", None)
        gp_pct = fees.get("gold_pro", {}).get("pct", None)
        delta_cost_unit = (gp_fee - gs_fee) if (gs_fee is not None and gp_fee is not None) else None

        # Upside: brecha de ventas, asumimos cerrar 50% de la brecha con el upgrade
        gap = p["Gap_Sales"]
        upside_unit = price * 0.5  # asumir 50% conversión de brecha = revenue por unidad
        upside_180d = gap * 0.5 * price

        # Costo extra 180d si cubrimos 50% de la brecha + ventas actuales
        ventas_180d_proyectadas = lose["sold_quantity"] + gap * 0.5
        extra_cost_180d = (delta_cost_unit or 0) * ventas_180d_proyectadas

        # Net 180d
        net_180d = upside_180d - extra_cost_180d

        rows.append({
            "#": len(rows)+1,
            "Producto": p["Producto"][:50],
            "Lose ItemID": lose_id,
            "Cuenta": lose_cuenta,
            "Cat ID": cat,
            "Precio CLP": price,
            "Win Listing": win_lt,
            "Lose Listing": lose_lt,
            "Needs Upgrade": needs_upgrade,
            "Fee gold_special CLP": gs_fee,
            "Fee gold_special %": gs_pct,
            "Fee gold_pro CLP": gp_fee,
            "Fee gold_pro %": gp_pct,
            "Δ Costo/unidad CLP": delta_cost_unit,
            "Brecha 180d (u)": gap,
            "Upside revenue 180d (50% brecha)": int(upside_180d),
            "Costo extra 180d CLP": int(extra_cost_180d) if delta_cost_unit else None,
            "Net 180d CLP": int(net_180d) if delta_cost_unit else None,
            "Permalink": p["Lose_Permalink"],
        })

    df = pd.DataFrame(rows)
    df.to_excel(OUT, index=False)
    print(f"OK {OUT}")
    print()
    print("=== Resumen ===")
    needs = df[df["Needs Upgrade"]]
    print(f"Pares que necesitan upgrade gold_special→gold_pro: {len(needs)} de {len(df)}")
    print(f"Upside revenue 180d (50% brecha cerrada): ${needs['Upside revenue 180d (50% brecha)'].sum():,}")
    extra_cost = needs["Costo extra 180d CLP"].dropna().sum()
    net = needs["Net 180d CLP"].dropna().sum()
    print(f"Costo extra comisiones 180d: ${int(extra_cost):,}")
    print(f"Neto proyectado 180d: ${int(net):,}")
    print()
    print("Detalle (ordenado por Net):")
    for _, r in needs.sort_values("Net 180d CLP", ascending=False).iterrows():
        print(f"  {r['Cuenta']} {r['Lose ItemID']} | {r['Producto'][:35]:35s} | "
              f"${r['Precio CLP']:>7,} | fee {r['Fee gold_special %']}→{r['Fee gold_pro %']} | "
              f"Δ${r['Δ Costo/unidad CLP'] or 0:>6,.0f}/u | "
              f"upside ${r['Upside revenue 180d (50% brecha)']:>8,} - extra "
              f"${int(r['Costo extra 180d CLP'] or 0):>6,} = net ${int(r['Net 180d CLP'] or 0):>8,}")


if __name__ == "__main__":
    main()
