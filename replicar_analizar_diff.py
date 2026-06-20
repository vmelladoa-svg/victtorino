"""
Construye el diff por par y el plan de cambios para los 15 perdedores.
Lee plan_replicacion_top15.xlsx + raw_fichas.json.
Salida: replicacion_plan_aplicar.xlsx con diff visible.
"""
import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent
PLAN = ROOT / "plan_replicacion_top15.xlsx"
FICHAS = ROOT / "data" / "auditoria" / "raw_fichas.json"
OUT = ROOT / "replicacion_plan_aplicar.xlsx"


def attrs_dict(it):
    d = {}
    for a in (it.get("attributes") or []):
        val = a.get("value_name") or (a.get("values") or [{}])[0].get("name") or ""
        d[a.get("id")] = val
    return d


def main():
    plan = pd.read_excel(PLAN)
    fichas = json.loads(FICHAS.read_text(encoding="utf-8"))

    out_rows = []
    for _, p in plan.iterrows():
        win = fichas[p["Win_ID"]]
        lose = fichas[p["Lose_ID"]]
        w_attr = attrs_dict(win)
        l_attr = attrs_dict(lose)
        w_desc = (win.get("_description", {}) or {}).get("plain_text", "") or ""
        l_desc = (lose.get("_description", {}) or {}).get("plain_text", "") or ""

        # Diff de atributos: en win pero no en lose, o diferentes
        missing = sorted([k for k in w_attr if k not in l_attr])
        different = sorted([k for k in w_attr if k in l_attr and w_attr[k] != l_attr[k]])

        # Cambios sugeridos
        cambios = []
        # 1. Listing type
        if win["listing_type_id"] != lose["listing_type_id"]:
            cambios.append(f"LISTING_TYPE: {lose['listing_type_id']} → {win['listing_type_id']}  ⚠️ costo")
        # 2. Título
        if win["title"] != lose["title"]:
            cambios.append(f"TÍTULO distinto")
        # 3. Atributos faltantes (lose no tiene)
        if missing:
            cambios.append(f"+{len(missing)} atributos faltantes: {','.join(missing[:8])}{'...' if len(missing)>8 else ''}")
        # 4. Atributos diferentes
        if different:
            cambios.append(f"~{len(different)} atributos con valor distinto: {','.join(different[:8])}{'...' if len(different)>8 else ''}")
        # 5. Descripción
        len_diff = len(w_desc) - len(l_desc)
        if abs(len_diff) > 100:
            cambios.append(f"DESCRIPCIÓN: ganador {len(w_desc)} chars vs perdedor {len(l_desc)} chars")
        # 6. Fotos count
        wp = len(win.get("pictures") or [])
        lp = len(lose.get("pictures") or [])
        if wp != lp:
            cambios.append(f"FOTOS: {lp} → {wp} (copiar)")

        out_rows.append({
            "#": len(out_rows)+1,
            "Producto": p["Producto"][:50],
            "Win (C3)": p["Win_ID"],
            "Lose": f"{p['Lose_Cuenta']} {p['Lose_ID']}",
            "Brecha ventas": p["Gap_Sales"],
            "Win Listing": win["listing_type_id"],
            "Lose Listing": lose["listing_type_id"],
            "Win Attrs": len(w_attr),
            "Lose Attrs": len(l_attr),
            "Attrs faltantes": len(missing),
            "Attrs diferentes": len(different),
            "Win Desc chars": len(w_desc),
            "Lose Desc chars": len(l_desc),
            "Win Pics": wp,
            "Lose Pics": lp,
            "Permalink lose": p["Lose_Permalink"],
            "Cambios sugeridos": " | ".join(cambios),
            "Lose_ItemID": p["Lose_ID"],
            "Win_ItemID": p["Win_ID"],
        })

    df_out = pd.DataFrame(out_rows)
    df_out.to_excel(OUT, index=False)
    print(f"OK {OUT}")
    print(f"\n=== Resumen diff por par ===")
    for _, r in df_out.iterrows():
        print(f"\n{r['#']:2d}. {r['Producto']}")
        print(f"    {r['Win (C3)']} → {r['Lose']}  | Brecha {r['Brecha ventas']}u")
        print(f"    Listing: {r['Win Listing']} vs {r['Lose Listing']}")
        print(f"    Attrs: win {r['Win Attrs']}, lose {r['Lose Attrs']} (faltan {r['Attrs faltantes']}, distintos {r['Attrs diferentes']})")
        print(f"    Desc: {r['Win Desc chars']} vs {r['Lose Desc chars']} chars  | Pics: {r['Win Pics']} vs {r['Lose Pics']}")


if __name__ == "__main__":
    main()
