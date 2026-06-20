"""
Extiende el análisis ROI a todos los 31 pares C3→C1/C2 (no solo top 15).
Excluye los ya ejecutados en el primer batch.
Output: replicacion_upgrade_extra_dryrun.xlsx
"""
import json
import time
import re
from pathlib import Path
import pandas as pd
import pickle
import requests

ROOT = Path(__file__).parent
ANALISIS = ROOT / "data" / "auditoria" / "analisis.pkl"
PRIMER_DRYRUN = ROOT / "replicacion_upgrade_dryrun.xlsx"
OUT = ROOT / "replicacion_upgrade_extra_dryrun.xlsx"

TOK = {
    "C1": json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"],
    "C2": json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"],
    "C3": json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"],
}


def listing_prices(category_id, price, cuenta):
    h = {"Authorization": f"Bearer {TOK[cuenta]}"}
    r = requests.get(
        "https://api.mercadolibre.com/sites/MLC/listing_prices",
        params={"price": price, "category_id": category_id},
        headers=h, timeout=15,
    )
    return r.json() if r.status_code == 200 else None


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"].copy()
    df["NormTitle"] = df["Título"].apply(lambda t: re.sub(r"\s+", " ", (t or "").strip().lower()))

    # Reconstruir TODOS los pares C3 ganador → C1/C2
    pairs = []
    for t, g in df.groupby("NormTitle"):
        if g["Cuenta"].nunique() < 2:
            continue
        g = g.sort_values("Vendidos180d", ascending=False)
        c3_items = g[g["Cuenta"] == "C3"]
        if c3_items.empty:
            continue
        c3 = c3_items.iloc[0]
        if c3["Vendidos180d"] < g.iloc[0]["Vendidos180d"]:
            continue
        for _, l in g[(g["Cuenta"].isin(["C1", "C2"])) & (g["Vendidos180d"] < c3["Vendidos180d"])].iterrows():
            pairs.append({
                "Producto": t[:60],
                "Win_ID": c3["ItemID"], "Lose_ID": l["ItemID"], "Lose_Cuenta": l["Cuenta"],
                "Lose_Cat": l["Categoría"], "Lose_Precio": int(l["Precio"]),
                "Win_Sales": int(c3["Vendidos180d"]), "Lose_Sales": int(l["Vendidos180d"]),
                "Gap_Sales": int(c3["Vendidos180d"] - l["Vendidos180d"]),
                "Lose_Permalink": l["Permalink"],
            })
    pairs_df = pd.DataFrame(pairs).sort_values("Gap_Sales", ascending=False).reset_index(drop=True)
    print(f"Pares totales: {len(pairs_df)}")

    # Excluir los Lose_ID que ya están en el primer dry-run
    prev = pd.read_excel(PRIMER_DRYRUN)
    prev_ids = set(prev["Lose ItemID"].astype(str))
    extras = pairs_df[~pairs_df["Lose_ID"].astype(str).isin(prev_ids)].copy()
    print(f"Excluidos top15: {len(pairs_df) - len(extras)}")
    print(f"Extras a evaluar: {len(extras)}")

    # Para cada extra: GET item actual (verificar listing actual) + listing_prices
    rows = []
    for _, p in extras.iterrows():
        lid = p["Lose_ID"]
        cuenta = p["Lose_Cuenta"]
        # Estado actual
        h = {"Authorization": f"Bearer {TOK[cuenta]}"}
        r = requests.get(
            f"https://api.mercadolibre.com/items/{lid}",
            params={"attributes": "id,title,price,category_id,listing_type_id,status,available_quantity,sold_quantity"},
            headers=h, timeout=15,
        )
        if r.status_code != 200:
            continue
        it = r.json()
        lt = it.get("listing_type_id")
        if lt != "gold_special":
            # ya está en gold_pro u otro — skip
            rows.append({
                "Producto": p["Producto"][:50], "Cuenta": cuenta, "Lose ItemID": lid,
                "Cat": p["Lose_Cat"], "Precio CLP": p["Lose_Precio"],
                "Lose Listing": lt, "Needs Upgrade": False,
                "Gap_Sales": p["Gap_Sales"], "Reason": f"ya está en {lt}",
            })
            continue

        prices = listing_prices(p["Lose_Cat"], p["Lose_Precio"], cuenta=cuenta)
        time.sleep(0.1)
        fees = {}
        if prices:
            for entry in prices:
                fees[entry.get("listing_type_id")] = {
                    "amount": entry.get("sale_fee_amount", 0),
                    "pct": entry.get("sale_fee_details", {}).get("percentage_fee"),
                }
        gs_fee = fees.get("gold_special", {}).get("amount")
        gp_fee = fees.get("gold_pro", {}).get("amount")
        gs_pct = fees.get("gold_special", {}).get("pct")
        gp_pct = fees.get("gold_pro", {}).get("pct")
        delta = (gp_fee - gs_fee) if (gs_fee is not None and gp_fee is not None) else None

        gap = p["Gap_Sales"]
        upside_180d = gap * 0.5 * p["Lose_Precio"]
        proy_sales_180d = p["Lose_Sales"] + gap * 0.5
        extra_cost_180d = (delta or 0) * proy_sales_180d
        net_180d = upside_180d - extra_cost_180d

        rows.append({
            "Producto": p["Producto"][:50], "Cuenta": cuenta, "Lose ItemID": lid,
            "Cat": p["Lose_Cat"], "Precio CLP": p["Lose_Precio"],
            "Lose Listing": lt, "Needs Upgrade": True,
            "Win Sales 180d": p["Win_Sales"], "Lose Sales 180d": p["Lose_Sales"],
            "Gap_Sales": gap,
            "Fee gold_special CLP": gs_fee, "Fee gold_special %": gs_pct,
            "Fee gold_pro CLP": gp_fee, "Fee gold_pro %": gp_pct,
            "Δ Costo/u CLP": delta,
            "Upside revenue 180d (50%)": int(upside_180d),
            "Costo extra 180d CLP": int(extra_cost_180d) if delta else None,
            "Net 180d CLP": int(net_180d) if delta else None,
            "Permalink": p["Lose_Permalink"],
            "Reason": "",
        })
        time.sleep(0.05)

    df_out = pd.DataFrame(rows)
    df_out.to_excel(OUT, index=False)
    print(f"\nOK {OUT}")
    print()
    target = df_out[(df_out["Needs Upgrade"]) & (df_out["Net 180d CLP"].fillna(-1) > 0)]
    print(f"=== Extras con ROI+ ({len(target)} de {(df_out['Needs Upgrade']==True).sum()}) ===")
    for _, r in target.sort_values("Net 180d CLP", ascending=False).iterrows():
        print(f"  {r['Cuenta']} {r['Lose ItemID']} | {r['Producto'][:35]:35s} | "
              f"${r['Precio CLP']:>7,} | fee {r['Fee gold_special %']}→{r['Fee gold_pro %']} | "
              f"Δ${r['Δ Costo/u CLP'] or 0:>6,.0f}/u | gap {r['Gap_Sales']:2d} | "
              f"net ${int(r['Net 180d CLP'] or 0):>8,}")
    if len(target):
        print(f"\nNet 180d total proyectado del bloque extra: ${int(target['Net 180d CLP'].sum()):,}")
    neg = df_out[(df_out["Needs Upgrade"]) & (df_out["Net 180d CLP"].fillna(-1) <= 0)]
    print(f"\nExtras con ROI ≤0 (no se ejecutan): {len(neg)}")
    skip = df_out[df_out["Needs Upgrade"] == False]
    print(f"Skip (ya en gold_pro u otro): {len(skip)}")


if __name__ == "__main__":
    main()
