"""
Analisis de fotos faltantes y matching cross-cuentas.
Solo LEE. No modifica nada en MercadoLibre.

Produce:
  1. fotos_faltantes_c3.xlsx  — items en C3 con menos de 4 fotos
  2. replicacion_c3_a_c1.xlsx — items en C1 con <4 fotos cuyo SKU equivalente en C3 tiene mas fotos
  3. replicacion_c3_a_c2.xlsx — idem para C2
"""
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd

ROOT = Path(__file__).parent
SNAP = ROOT / "data" / "auditoria"


def sku_de(item):
    sku = (item.get("seller_custom_field") or "").strip().upper()
    if not sku:
        for a in (item.get("attributes") or []):
            if a.get("id") == "SELLER_SKU":
                sku = (a.get("value_name") or "").strip().upper()
                break
    return sku


def cargar(cuenta):
    snap = json.loads((SNAP / f"snapshot_{cuenta}.json").read_text(encoding="utf-8"))
    actives = [i for i in snap["items"] if i.get("status") == "active"]
    res = []
    for it in actives:
        pics = it.get("pictures") or []
        res.append({
            "id": it["id"],
            "title": it.get("title"),
            "sku": sku_de(it),
            "n_pics": len(pics),
            "pic_urls": [p.get("url") or p.get("secure_url") for p in pics],
            "stock": it.get("available_quantity"),
            "price": it.get("price"),
            "permalink": it.get("permalink"),
        })
    return res


print("Cargando snapshots...")
c1 = cargar("c1")
c2 = cargar("c2")
c3 = cargar("c3")
print(f"  C1: {len(c1)} | C2: {len(c2)} | C3: {len(c3)}")

# Indice por SKU (mejor fuente = mas pics)
def index_by_sku(items):
    idx = {}
    for it in items:
        sku = it["sku"]
        if not sku or it["n_pics"] == 0:
            continue
        if sku not in idx or it["n_pics"] > idx[sku]["n_pics"]:
            idx[sku] = it
    return idx

idx_c1 = index_by_sku(c1)
idx_c2 = index_by_sku(c2)
idx_c3 = index_by_sku(c3)

# Diagnostico de SKUs disponibles
print(f"\nSKUs unicos:")
print(f"  C1: {len(idx_c1)} con fotos")
print(f"  C2: {len(idx_c2)} con fotos")
print(f"  C3: {len(idx_c3)} con fotos")
print(f"\nSin SKU (no podran matchearse):")
print(f"  C1: {sum(1 for i in c1 if not i['sku'])} de {len(c1)}")
print(f"  C2: {sum(1 for i in c2 if not i['sku'])} de {len(c2)}")
print(f"  C3: {sum(1 for i in c3 if not i['sku'])} de {len(c3)}")

# ──── 1) Fotos faltantes en C3
faltantes_c3 = []
for it in c3:
    if it["n_pics"] < 4:
        # Hay fuente en C1 o C2 con mas fotos?
        fuente_c1 = idx_c1.get(it["sku"])
        fuente_c2 = idx_c2.get(it["sku"])
        f1 = fuente_c1["n_pics"] if fuente_c1 else 0
        f2 = fuente_c2["n_pics"] if fuente_c2 else 0
        mejor_fuente = "C1" if f1 >= f2 and f1 > it["n_pics"] else ("C2" if f2 > it["n_pics"] else "—")
        max_disponible = max(f1, f2, it["n_pics"])
        faltantes_c3.append({
            "Item ID": it["id"],
            "SKU": it["sku"] or "(sin SKU)",
            "Titulo": it["title"],
            "Fotos actuales": it["n_pics"],
            "Stock": it["stock"],
            "Precio": it["price"],
            "Fotos en C1": f1,
            "Fotos en C2": f2,
            "Mejor fuente": mejor_fuente,
            "Fotos posibles": max_disponible,
            "Mejora (fotos)": max_disponible - it["n_pics"] if mejor_fuente != "—" else 0,
            "Permalink": it["permalink"],
        })

df_falt = pd.DataFrame(faltantes_c3).sort_values(["Mejora (fotos)", "Fotos actuales"], ascending=[False, True])
out1 = ROOT / "fotos_faltantes_c3.xlsx"
df_falt.to_excel(out1, index=False)
print(f"\nOK  {out1}  ({len(df_falt)} items con <4 fotos en C3)")
con_match = (df_falt["Mejora (fotos)"] > 0).sum()
print(f"   {con_match} pueden mejorarse con fuente en C1 o C2")

# ──── 2 y 3) Replicacion C3 → C1 / C3 → C2
def plan_replicacion(target_items, target_name, idx_fuente_c3):
    rows = []
    for it in target_items:
        if it["n_pics"] >= 4:
            continue
        fuente = idx_fuente_c3.get(it["sku"])
        if not fuente:
            continue
        if fuente["n_pics"] <= it["n_pics"]:
            continue
        rows.append({
            f"{target_name} Item ID": it["id"],
            "SKU": it["sku"],
            "Titulo": it["title"],
            f"Fotos {target_name}": it["n_pics"],
            "Fotos C3 (fuente)": fuente["n_pics"],
            "Mejora": fuente["n_pics"] - it["n_pics"],
            "C3 Item ID": fuente["id"],
            f"Permalink {target_name}": it["permalink"],
            "Permalink C3": fuente["permalink"],
        })
    df = pd.DataFrame(rows).sort_values("Mejora", ascending=False)
    return df

df_c1 = plan_replicacion(c1, "C1", idx_c3)
df_c2 = plan_replicacion(c2, "C2", idx_c3)

out2 = ROOT / "replicacion_c3_a_c1.xlsx"
out3 = ROOT / "replicacion_c3_a_c2.xlsx"
df_c1.to_excel(out2, index=False)
df_c2.to_excel(out3, index=False)
print(f"\nOK  {out2}  ({len(df_c1)} items en C1 que pueden recibir fotos de C3)")
print(f"OK  {out3}  ({len(df_c2)} items en C2 que pueden recibir fotos de C3)")

# Resumen consola
print("\n=== RESUMEN ===")
print(f"C3 fotos faltantes:      {len(df_falt):3d}  (de los cuales {con_match} con fuente externa disponible)")
print(f"C1 → recibir desde C3:   {len(df_c1):3d}  publicaciones candidatas")
print(f"C2 → recibir desde C3:   {len(df_c2):3d}  publicaciones candidatas")
