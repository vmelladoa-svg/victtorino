"""
Captura baseline pre-cambios de los items intervenidos hoy (2026-05-23).
Output: data/auditoria/seguimiento_baseline_2026-05-23.json

Cohortes:
  - upgrade_listing: 24 items con upgrade gold_pro
  - sync_atributos: 2 items con sync de atributos
  - fotos_cross: 14 items con fotos actualizadas
  - titulo_playwright: 1 item con título cambiado
  - bajada_precio: 7 items con precio -10%
  - ads_top10: 10 SKUs candidatos a Mercado Ads C3
  - control: 30 items random de C1/C2/C3 sin intervención (grupo control)
"""
import json
import glob
import pickle
import random
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).parent
ANALISIS = ROOT / "data" / "auditoria" / "analisis.pkl"
OUT = ROOT / "data" / "auditoria" / "seguimiento_baseline_2026-05-23.json"

random.seed(42)  # reproducible


def main():
    data = pickle.loads(ANALISIS.read_bytes())
    df = data["df_publicaciones"]
    snapshots = data["snapshots"]

    # 1) Cohorte upgrade_listing — leer logs
    upgrade_ids = set()
    for f in sorted(glob.glob(str(ROOT / "data/auditoria/upgrade_listing_*.json"))):
        for x in json.load(open(f, encoding="utf-8")):
            if x.get("status") == "OK":
                upgrade_ids.add(x["item"])

    # 2) Cohorte sync atributos
    sync_ids = set()
    for f in sorted(glob.glob(str(ROOT / "data/auditoria/sync_atributos_*.json"))):
        for x in json.load(open(f, encoding="utf-8")):
            if x.get("status") == "OK":
                sync_ids.add(x["item"])

    # 3) Cohorte fotos
    foto_ids = set()
    for f in sorted(glob.glob(str(ROOT / "data/auditoria/fotos_cross_*.json"))):
        for x in json.load(open(f, encoding="utf-8")):
            if x.get("status") == "OK":
                foto_ids.add(x["target_id"])

    # 4) Cohorte título Playwright
    titulo_ids = set()
    for f in sorted(glob.glob(str(ROOT / "data/auditoria/titulos_playwright_*.json"))):
        for x in json.load(open(f, encoding="utf-8")):
            if x.get("status") == "OK":
                titulo_ids.add(x["iid"])

    # 5) Cohorte bajada precio
    precio_ids = set()
    for f in sorted(glob.glob(str(ROOT / "data/auditoria/bajar_precio_*.json"))):
        for x in json.load(open(f, encoding="utf-8")):
            if x.get("status") == "OK":
                precio_ids.add(x["item"])

    # 6) Ads top 10 C3
    c3 = df[df["Cuenta"] == "C3"].copy()
    candidatos = c3[(c3["Stock"] >= 3) & (c3["HealthCalc"] >= 70) & (c3["Vendidos180d"] > 0)]
    ads_top10 = set(candidatos.sort_values("Vendidos180d", ascending=False).head(10)["ItemID"].tolist())

    # 7) Control: 30 items random sin intervención (10 por cuenta)
    intervenidos = upgrade_ids | sync_ids | foto_ids | titulo_ids | precio_ids | ads_top10
    activos = df[df["Vendidos180d"] > 0]  # solo los que venden para comparación justa
    control = set()
    for cuenta in ("C1", "C2", "C3"):
        candidates = activos[(activos["Cuenta"] == cuenta) & (~activos["ItemID"].isin(intervenidos))]["ItemID"].tolist()
        random.shuffle(candidates)
        control.update(candidates[:10])

    # Capturar baseline por item
    def snapshot_item(iid):
        row = df[df["ItemID"] == iid]
        if row.empty:
            return None
        r = row.iloc[0]
        return {
            "item_id": iid,
            "cuenta": r["Cuenta"],
            "titulo": r["Título"],
            "categoria": r["Categoría"],
            "precio_baseline": int(r["Precio"]),
            "stock_baseline": int(r["Stock"]),
            "listing_baseline": r["ListingType"],
            "fotos_baseline": int(r["Fotos"]),
            "visitas_30d_baseline": int(r["Visitas30d"]),
            "vendidos_180d_baseline": int(r["Vendidos180d"]),
            "revenue_180d_baseline": int(r["Revenue180d"]),
            "health_calc_baseline": int(r["HealthCalc"]),
            "conv_rate_baseline": float(r["ConvRate%"]),
        }

    cohortes = {
        "upgrade_listing": sorted(upgrade_ids),
        "sync_atributos": sorted(sync_ids),
        "fotos_cross": sorted(foto_ids),
        "titulo_playwright": sorted(titulo_ids),
        "bajada_precio": sorted(precio_ids),
        "ads_top10": sorted(ads_top10),
        "control": sorted(control),
    }

    baseline = {
        "fecha_baseline": "2026-05-23",
        "fecha_captura": datetime.utcnow().isoformat() + "Z",
        "descripcion": "Baseline pre-cambios para medir efecto de la sesión de optimización 2026-05-23",
        "cohortes": cohortes,
        "items": {},
    }

    # Capturar todos los items únicos
    all_ids = set()
    for ids in cohortes.values():
        all_ids.update(ids)

    for iid in sorted(all_ids):
        snap = snapshot_item(iid)
        if snap:
            baseline["items"][iid] = snap

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {OUT}")
    print(f"\nTamaño cohortes:")
    for k, v in cohortes.items():
        print(f"  {k}: {len(v)} items")
    print(f"  TOTAL items capturados: {len(baseline['items'])}")
    print(f"\nMétricas baseline agregadas:")
    for cohorte, ids in cohortes.items():
        items = [baseline["items"][i] for i in ids if i in baseline["items"]]
        if not items: continue
        total_visitas = sum(i["visitas_30d_baseline"] for i in items)
        total_vendidos = sum(i["vendidos_180d_baseline"] for i in items)
        total_revenue = sum(i["revenue_180d_baseline"] for i in items)
        avg_health = sum(i["health_calc_baseline"] for i in items) / len(items)
        print(f"  {cohorte:18s}: {len(items):3d} items | visitas30d={total_visitas:5d} | vendidos180d={total_vendidos:4d} | revenue180d=${total_revenue:>10,} | health avg={avg_health:.1f}")


if __name__ == "__main__":
    main()
