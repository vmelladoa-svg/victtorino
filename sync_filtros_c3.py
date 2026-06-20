"""
Sincroniza atributos de ML C3 -> atributos globales (filtros) de WooCommerce.

  python sync_filtros_c3.py            # DRY-RUN: reporta facetas, normalizacion, matcheo (no escribe)
  python sync_filtros_c3.py --aplicar  # crea atributos globales + asigna a productos matcheados

Solo aplica a productos con match CONFIABLE (SKU exacto ML-id / scf / -T, o cruce alta).
Los dudosos y sin-match se reportan, no se tocan.
"""
import json, re, sys, io, time, requests
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).parent
ITEMS = json.load(open(ROOT / "atributos_c3_live.json", encoding="utf-8"))
WOO   = json.load(open(ROOT / "woo_products_live.json", encoding="utf-8"))
CRUCE = json.load(open(ROOT / "cruce_ml_woo_resultado.json", encoding="utf-8"))

# Credenciales WooCommerce R/W (POST/PUT requieren query params, no Basic Auth)
WC_BASE = "https://victtorino.cl/wp-json/wc/v3"
WC_CK   = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
WC_CS   = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"
WC_QP   = {"consumer_key": WC_CK, "consumer_secret": WC_CS}

# ───────────────────────── FACETAS + NORMALIZACION ─────────────────────────
# raw (lower, stripped) -> valor limpio ; None = descartar
NORM = {
    "BRAND": {},  # ya limpio: Täumm / Victtorino / Colomba
    "COLOR": {
        "plateado": "Plateado", "plate": "Plateado",
        "blanco": "Blanco", "blanco/cafe": "Blanco",
        "negro": "Negro",
        "cromado": "Cromado", "acero inoxidable / cromado": "Cromado",
        "acero inoxidable": "Acero inoxidable",
        "azul marino": "Azul", "azul": "Azul",
        "bronce": "Bronce", "transparente": "Transparente",
        "52053": None, "estandar": None,
    },
    "MATERIAL": {
        "acero inoxidable": "Acero inoxidable", "acero": "Acero inoxidable",
        "acero esmaltado": "Acero inoxidable", "acero inoxidable y plástico": "Acero inoxidable",
        "plástico": "Plástico", "abs": "Plástico", "plástico/pvc": "Plástico",
        "plástico (cuerpo) con tapa cromada": "Plástico",
        "metal": "Metal", "zamak cromado": "Metal",
        "bronce": "Bronce", "latón cromado": "Latón",
        "acrílico": "Acrílico", "vidrio": "Vidrio",
    },
    "FINISH": {
        "cromado": "Cromado", "cromado brillante": "Cromado", "zamak cromado": "Cromado",
        "cromado (tapa) y plástico blanco (cuerpo)": "Cromado",
        "brillante": "Brillante", "mate": "Mate",
        "cepillado": "Cepillado", "circular satinado cepillado": "Cepillado",
        "pulido fino": "Pulido", "pulido": "Pulido",
        "inoxidable": "Inoxidable", "plástico": None,
    },
    "FAUCET_CONTROL_TYPE": {
        "monocomando": "Monocomando", "monomando": "Monocomando",
        "doble comando": "Doble comando",
        "palanca": "Palanca",
        "manual": "Manual", "llave de paso manual": "Manual",
        "con difusor": None,
    },
    "MOUNTING_TYPE": {
        "de pared": "De pared", "de mesa": "De mesa", "sobre mesada": "Sobre mesada",
    },
    "HOLES_NUMBER": {
        "1": "1 agujero", "2": "2 agujeros", "3": "3 agujeros", "4": "4 agujeros",
    },
}
FACETS = {  # ml_attr_id : (slug, label)
    "BRAND": ("marca", "Marca"),
    "COLOR": ("color", "Color"),
    "MATERIAL": ("material", "Material"),
    "FINISH": ("acabado", "Acabado"),
    "FAUCET_CONTROL_TYPE": ("tipo-control", "Tipo de control"),
    "MOUNTING_TYPE": ("tipo-montaje", "Tipo de montaje"),
    "HOLES_NUMBER": ("n-agujeros", "N° de agujeros"),
}


def normalize(aid, raw):
    if not raw:
        return None
    table = NORM.get(aid, {})
    key = raw.strip().lower()
    if key in table:
        return table[key]
    if not table:          # sin tabla (BRAND) -> tal cual
        return raw.strip()
    return raw.strip()     # valor no previsto: se conserva (se reportará)


# ───────────────────────── MATCHEO ML -> WOO ─────────────────────────
woo_by_sku = {(p.get("sku") or "").strip().upper(): p for p in WOO if p.get("sku")}
woo_by_id  = {p["id"]: p for p in WOO}
cruce_alta = {r["ml_id"]: r["woo_match"][0] for r in CRUCE["ya_en_web"]}
cruce_dud  = {r["ml_id"]: r["woo_match"][0] for r in CRUCE["dudosos"]}


def match(it):
    mlid = it["id"]; scf = (it.get("seller_custom_field") or "").strip()
    if f"ML-{mlid}".upper() in woo_by_sku: return woo_by_sku[f"ML-{mlid}".upper()], "sku_mlid"
    if scf and scf.upper() in woo_by_sku:  return woo_by_sku[scf.upper()], "sku_scf"
    if scf:
        base = re.sub(r"__.*$", "", scf)
        for cand in (base + "-T", base, base.upper()):
            if cand.upper() in woo_by_sku: return woo_by_sku[cand.upper()], "sku_t"
    if mlid in cruce_alta and cruce_alta[mlid] in woo_by_id:
        return woo_by_id[cruce_alta[mlid]], "cruce_alta"
    return None, None


def build():
    """Devuelve: asignaciones {woo_id:{slug:valor}}, stats, valores no previstos."""
    asign = defaultdict(dict)
    facet_vals = defaultdict(Counter)
    unexpected = defaultdict(Counter)
    confiable = dudoso = sin = 0
    rep_dud, rep_sin = [], []
    for it in ITEMS:
        p, how = match(it)
        av = {a["id"]: a.get("value_name") for a in it.get("attributes", [])}
        if not p:
            if it["id"] in cruce_dud:
                dudoso += 1; rep_dud.append((it["id"], it.get("title", "")[:55]))
            else:
                sin += 1; rep_sin.append((it["id"], it.get("title", "")[:55]))
            continue
        confiable += 1
        for aid, (slug, label) in FACETS.items():
            raw = av.get(aid)
            val = normalize(aid, raw)
            if val:
                asign[p["id"]][slug] = val
                facet_vals[slug][val] += 1
                if raw and raw.strip().lower() not in NORM.get(aid, {}) and NORM.get(aid):
                    unexpected[slug][raw.strip()] += 1
    return asign, facet_vals, unexpected, dict(confiable=confiable, dudoso=dudoso, sin=sin,
                                               rep_dud=rep_dud, rep_sin=rep_sin)


def dry_run():
    asign, fv, unexp, st = build()
    print("=" * 70)
    print("  DRY-RUN — Sincronización de filtros C3 → web (NO escribe nada)")
    print("=" * 70)
    print(f"\nML activos analizados : {len(ITEMS)}")
    print(f"Match confiable        : {st['confiable']}  (reciben filtros)")
    print(f"Match dudoso           : {st['dudoso']}  (se reportan, NO se tocan)")
    print(f"Sin match              : {st['sin']}  (se reportan, NO se tocan)")
    print(f"Productos web a editar : {len(asign)}")

    print("\n" + "─" * 70)
    print("  FACETAS Y VALORES NORMALIZADOS (n = productos web con ese valor)")
    print("─" * 70)
    for aid, (slug, label) in FACETS.items():
        print(f"\n● {label}  (pa_{slug})  — {sum(fv[slug].values())} productos")
        for val, c in fv[slug].most_common():
            print(f"     {c:3}  {val}")
        if unexp.get(slug):
            print(f"     ⚠ valores NO normalizados (se cargan tal cual, revisa):")
            for val, c in unexp[slug].most_common():
                print(f"        {c:3}  «{val}»")

    json.dump({str(k): v for k, v in asign.items()},
              open(ROOT / "sync_filtros_asignacion.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump({"dudosos": st["rep_dud"], "sin_match": st["rep_sin"]},
              open(ROOT / "sync_filtros_no_matcheados.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("\n" + "─" * 70)
    print("  Asignación propuesta -> sync_filtros_asignacion.json")
    print("  No matcheados        -> sync_filtros_no_matcheados.json")
    print("  Para aplicar:  python sync_filtros_c3.py --aplicar")
    print("─" * 70)


# ───────────────────────── APLICAR ─────────────────────────
def wc_post(path, body, retries=3):
    for n in range(retries):
        r = requests.post(f"{WC_BASE}{path}", params=WC_QP, json=body, timeout=60)
        if r.status_code < 500:
            return r
        time.sleep(5)
    return r


def wc_put(path, body, retries=3):
    for n in range(retries):
        r = requests.put(f"{WC_BASE}{path}", params=WC_QP, json=body, timeout=60)
        if r.status_code < 500:
            return r
        time.sleep(5)
    return r


def ensure_attribute(slug, label):
    """Crea el atributo global o devuelve el existente. Retorna su id."""
    r = wc_post("/products/attributes",
                {"name": label, "slug": slug, "type": "select",
                 "order_by": "menu_order", "has_archives": True})
    if r.ok:
        return r.json()["id"]
    # ya existe -> buscarlo
    existing = requests.get(f"{WC_BASE}/products/attributes", params=WC_QP).json()
    for a in existing:
        if a["slug"] in (slug, f"pa_{slug}"):
            return a["id"]
    raise RuntimeError(f"No pude crear ni hallar atributo {slug}: {r.text[:200]}")


def aplicar():
    asign, fv, unexp, st = build()
    print("=" * 70)
    print("  APLICANDO filtros a la web (producción)")
    print("=" * 70)

    # 1) atributos globales + ids
    attr_id = {}
    for aid, (slug, label) in FACETS.items():
        attr_id[slug] = ensure_attribute(slug, label)
        print(f"  atributo pa_{slug:14} id={attr_id[slug]}  ({label})")
        time.sleep(0.3)

    # 2) términos
    print("\n  Creando términos...")
    for slug in attr_id:
        for val in fv[slug]:
            r = wc_post(f"/products/attributes/{attr_id[slug]}/terms", {"name": val})
            time.sleep(0.2)
    print("  términos listos.")

    # 3) asignar a productos (merge sin borrar lo existente)
    woo_attr_ids = set(attr_id.values())
    woo_now = {p["id"]: p for p in WOO}
    print(f"\n  Asignando a {len(asign)} productos...")
    ok = err = 0; errores = []
    for i, (wid, facetas) in enumerate(asign.items(), 1):
        wid = int(wid)
        prev = woo_now.get(wid, {}).get("attributes", [])
        # conservar atributos previos que NO sean de nuestras facetas
        keep = [a for a in prev if a.get("id") not in woo_attr_ids]
        nuevos = [{"id": attr_id[slug], "options": [val],
                   "visible": True, "variation": False}
                  for slug, val in facetas.items()]
        r = wc_put(f"/products/{wid}", {"attributes": keep + nuevos})
        if r.ok:
            ok += 1
        else:
            err += 1; errores.append({"id": wid, "err": r.text[:200]})
        print(f"    [{i}/{len(asign)}] {wid}  {'OK' if r.ok else 'ERR'}", end="\r")
        time.sleep(0.4)

    print(f"\n\n  Productos actualizados : {ok}")
    print(f"  Errores                : {err}")
    if errores:
        json.dump(errores, open(ROOT / "sync_filtros_errores.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("  Detalle -> sync_filtros_errores.json")
    print("=" * 70)


if __name__ == "__main__":
    if "--aplicar" in sys.argv:
        aplicar()
    else:
        dry_run()
