"""
Cobertura total: examinar TODOS los pares ganador → perdedor (no solo C3 ganador).
Genera replicacion_upgrade_global.xlsx con ROI por par para los perdedores en gold_special.
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
OUT = ROOT / "replicacion_upgrade_global.xlsx"

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


def get_item_status(cuenta, iid):
    h = {"Authorization": f"Bearer {TOK[cuenta]}"}
    r = requests.get(
        f"https://api.mercadolibre.com/items/{iid}",
        params={"attributes": "id,listing_type_id,status,price"},
        headers=h, timeout=15,
    )
    return r.json() if r.status_code == 200 else None


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"].copy()
    df["NormTitle"] = df["Título"].apply(lambda t: re.sub(r"\s+", " ", (t or "").strip().lower()))

    # Todos los pares ganador→perdedor (cualquier cuenta ganadora)
    pairs = []
    for t, g in df.groupby("NormTitle"):
        if g["Cuenta"].nunique() < 2:
            continue
        g = g.sort_values("Vendidos180d", ascending=False)
        if g.iloc[0]["Vendidos180d"] == 0:
            continue  # nadie vende, no hay ganador
        win = g.iloc[0]
        for _, l in g.iloc[1:].iterrows():
            if l["Vendidos180d"] >= win["Vendidos180d"]:
                continue
            pairs.append({
                "Producto": t[:60],
                "Win_Cuenta": win["Cuenta"], "Win_ID": win["ItemID"], "Win_Listing": win["ListingType"],
                "Win_Sales": int(win["Vendidos180d"]),
                "Lose_Cuenta": l["Cuenta"], "Lose_ID": l["ItemID"], "Lose_Listing": l["ListingType"],
                "Lose_Sales": int(l["Vendidos180d"]), "Lose_Cat": l["Categoría"],
                "Lose_Precio": int(l["Precio"]),
                "Gap_Sales": int(win["Vendidos180d"] - l["Vendidos180d"]),
                "Lose_Permalink": l["Permalink"],
            })
    pairs_df = pd.DataFrame(pairs).sort_values("Gap_Sales", ascending=False).reset_index(drop=True)
    print(f"Total pares (todas combinaciones): {len(pairs_df)}")

    # Excluir pares ya cubiertos en bloques anteriores (lose_id presente en logs upgrade_listing)
    import glob
    seen = set()
    for f in glob.glob(str(ROOT / "data" / "auditoria" / "upgrade_listing_*.json")):
        for x in json.load(open(f, encoding="utf-8")):
            seen.add(x["item"])
    print(f"Items ya procesados en bloques anteriores: {len(seen)}")
    pending = pairs_df[~pairs_df["Lose_ID"].isin(seen)].copy()
    print(f"Pares pendientes a evaluar: {len(pending)}")

    # Filtrar: solo donde ganador NO es C3 (los C3-ganador ya los hicimos en bloques 1+2)
    # Y donde el ganador esté en gold_pro (validando que el upgrade tiene sentido)
    candidates = pending[
        (pending["Win_Cuenta"] != "C3") &
        (pending["Win_Listing"] == "gold_pro") &
        (pending["Lose_Listing"] == "gold_special")
    ].copy()
    print(f"Candidatos (ganador C1/C2 en gold_pro + perdedor en gold_special): {len(candidates)}")

    # Verificar estado real y calcular ROI
    rows = []
    for _, p in candidates.iterrows():
        lid = p["Lose_ID"]
        cuenta = p["Lose_Cuenta"]
        it = get_item_status(cuenta, lid)
        time.sleep(0.1)
        if not it:
            continue
        if it.get("listing_type_id") != "gold_special":
            rows.append({**p.to_dict(), "Needs Upgrade": False, "Reason": f"actual {it.get('listing_type_id')}"})
            continue
        prices = listing_prices(p["Lose_Cat"], p["Lose_Precio"], cuenta)
        time.sleep(0.1)
        fees = {}
        if prices:
            for e in prices:
                fees[e.get("listing_type_id")] = {
                    "amount": e.get("sale_fee_amount", 0),
                    "pct": e.get("sale_fee_details", {}).get("percentage_fee"),
                }
        gs_fee = fees.get("gold_special", {}).get("amount")
        gp_fee = fees.get("gold_pro", {}).get("amount")
        gs_pct = fees.get("gold_special", {}).get("pct")
        gp_pct = fees.get("gold_pro", {}).get("pct")
        delta = (gp_fee - gs_fee) if (gs_fee is not None and gp_fee is not None) else None
        gap = p["Gap_Sales"]
        upside_180d = gap * 0.5 * p["Lose_Precio"]
        proy = p["Lose_Sales"] + gap * 0.5
        extra_cost = (delta or 0) * proy
        net = upside_180d - extra_cost
        rows.append({
            **p.to_dict(),
            "Needs Upgrade": True,
            "Fee gold_special CLP": gs_fee, "Fee gold_special %": gs_pct,
            "Fee gold_pro CLP": gp_fee, "Fee gold_pro %": gp_pct,
            "Δ Costo/u CLP": delta,
            "Upside revenue 180d (50%)": int(upside_180d),
            "Costo extra 180d CLP": int(extra_cost) if delta else None,
            "Net 180d CLP": int(net) if delta else None,
        })

    out = pd.DataFrame(rows)
    # Renombrar columnas para compatibilidad con ejecutor
    out = out.rename(columns={"Lose_ID": "Lose ItemID", "Lose_Cuenta": "Cuenta"})
    out.to_excel(OUT, index=False)
    print(f"\nOK {OUT}")

    target = out[(out["Needs Upgrade"]) & (out["Net 180d CLP"].fillna(-1) > 0)]
    neg = out[(out["Needs Upgrade"]) & (out["Net 180d CLP"].fillna(-1) <= 0)]
    print(f"\nROI+: {len(target)}, ROI≤0: {len(neg)}")
    for _, r in target.sort_values("Net 180d CLP", ascending=False).iterrows():
        print(f"  {r['Cuenta']} {r['Lose ItemID']} | {r['Producto'][:40]:40s} | "
              f"win {r['Win_Cuenta']} ({r['Win_Sales']}u) → lose ({r['Lose_Sales']}u) | "
              f"${r['Lose_Precio']:>7,} | net ${int(r['Net 180d CLP']):>8,}")
    if len(target):
        print(f"\nNet 180d total bloque global: ${int(target['Net 180d CLP'].sum()):,}")


if __name__ == "__main__":
    main()
