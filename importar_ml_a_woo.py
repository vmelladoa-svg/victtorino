"""
Prueba: importar 2 anuncios ML (cuenta C3) a WooCommerce como productos draft.

- Fuente: /users/{user_id}/items/search?status=active
- Detalle: /items/{id} y /items/{id}/description
- Destino: POST /wp-json/wc/v3/products  (status=draft)

Si hay error de auth o mapeo critico, aborta y reporta.
"""
import json
import os
import sys
import re
import io
import requests
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
load_dotenv()

# --- Credenciales ML (C3) ---
TOKENS_PATH = r"C:\Users\dell\victtorino\tokens_cuenta3.json"
with open(TOKENS_PATH, "r", encoding="utf-8") as f:
    tk = json.load(f)
ML_TOKEN = tk["access_token"]
ML_USER_ID = tk["user_id"]

# --- Credenciales WooCommerce ---
WC_BASE = "https://victtorino.cl"
WC_KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
WC_SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"

ML_HEAD = {"Authorization": f"Bearer {ML_TOKEN}"}


def abort(msg):
    print(f"\nABORTADO: {msg}", flush=True)
    sys.exit(1)


def ml_get(path, params=None):
    url = f"https://api.mercadolibre.com{path}"
    r = requests.get(url, headers=ML_HEAD, params=params or {}, timeout=30)
    if r.status_code == 401:
        abort(f"ML auth fallo (401) en {path}. Refresca token C3.")
    if r.status_code >= 400:
        abort(f"ML HTTP {r.status_code} en {path}: {r.text[:200]}")
    return r.json()


def wc_get(path, params=None):
    url = f"{WC_BASE}/wp-json/wc/v3{path}"
    r = requests.get(url, params=params or {}, auth=(WC_KEY, WC_SEC), timeout=30)
    if r.status_code == 401:
        abort(f"Woo auth fallo (401) en {path}.")
    if r.status_code >= 400:
        abort(f"Woo HTTP {r.status_code} en {path}: {r.text[:200]}")
    return r.json(), r.headers


def wc_post(path, body):
    # Apache puede tirar el header Authorization en POST -> usar query params
    url = f"{WC_BASE}/wp-json/wc/v3{path}"
    params = {"consumer_key": WC_KEY, "consumer_secret": WC_SEC}
    r = requests.post(url, json=body, params=params, timeout=60)
    if r.status_code == 401:
        abort(f"Woo auth fallo (401) en POST {path}: {r.text[:300]}")
    if r.status_code >= 400:
        abort(f"Woo HTTP {r.status_code} en POST {path}: {r.text[:300]}")
    return r.json()


def woo_categorias():
    """Devuelve lista de todas las categorias de Woo."""
    out = []
    page = 1
    while True:
        data, headers = wc_get("/products/categories", {"per_page": 100, "page": page})
        if not data:
            break
        out.extend(data)
        total_pages = int(headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1
    return out


def matchear_categoria(ml_path, cats_woo):
    """
    ml_path: lista de dicts [{id, name}, ...] desde /items/{id} -> category_path_from_root.
    cats_woo: lista de categorias Woo {id, name, slug, parent}.
    Estrategia: probar nombres ML del mas especifico al mas general,
    buscar match exacto (case-insensitive) en nombres Woo. Si no, buscar
    substring; si nada, retornar None.
    """
    if not ml_path:
        return None, None
    nombres_ml = [c["name"] for c in reversed(ml_path)]  # del mas especifico al raiz
    nombres_woo = {c["name"].lower().strip(): c for c in cats_woo}

    # 1) match exacto
    for n in nombres_ml:
        c = nombres_woo.get(n.lower().strip())
        if c:
            return c, f"exacto:{n}"
    # 2) substring (ml dentro de woo o viceversa)
    for n in nombres_ml:
        n_low = n.lower().strip()
        for w_low, c in nombres_woo.items():
            if n_low and (n_low in w_low or w_low in n_low) and len(n_low) >= 4:
                return c, f"substring:{n}~{c['name']}"
    return None, None


def strip_html_basico(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def detalle_ml(item_id):
    item = ml_get(f"/items/{item_id}")
    try:
        desc = ml_get(f"/items/{item_id}/description")
        descripcion = desc.get("plain_text") or strip_html_basico(desc.get("text", ""))
    except SystemExit:
        raise
    except Exception:
        descripcion = ""
    return item, descripcion


def construir_producto_woo(item, descripcion, cat_woo, status="draft"):
    imagenes = [{"src": p["url"]} for p in item.get("pictures", []) if p.get("url")]
    precio = item.get("price")
    stock = item.get("available_quantity") or 0
    body = {
        "name": item.get("title", "Sin titulo"),
        "type": "simple",
        "status": status,
        "regular_price": str(int(precio)) if precio is not None else "",
        "manage_stock": True,
        "stock_quantity": int(stock),
        "description": descripcion or "",
        "short_description": "",
        "images": imagenes,
        "sku": f"ML-{item.get('id')}",  # SKU prefijado para identificar origen ML
    }
    if cat_woo:
        body["categories"] = [{"id": cat_woo["id"]}]
    return body


def main():
    print("=" * 70)
    print(f"Importar 2 anuncios ML (C3 user_id={ML_USER_ID}) -> WooCommerce draft")
    print("=" * 70)

    # 1) listar 2 items activos
    print("\n[1/4] Listando items activos en ML...")
    res = ml_get(f"/users/{ML_USER_ID}/items/search", {"status": "active", "limit": 2})
    ids = res.get("results", [])
    if len(ids) < 2:
        abort(f"ML devolvio solo {len(ids)} items activos; se requieren 2.")
    print(f"      OK -> {ids}")

    # 2) categorias Woo
    print("\n[2/4] Cargando categorias WooCommerce...")
    cats_woo = woo_categorias()
    print(f"      OK -> {len(cats_woo)} categorias en Woo")

    creados = []
    saltados = []

    for idx, mid in enumerate(ids, start=1):
        print(f"\n[3/4] ({idx}/2) Procesando ML item {mid}...")
        item, descripcion = detalle_ml(mid)

        titulo = item.get("title", "")
        precio = item.get("price")
        stock = item.get("available_quantity")
        ml_path = item.get("category_path_from_root", [])
        print(f"      titulo: {titulo[:60]}")
        print(f"      precio: {precio} | stock: {stock} | fotos: {len(item.get('pictures', []))}")
        print(f"      categoria ML: {' > '.join(c['name'] for c in ml_path) if ml_path else '(sin path)'}")

        cat_woo, motivo = matchear_categoria(ml_path, cats_woo)
        if cat_woo:
            print(f"      -> match Woo: '{cat_woo['name']}' (id={cat_woo['id']}) [{motivo}]")
        else:
            print(f"      -> sin match de categoria, queda en 'Uncategorized'")

        # Verificar duplicado por SKU
        sku = f"ML-{mid}"
        existentes, _ = wc_get("/products", {"sku": sku})
        if existentes:
            ex = existentes[0]
            print(f"      DUPLICADO: ya existe en Woo (id={ex['id']}, status={ex['status']}). Salto creacion.")
            saltados.append({"ml_id": mid, "woo_id": ex["id"], "permalink": ex.get("permalink"), "motivo": "SKU duplicado"})
            continue

        body = construir_producto_woo(item, descripcion, cat_woo, status="draft")
        print(f"      [4/4] Creando producto draft en Woo...")
        nuevo = wc_post("/products", body)
        creados.append({
            "ml_id": mid,
            "ml_titulo": titulo,
            "woo_id": nuevo["id"],
            "permalink": nuevo.get("permalink"),
            "status": nuevo.get("status"),
            "edit_url": f"{WC_BASE}/wp-admin/post.php?post={nuevo['id']}&action=edit",
        })
        print(f"      OK -> Woo id={nuevo['id']} status={nuevo['status']}")

    # Reporte final
    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    print(json.dumps({"creados": creados, "saltados": saltados}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
