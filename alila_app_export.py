"""
Exporta el catalogo completo de la app alila (coleccion clientDB 'hjxq') a Excel.
Usa alila_app_client.py (backend uniCloud). Solo lectura.
"""
import alila_app_client as A
import pandas as pd, json, time
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")

# pinyin -> etiqueta legible (mejor esfuerzo; los crudos se conservan)
COLS = {
    "hjh": "Código", "mc": "Nombre", "pm_xh": "Nombre/Modelo (CN)", "yw_pm": "Nombre (EN)",
    "zw_pm": "Nombre (CN)", "cgj": "Costo compra", "jg": "Precio", "jf_jg": "Precio en puntos",
    "cg_lj": "Link proveedor (1688)", "ml_lj": "Link MercadoLibre", "x_lm": "Categoría ES",
    "z_lm": "Categoría CN", "xx_fl": "Subcategoría", "bg_pl": "Rubro", "dw": "Unidad",
    "sp_cc": "Dimensiones", "bz_ss": "Embalaje", "bz": "Notas", "ss_cy": "Keywords ES",
    "kw": "Keywords", "zgkw": "Keywords (extra)", "gys_hjh": "Código proveedor",
    "zl_kc": "Stock", "hh": "N° artículo", "sm": "Descripción", "zt": "Estado",
    "hj_fzr": "Responsable", "create_date": "Fecha creación",
}

def fetch_all(where=None, limit=100):
    A.auth()
    rows, skip = [], 0
    while True:
        if skip and skip % 1000 == 0:
            A.auth()  # token dura 600s, refrescar por si acaso
        r = A.coll_get("hjxq", where=where, skip=skip, limit=limit)
        data = (r.get("data") or {}).get("data") or []
        if not data:
            break
        rows.extend(data)
        print(f"  {len(rows)} productos...")
        if len(data) < limit:
            break
        skip += limit
        time.sleep(0.05)
    return rows

def flat(d):
    o = {}
    for k, v in d.items():
        if k == "pf" and isinstance(v, list) and v:  # precios por volumen
            try:
                precios = sorted([(int(t.get("sl") or 0), t.get("xsj")) for t in v], key=lambda x: x[0])
                o["Precio (1u/menor cant.)"] = precios[0][1]
                o["Precio (mayor cant.)"] = precios[-1][1]
            except Exception:
                pass
            o["Precios x volumen (raw)"] = json.dumps(v, ensure_ascii=False)
        elif k == "tp" and isinstance(v, list):  # fotos
            o["N° fotos"] = len(v)
            o["Foto principal"] = v[0] if v else ""
            o["Todas las fotos"] = " | ".join(x for x in v if isinstance(x, str))
        elif k in ("sx1", "sx2") and isinstance(v, dict):
            nombre, vals = v.get("sxm"), v.get("sxz")
            if nombre:
                o[f"Atributo {k[-1]}"] = f"{nombre}: {', '.join(x for x in (vals or []) if x)}"
        elif k == "create_date":
            try:
                o[COLS[k]] = time.strftime("%Y-%m-%d", time.localtime(int(v)/1000))
            except Exception:
                o[COLS.get(k, k)] = v
        else:
            o[COLS.get(k, k)] = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
    return o

if __name__ == "__main__":
    print("=== Descargando catálogo hjxq (TODOS) ===")
    rows = fetch_all()
    print(f"\nTotal crudo: {len(rows)}")
    df = pd.DataFrame([flat(r) for r in rows])
    # ordenar columnas: las legibles primero
    pref = ["Código", "Nombre/Modelo (CN)", "Nombre (EN)", "Nombre (CN)", "Estado",
            "Categoría ES", "Categoría CN", "Subcategoría", "Rubro",
            "Costo compra", "Precio (1u/menor cant.)", "Precio (mayor cant.)", "Precios x volumen (raw)",
            "Precio en puntos", "Stock", "Unidad", "Dimensiones", "Embalaje",
            "Link proveedor (1688)", "Link MercadoLibre", "Keywords ES",
            "N° fotos", "Foto principal", "Todas las fotos", "Notas", "Descripción"]
    cols = [c for c in pref if c in df.columns] + [c for c in df.columns if c not in pref]
    df = df[cols]
    out = ROOT / "alila_app_catalogo.xlsx"
    df.to_excel(out, index=False)
    print(f"=== LISTO: {len(df)} productos -> {out} ===")
    print("En venta:", int((df['Estado'] == '上线销售').sum()) if 'Estado' in df else '?')
    print("Con link 1688:", int(df['Link proveedor (1688)'].astype(str).str.contains('1688').sum()) if 'Link proveedor (1688)' in df else '?')
    print("Con link ML:", int(df['Link MercadoLibre'].astype(str).str.startswith('http').sum()) if 'Link MercadoLibre' in df else '?')
