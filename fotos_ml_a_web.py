"""
fotos_ml_a_web.py  —  Copia fotos de MercadoLibre a productos de la web (WooCommerce)
=====================================================================================
Caso de uso: productos que YA existen en victtorino.cl pero sin foto (o con muy pocas),
y que tienen su publicacion equivalente en alguna cuenta ML (C1/C2/C3) con buenas fotos.

Como funciona el cruce
----------------------
1. Lee el catalogo WooCommerce EN VIVO (no usa snapshots viejos).
2. Lee las publicaciones ML activas desde data/auditoria/snapshot_c{1,2,3}.json.
3. Matchea cada producto web por:
      - SKU exacto  (sku web "010501022-T" == sku ML sin sufijo "__NNNN")  -> score 1.0
      - Si no hay SKU, por TITULO normalizado (Jaccard/ratio) + validacion de
        NUMEROS de dimension (80x80, 100x44, 90mm...). Si las dimensiones no calzan,
        cae a "dudoso" aunque el titulo se parezca.
4. Clasifica:
      SEGURO  = SKU exacto, o titulo>=0.85 con dimensiones compatibles  -> auto-aplicable
      DUDOSO  = el resto                                                -> revisar a mano

IMPORTANTE: al aplicar PRESERVA las fotos existentes (por id) y AGREGA las de ML.
mlstatic.com sirve URLs publicas, asi que WooCommerce las descarga directo.

Uso
---
  python fotos_ml_a_web.py                      # DRY-RUN: muestra el plan, escribe plan_fotos_web.json. No cambia nada.
  python fotos_ml_a_web.py --max-fotos 1        # considera tambien productos que tienen <=1 foto (default 0 = solo sin foto)
  python fotos_ml_a_web.py --apply-seguros      # aplica todos los clasificados SEGURO
  python fotos_ml_a_web.py --apply 1816 1818    # aplica woo_ids puntuales (incluye dudosos que tu apruebes)

Recomendacion: corre primero el dry-run, revisa la tabla DUDOSO, y aplica con --apply
los woo_id que confirmes. Para productos sensibles a dimension/modelo (shower doors,
lavaplatos por tamano, asientos WC por modelo) NUNCA confies ciego en el match por titulo.
"""
import json, sys, io, re, unicodedata, argparse, time
from difflib import SequenceMatcher
from pathlib import Path
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
ROOT = Path(__file__).resolve().parent

WC  = "https://victtorino.cl"
KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"

RUIDO = {"envio","gratis","nuevo","oferta","para","con","sin","de","del","la","el",
         "los","las","un","una","y","o","en"}


def http(method, url, **kw):
    """GET/PUT con reintentos ante timeouts/503 transitorios del servidor web."""
    kw.setdefault("timeout", 60)
    last = None
    for intento in range(4):
        try:
            r = requests.request(method, url, **kw)
            if r.status_code == 503:
                last = r
                time.sleep(3 * (intento + 1))
                continue
            return r
        except requests.exceptions.RequestException as e:
            last = e
            time.sleep(3 * (intento + 1))
    if isinstance(last, Exception):
        raise last
    return last


def norm(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(sorted(t for t in s.split() if t and t not in RUIDO and len(t) > 1))


def nums(s):
    """Numeros de >=2 digitos (dimensiones)."""
    return set(re.findall(r"\d{2,4}", (s or "").lower().replace(",", ".")))


def sku_de(it):
    s = (it.get("seller_custom_field") or "").strip().upper()
    if not s:
        for a in (it.get("attributes") or []):
            if a.get("id") == "SELLER_SKU":
                s = (a.get("value_name") or "").strip().upper()
    return s


def cargar_ml():
    ml = []
    for c in ["c1", "c2", "c3"]:
        f = ROOT / "data" / "auditoria" / f"snapshot_{c}.json"
        if not f.exists():
            print(f"[WARN] falta {f}; salto cuenta {c}")
            continue
        snap = json.loads(f.read_text(encoding="utf-8"))
        for it in snap["items"]:
            if it.get("status") != "active":
                continue
            pics = it.get("pictures") or []
            if not pics:
                continue
            ml.append({
                "cuenta": c, "id": it["id"], "title": it.get("title") or "",
                "n": len(pics), "sku": sku_de(it).split("__")[0],
                "norm": norm(it.get("title")), "nums": nums(it.get("title")),
                "urls": [(p.get("secure_url") or p.get("url")) for p in pics],
            })
    return ml


def cargar_woo_sin_foto(max_fotos):
    """Productos web con <= max_fotos imagenes (default 0 = sin foto) y con SKU."""
    out, page = [], 1
    while True:
        r = http("GET", f"{WC}/wp-json/wc/v3/products",
                 params={"consumer_key": KEY, "consumer_secret": SEC,
                         "per_page": 100, "page": page, "status": "any"})
        r.raise_for_status()
        d = r.json()
        if not d:
            break
        out.extend(d)
        if int(r.headers.get("X-WP-TotalPages", 1)) <= page:
            break
        page += 1
    res = []
    for p in out:
        if (p.get("sku") or "").strip() and len(p.get("images") or []) <= max_fotos:
            res.append(p)
    return res


def mejor_match(name, sku, ml):
    nm, wn = norm(name), nums(name)
    best, bs = None, 0.0
    for m in ml:
        sc = SequenceMatcher(None, nm, m["norm"]).ratio()
        tm, tw = set(nm.split()), set(m["norm"].split())
        if tm and tw:
            sc = max(sc, len(tm & tw) / len(tm | tw))
        if m["sku"] and m["sku"] == sku:
            sc = 2.0
        if sc > bs:
            bs, best = sc, m
    if not best:
        return None, 0.0, False, False
    sku_ok = best["sku"] == sku and bool(sku)
    nums_ok = (not wn) or (wn <= best["nums"])
    return best, min(bs, 1.0), sku_ok, nums_ok


def construir_plan(max_fotos):
    ml = cargar_ml()
    print(f"ML activos con fotos: {len(ml)}")
    woo = cargar_woo_sin_foto(max_fotos)
    print(f"Productos web con <={max_fotos} foto(s) y SKU: {len(woo)}\n")
    seguro, dudoso = [], []
    for p in woo:
        sku = (p.get("sku") or "").strip().upper()
        best, sc, sku_ok, nums_ok = mejor_match(p.get("name"), sku, ml)
        if not best:
            continue
        rec = {"woo_id": p["id"], "sku": sku, "name": p.get("name"),
               "existentes": [im["id"] for im in (p.get("images") or [])],
               "score": round(sc, 2), "sku_ok": sku_ok, "nums_ok": nums_ok,
               "ml_cuenta": best["cuenta"], "ml_id": best["id"],
               "ml_title": best["title"], "ml_fotos": best["n"], "urls": best["urls"]}
        (seguro if (sku_ok or (sc >= 0.85 and nums_ok)) else dudoso).append(rec)
    plan = {"seguro": seguro, "dudoso": dudoso}
    (ROOT / "plan_fotos_web.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan


def aplicar(registros):
    ok = 0
    for r in registros:
        wid = r["woo_id"]
        images = [{"id": i} for i in r["existentes"]] + [{"src": u} for u in r["urls"]]
        p = http("PUT", f"{WC}/wp-json/wc/v3/products/{wid}",
                 params={"consumer_key": KEY, "consumer_secret": SEC},
                 json={"images": images}, timeout=180)
        if p.status_code >= 400:
            print(f"  [{wid}] ERROR {p.status_code}: {p.text[:120]}")
            continue
        fin = len(p.json().get("images", []))
        print(f"  [{wid}] OK  {len(r['existentes'])} previas + {len(r['urls'])} ML -> {fin} en web | {r['name'][:42]}")
        ok += 1
    print(f"\n=== {ok}/{len(registros)} aplicados ===")


def tabla(titulo, regs):
    print(f"\n=== {titulo}: {len(regs)} ===")
    for r in regs:
        tag = "SKU" if r["sku_ok"] else f"t{r['score']}"
        nm = (r["name"] or "").encode("ascii", "replace").decode()[:40]
        mt = (r["ml_title"] or "").encode("ascii", "replace").decode()[:34]
        print(f"  {r['woo_id']} {r['sku']:14} {tag:5} existe={len(r['existentes'])} +{r['ml_fotos']}f "
              f"[{r['ml_cuenta']}] | {nm} <- {mt}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-fotos", type=int, default=0,
                    help="incluir productos con hasta N fotos (default 0 = solo sin foto)")
    ap.add_argument("--apply-seguros", action="store_true")
    ap.add_argument("--apply", nargs="*", type=int, default=None,
                    help="woo_ids puntuales a aplicar")
    args = ap.parse_args()

    plan = construir_plan(args.max_fotos)
    tabla("SEGURO (auto-aplicable)", plan["seguro"])
    tabla("DUDOSO (revisar a mano)", plan["dudoso"])

    if args.apply_seguros:
        print("\n>>> Aplicando SEGUROS...")
        aplicar(plan["seguro"])
    elif args.apply:
        pool = {r["woo_id"]: r for r in plan["seguro"] + plan["dudoso"]}
        elegidos = [pool[i] for i in args.apply if i in pool]
        faltan = [i for i in args.apply if i not in pool]
        if faltan:
            print(f"[WARN] sin candidato en el plan: {faltan}")
        print(f"\n>>> Aplicando {len(elegidos)} woo_id puntuales...")
        aplicar(elegidos)
    else:
        print("\n(DRY-RUN: nada cambiado. Usa --apply-seguros o --apply <ids> para escribir.)")


if __name__ == "__main__":
    main()
