"""
Toma los 29 items del SEO enriched marcados 'Upgrade a gold_pro' (caso replicación pendiente),
verifica estado actual via API, calcula ROI (acá la gap_sales = 0 porque el hermano no vende
pero sí tiene visitas; usamos visitas como proxy de upside).

Dry-run + execute opcional.
"""
import json
import time
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).parent
IN_XLSX = ROOT / "analisis_seo_sin_visitas_enriched.xlsx"
OUT_XLSX = ROOT / "seo_upgrade_extras_dryrun.xlsx"

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


def get_item(cuenta, iid):
    h = {"Authorization": f"Bearer {TOK[cuenta]}"}
    r = requests.get(
        f"https://api.mercadolibre.com/items/{iid}",
        params={"attributes": "id,listing_type_id,status,price"},
        headers=h, timeout=15,
    )
    return r.json() if r.status_code == 200 else None


def upgrade_item(cuenta, iid):
    h = {"Authorization": f"Bearer {TOK[cuenta]}", "Content-Type": "application/json"}
    r = requests.post(
        f"https://api.mercadolibre.com/items/{iid}/listing_type",
        json={"id": "gold_pro"}, headers=h, timeout=20,
    )
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text[:300]


def main(execute=False):
    df = pd.read_excel(IN_XLSX)
    cand = df[df["Acción recomendada"] == "Upgrade a gold_pro (caso replicación pendiente)"].copy()
    print(f"Candidatos detectados por SEO: {len(cand)}")

    # Excluir los ya procesados
    import glob
    seen = set()
    for f in glob.glob(str(ROOT / "data" / "auditoria" / "upgrade_listing_*.json")):
        for x in json.load(open(f, encoding="utf-8")):
            seen.add(x["item"])
    pending = cand[~cand["ItemID"].isin(seen)].copy()
    print(f"Pendientes (no procesados antes): {len(pending)}")

    rows = []
    for _, p in pending.iterrows():
        iid = p["ItemID"]
        cuenta = p["Cuenta"]
        it = get_item(cuenta, iid)
        time.sleep(0.1)
        if not it:
            rows.append({**p.to_dict(), "Estado actual": "ERROR_GET", "Net 180d CLP": None})
            continue
        cur_lt = it.get("listing_type_id")
        if cur_lt != "gold_special":
            rows.append({**p.to_dict(), "Estado actual": cur_lt, "Net 180d CLP": None})
            continue

        # ROI: upside = visitas del hermano * conv 3% promedio * precio
        hermano_visits = float(p["Hermano Visitas 30d"] or 0)
        precio = float(p["Precio"])
        # Asumir que si nuestro item logra el mismo tráfico que el hermano, vende a conv 3%
        sales_proy_30d = hermano_visits * 0.03
        sales_proy_180d = sales_proy_30d * 6
        upside = sales_proy_180d * precio

        prices = listing_prices(p["Categoría"], precio, cuenta)
        time.sleep(0.05)
        fees = {}
        if prices:
            for e in prices:
                fees[e.get("listing_type_id")] = {"amount": e.get("sale_fee_amount", 0),
                                                  "pct": e.get("sale_fee_details", {}).get("percentage_fee")}
        gs_fee = fees.get("gold_special", {}).get("amount")
        gp_fee = fees.get("gold_pro", {}).get("amount")
        delta = (gp_fee - gs_fee) if (gs_fee is not None and gp_fee is not None) else None
        extra = (delta or 0) * sales_proy_180d
        net = upside - extra
        rows.append({
            **p.to_dict(),
            "Estado actual": cur_lt,
            "Hermano visitas 30d (num)": hermano_visits,
            "Ventas proy 180d": round(sales_proy_180d, 2),
            "Upside revenue 180d": int(upside),
            "Δ Fee/u CLP": delta,
            "Costo extra 180d": int(extra) if delta else None,
            "Net 180d CLP": int(net) if delta else None,
        })

    out = pd.DataFrame(rows)
    out.to_excel(OUT_XLSX, index=False)
    print(f"\nOK {OUT_XLSX}")

    target = out[(out["Estado actual"] == "gold_special") & (out["Net 180d CLP"].fillna(-1) > 0)]
    print(f"\nROI+: {len(target)}")
    for _, r in target.sort_values("Net 180d CLP", ascending=False).iterrows():
        print(f"  {r['Cuenta']} {r['ItemID']} | {r['Título actual'][:40]:40s} | "
              f"hermano {int(r['Hermano visitas 30d (num)'])}v | "
              f"upside ${r['Upside revenue 180d']:>8,} | net ${int(r['Net 180d CLP']):>7,}")
    if len(target):
        print(f"\nNet 180d bloque SEO: ${int(target['Net 180d CLP'].sum()):,}")

    if not execute or not len(target):
        if not execute:
            print("\n[dry-run — no se ejecuta PUT]")
        return

    print(f"\n=== EJECUTANDO {len(target)} upgrades ===")
    log = []
    for i, (_, r) in enumerate(target.iterrows(), 1):
        iid = r["ItemID"]; cuenta = r["Cuenta"]
        print(f"[{i}/{len(target)}] {cuenta} {iid}  {r['Título actual'][:35]}")
        sc, body = upgrade_item(cuenta, iid)
        if sc == 200:
            time.sleep(0.5)
            post = get_item(cuenta, iid)
            ok = post and post.get("listing_type_id") == "gold_pro"
            marker = "✓" if ok else "?"
            print(f"  {marker} {post.get('listing_type_id') if post else 'no-get'}")
            log.append({"item": iid, "cuenta": cuenta, "status": "OK" if ok else "POST_MISMATCH",
                       "net_180d_proyectado": int(r["Net 180d CLP"])})
        else:
            print(f"  ✗ {sc} {body}")
            log.append({"item": iid, "cuenta": cuenta, "status": "FAIL", "http": sc, "detail": str(body)})
        time.sleep(0.4)
    out_log = ROOT / "data" / "auditoria" / f"upgrade_listing_seo_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    out_log.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    ok_n = sum(1 for x in log if x["status"] == "OK")
    fail_n = sum(1 for x in log if x["status"] == "FAIL")
    print(f"\nOK: {ok_n} | FAIL: {fail_n}")
    print(f"LOG: {out_log}")


if __name__ == "__main__":
    main(execute=("--execute" in sys.argv))
