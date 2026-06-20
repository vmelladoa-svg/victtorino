"""
Enriquece snapshots con campos relevantes para análisis de catálogo central y canibalización:
  - catalog_listing (bool): si está en el catálogo central de ML
  - catalog_product_id: ID del producto en catálogo (si aplica)
  - buy_box_winner (bool): si es el ganador del buy box (cuando catalog=True)
  - sub_status: ['paused','outdated', etc]

Output: data/auditoria/catalog_enrichment_2026-05-24.json
"""
import json
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

ROOT = Path(__file__).parent
OUT = ROOT / "data" / "auditoria" / "catalog_enrichment_2026-05-24.json"

TOK = {
    "C1": json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"],
    "C2": json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"],
    "C3": json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"],
}


def fetch_item(cuenta, iid):
    h = {"Authorization": f"Bearer {TOK[cuenta]}"}
    r = requests.get(
        f"https://api.mercadolibre.com/items/{iid}",
        params={"attributes": "id,catalog_listing,catalog_product_id,buy_box_winner,domain_id,family_name,sub_status,inventory_id"},
        headers=h, timeout=15,
    )
    if r.status_code != 200:
        return iid, {"error": r.status_code}
    j = r.json()
    return iid, {
        "catalog_listing": j.get("catalog_listing"),
        "catalog_product_id": j.get("catalog_product_id"),
        "buy_box_winner": j.get("buy_box_winner"),
        "domain_id": j.get("domain_id"),
        "family_name": j.get("family_name"),
        "sub_status": j.get("sub_status"),
    }


def main():
    import pickle
    data = pickle.loads((ROOT / "data" / "auditoria" / "analisis.pkl").read_bytes())
    snapshots = data["snapshots"]

    # Obtener item IDs por cuenta
    tareas = []
    for c in ("C1", "C2", "C3"):
        for iid in snapshots[c].get("items_activos", []):
            tareas.append((c, iid))
    print(f"Total items a enriquecer: {len(tareas)}")

    enriched = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(fetch_item, c, iid): (c, iid) for c, iid in tareas}
        done = 0
        for f in as_completed(futs):
            cuenta, iid = futs[f]
            iid2, data_e = f.result()
            data_e["cuenta"] = cuenta
            enriched[iid] = data_e
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(tareas)} en {time.time()-t0:.0f}s")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nOK {OUT} ({len(enriched)} items)")

    # Stats rápidas
    cat_l = sum(1 for v in enriched.values() if v.get("catalog_listing"))
    bb_w = sum(1 for v in enriched.values() if v.get("buy_box_winner"))
    cat_ids = sum(1 for v in enriched.values() if v.get("catalog_product_id"))
    family = sum(1 for v in enriched.values() if v.get("family_name"))
    print(f"\nStats:")
    print(f"  catalog_listing=True: {cat_l} ({cat_l/len(enriched)*100:.0f}%)")
    print(f"  buy_box_winner=True:  {bb_w} ({bb_w/len(enriched)*100:.0f}%)")
    print(f"  catalog_product_id no nulo: {cat_ids}")
    print(f"  family_name presente: {family}")


if __name__ == "__main__":
    main()
