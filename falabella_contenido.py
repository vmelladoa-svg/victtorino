# -*- coding: utf-8 -*-
"""
falabella_contenido.py
======================
Para 29 SKU de Falabella (griferia/bano/cocina) busca su publicacion equivalente
en las cuentas MercadoLibre C1/C2/C3 (mismo seller) y extrae:
  - todas las fotos en alta resolucion  -> falabella_contenido/<SKU_Seller>/*.jpg
  - atributos tecnicos                  -> falabella_atributos.csv / .xlsx

Cruce por CODIGO INTERNO: el SKU Falabella '030101005-T1' y el seller_custom_field
de ML '030101005-T' comparten el nucleo numerico '030101005'. Indexamos ML por ese
nucleo y casamos.

Uso:
  python falabella_contenido.py            # scan + match + reporte (sin bajar fotos)
  python falabella_contenido.py --fotos    # ademas descarga las imagenes
"""
from __future__ import annotations
import argparse, csv, io, json, os, re, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

ML_BASE = "https://api.mercadolibre.com"
OAUTH_URL = f"{ML_BASE}/oauth/token"
CLIENT_ID = os.getenv("ML_CLIENT_ID") or "3959231945649654"
CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET") or "PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG"

CUENTAS = [
    {"alias": "C1", "tokens_file": ROOT / "tokens_cuenta1.json"},
    {"alias": "C2", "tokens_file": ROOT / "tokens_cuenta2.json"},
    {"alias": "C3", "tokens_file": ROOT / "tokens_cuenta3.json"},
]

# SKU_Seller | SKU_Falabella | Nombre | Grupo
PRODUCTOS = [
    ("030101005-T1", "146924919", "FLEXIBLE AGUA HE HI M10 1/2 50 CM", "FOTOS+ATRIB"),
    ("040501005-T1", "143573861", "Flexible Llave Profesional", "FOTOS+ATRIB"),
    ("010301011-T1", "146702739", "VALVULA DESCARGA DUAL FLUSH ESTANQUE TRADICIONAL", "FOTOS+ATRIB"),
    ("010301010-T1", "146699566", "VALVULA CARGA WC FLOTADOR", "FOTOS+ATRIB"),
    ("040302001-T1", "146959317", "VALVULA DESCARGA TEMPORIZADA URINARIO", "FOTOS"),
    ("010701001-T1", "143104744", "Dispensador de Palanca", "FOTOS"),
    ("010403001-T1", "146236900", "SIFON URINARIO 1 1/4 METALICO", "FOTOS"),
    ("010205001-T1", "146697576", "SIFON LAVATORIO 1 1/4 CODO PLASTICO", "FOTOS"),
    ("020102001-T1", "143564418", "Lavaplatos Sobreponer 80x50 Inoxidable Derecho", "FOTOS"),
    ("020101006-T1", "143986699", "Lavaplatos Empotrado Ancho 80x50x22 Cm Hannover", "FOTOS"),
    ("040202006-T1", "143984852", "Monomando Lavatorio Domenica", "FOTOS"),
    ("020301002-T1", "146236971", "LLAVE LAVADERO LAVADORA DOBLE 34", "FOTOS"),
    ("040202008-T1", "143984268", "Monomando Lavatorio Modern", "FOTOS"),
    ("020201005-T1", "152324732", "Organizador De Ducha Esquinero Triangular Bano", "FOTOS"),
    ("010301018-T1", "146703555", "SELLO ANTIFUGA - MIRAGE", "FOTOS"),
    ("010701003-T1", "143104631", "Dispensador Toalla De Papel Interfoliado Plastico", "FOTOS"),
    ("010301004-T1", "143573701", "Kit Para Estanque WC Carga Descarga Y Fijaciones", "FOTOS"),
    ("010701011-T1", "143573665", "Dispensador Jabon Simple Mejorado 360 ml", "FOTOS"),
    ("020202008-T1", "143566300", "Desague Lavaplatos 3 1/2 Rebalse", "ATRIB"),
    ("030102002-T1", "146932883", "FLEXIBLE GAS HI HI 3/8 1/2 100 CM", "ATRIB"),
    ("030102003-T1", "146935020", "FLEXIBLE GAS HI HI 3/8 1/2 60 CM", "ATRIB"),
    ("010602001-T1", "146722720", "DESAGUE TINA 1 1/2 REBALSE PLASTICO", "ATRIB"),
    ("010301015-T1", "146703258", "VALVULA DE CARGA LATERAL", "ATRIB"),
    ("010703008-T1", "146228456", "ESPEJO 60X90 RECTANGULAR ONDAS", "ATRIB"),
    ("030102004-T1", "146955850", "LLAVE PASO GAS HI HE 12", "ATRIB"),
    ("020201001-T1", "146823515", "CODO LAVAPLATOS SALIDA SIFON", "ATRIB"),
    ("010103003-T1", "143573675", "Brazo De Ducha Para Plato Acero Inoxidable 40 Cms", "ATRIB"),
    ("010801004-T1", "143573423", "Kit Completo Ducha Bidet Arabe", "ATRIB"),
    ("030101051-T1", "146928175", "FLEXIBLE AGUA HE HI 1/2 35 CM", "ATRIB"),
]


def max_res_url(url: str) -> str:
    """Convierte una URL de imagen ML a su variante de maxima resolucion (2X)."""
    if not url:
        return url
    path = url.split("mlstatic.com/", 1)[-1]
    core = re.sub(r"^D_(NQ_NP_2X_|NQ_NP_|NQ_)?", "", path)
    core = re.sub(r"-[A-Z]\.(jpg|webp|png)$", "", core, flags=re.I)
    return f"https://http2.mlstatic.com/D_NQ_NP_2X_{core}-F.jpg"


def nucleo(sku: str) -> str:
    """Codigo interno: digitos antes del primer '-' o '__'. '030101005-T1' -> '030101005'."""
    if not sku:
        return ""
    s = re.split(r"[-_]", str(sku).strip())[0]
    return re.sub(r"\D", "", s)


# ---------------------------------------------------------------- tokens
def cargar_cuenta(cfg):
    f = cfg["tokens_file"]
    data = json.loads(f.read_text(encoding="utf-8"))
    return {
        "alias": cfg["alias"], "file": f,
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "user_id": int(data["user_id"]),
    }


def refrescar(c):
    r = requests.post(OAUTH_URL, data={
        "grant_type": "refresh_token", "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET, "refresh_token": c["refresh_token"],
    }, timeout=30)
    r.raise_for_status()
    d = r.json()
    c["access_token"] = d["access_token"]
    c["refresh_token"] = d.get("refresh_token", c["refresh_token"])
    merged = json.loads(c["file"].read_text(encoding="utf-8"))
    merged.update({"access_token": c["access_token"], "refresh_token": c["refresh_token"],
                   "expires_in": d.get("expires_in"), "user_id": c["user_id"]})
    c["file"].write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"  [{c['alias']}] token refrescado")


def api(c, method, url, **kw):
    kw.setdefault("timeout", 60)
    for intento in range(5):
        h = kw.pop("headers", {}) if intento == 0 else h
        h = {"Authorization": f"Bearer {c['access_token']}"}
        r = requests.request(method, url, headers=h, **kw)
        if r.status_code == 401:
            refrescar(c)
            continue
        if r.status_code == 429:
            time.sleep(min(2 ** intento, 30))
            continue
        if r.status_code >= 500:
            time.sleep(min(2 ** intento, 20))
            continue
        return r
    return r


def scan_items(c):
    """Todos los item_id del seller (active + paused)."""
    ids = []
    for estado in ("active", "paused"):
        scroll = None
        while True:
            params = {"search_type": "scan", "status": estado, "limit": 100}
            if scroll:
                params["scroll_id"] = scroll
            r = api(c, "GET", f"{ML_BASE}/users/{c['user_id']}/items/search", params=params)
            if r.status_code != 200:
                print(f"  [{c['alias']}] scan {estado} HTTP {r.status_code}: {r.text[:200]}")
                break
            d = r.json()
            res = d.get("results", [])
            ids.extend(res)
            scroll = d.get("scroll_id")
            if not scroll or not res:
                break
    return list(dict.fromkeys(ids))


def get_items(c, ids):
    """multi-get detallado en lotes de 20."""
    out = {}
    attrs = "id,title,seller_custom_field,available_quantity,status,permalink,pictures,attributes,seller_sku,domain_id,catalog_product_id"
    for i in range(0, len(ids), 20):
        lote = ids[i:i + 20]
        r = api(c, "GET", f"{ML_BASE}/items", params={"ids": ",".join(lote), "attributes": attrs})
        if r.status_code != 200:
            continue
        for row in r.json():
            if row.get("code") == 200:
                body = row["body"]
                out[body["id"]] = body
    return out


def sku_de_item(it):
    """Intenta seller_custom_field, luego attribute SELLER_SKU."""
    s = it.get("seller_custom_field")
    if s:
        return s
    for a in it.get("attributes", []):
        if a.get("id") in ("SELLER_SKU",):
            return a.get("value_name")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fotos", action="store_true", help="descargar imagenes")
    args = ap.parse_args()

    # indice nucleo -> [items]
    indice = {}
    cache_path = ROOT / "falabella_ml_items_cache.json"
    if cache_path.exists():
        print(f"Usando cache {cache_path.name}")
        indice = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        for cfg in CUENTAS:
            try:
                c = cargar_cuenta(cfg)
            except FileNotFoundError as e:
                print(f"SKIP {cfg['alias']}: {e}")
                continue
            print(f"[{c['alias']}] scan items...")
            ids = scan_items(c)
            print(f"[{c['alias']}] {len(ids)} items, multi-get...")
            items = get_items(c, ids)
            for it in items.values():
                sk = sku_de_item(it)
                nu = nucleo(sk) if sk else ""
                if not nu:
                    continue
                rec = {
                    "cuenta": c["alias"], "item_id": it["id"], "sku": sk,
                    "title": it.get("title"), "status": it.get("status"),
                    "stock": it.get("available_quantity"),
                    "permalink": it.get("permalink"),
                    "domain_id": it.get("domain_id"),
                    "pictures": [p.get("secure_url") or p.get("url") for p in it.get("pictures", [])],
                    "attributes": [{"id": a.get("id"), "name": a.get("name"), "value": a.get("value_name")}
                                   for a in it.get("attributes", []) if a.get("value_name")],
                }
                indice.setdefault(nu, []).append(rec)
        cache_path.write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Cache guardado: {cache_path.name}  ({len(indice)} nucleos)")

    # cruce
    filas_attr = []
    resumen = []
    fotos_dir = ROOT / "falabella_contenido"
    for sku_seller, sku_fala, nombre, grupo in PRODUCTOS:
        nu = nucleo(sku_seller)
        cands = indice.get(nu, [])
        # priorizar el que tenga mas fotos / activo
        cands = sorted(cands, key=lambda r: (r["status"] == "active", len(r["pictures"])), reverse=True)
        match = cands[0] if cands else None
        n_fotos = len(match["pictures"]) if match else 0
        n_attrs = len(match["attributes"]) if match else 0
        resumen.append((sku_seller, sku_fala, nombre, grupo,
                        match["item_id"] if match else "-",
                        match["cuenta"] if match else "-",
                        n_fotos, n_attrs))
        if match:
            for a in match["attributes"]:
                filas_attr.append([sku_seller, sku_fala, nombre, a["name"] or a["id"], a["value"]])
            # meta
            filas_attr.append([sku_seller, sku_fala, nombre, "_ML_item", match["item_id"]])
            filas_attr.append([sku_seller, sku_fala, nombre, "_ML_permalink", match["permalink"]])

            if args.fotos and n_fotos:
                d = fotos_dir / sku_seller
                d.mkdir(parents=True, exist_ok=True)
                for i, url in enumerate(match["pictures"][:8], 1):
                    u = max_res_url(url)
                    try:
                        rr = requests.get(u, timeout=60)
                        if rr.status_code == 200:
                            (d / f"{sku_seller}_{i:02d}.jpg").write_bytes(rr.content)
                    except Exception as e:
                        print(f"  foto fail {sku_seller} #{i}: {e}")

    # export CSV atributos
    with open(ROOT / "falabella_atributos.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["SKU_Seller", "SKU_Falabella", "Nombre", "Atributo", "Valor"])
        w.writerows(filas_attr)

    # resumen consola
    print("\n=== RESUMEN MATCH ===")
    print(f"{'SKU_Seller':14} {'Grupo':11} {'ML_item':14} {'Cta':3} {'Fotos':5} {'Attrs':5}  Nombre")
    sin = 0
    for r in resumen:
        if r[4] == "-":
            sin += 1
        print(f"{r[0]:14} {r[3]:11} {r[4]:14} {r[5]:3} {r[6]:>5} {r[7]:>5}  {r[2][:40]}")
    print(f"\nTotal: {len(resumen)}  |  con match: {len(resumen)-sin}  |  sin match: {sin}")
    print(f"CSV atributos: falabella_atributos.csv ({len(filas_attr)} filas)")
    # guardar resumen json
    (ROOT / "falabella_resumen.json").write_text(
        json.dumps([dict(zip(["sku_seller","sku_fala","nombre","grupo","ml_item","cuenta","fotos","attrs"], r)) for r in resumen],
                   ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
