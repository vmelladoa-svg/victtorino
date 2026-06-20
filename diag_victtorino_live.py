"""Diagnóstico en vivo victtorino.cl: versiones Elementor, smoke test, bug carrito 3173."""
import sys, io, re, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

print("=" * 60)
print("1) VERSIONES DE PLUGINS (System Status)")
print("=" * 60)
try:
    r = requests.get(f"{WC}/wp-json/wc/v3/system_status", params=P, timeout=60)
    if r.status_code == 200:
        data = r.json()
        plugins = data.get("active_plugins", [])
        env = data.get("environment", {})
        for pl in plugins:
            name = pl.get("name", "")
            if any(k in name.lower() for k in ["elementor", "redis", "litespeed",
                                               "autoptimize", "smush", "ewww", "woo"]):
                print(f"  {name:45s} v{pl.get('version','?')}")
        print(f"\n  PHP: {env.get('php_version')}  |  WP: {env.get('wp_version')}")
        print(f"  max_input_vars: {env.get('php_max_input_vars', '?')}")
        print(f"  external_object_cache: {env.get('external_object_cache')}")
        print(f"  WP_DEBUG: {env.get('wp_debug_mode')}")
        print(f"  Total plugins activos: {len(plugins)}")
    else:
        print(f"  System Status devolvió {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"  ERROR: {e}")

print()
print("=" * 60)
print("2) SMOKE TEST (códigos HTTP páginas clave)")
print("=" * 60)
paginas = ["/", "/tienda/", "/carrito/", "/categoria-producto/accesorios/"]
# añadir una ficha de producto real
try:
    rp = requests.get(f"{WC}/wp-json/wc/v3/products", params={**P, "per_page": 1,
                      "status": "publish"}, timeout=30)
    if rp.status_code == 200 and rp.json():
        prod = rp.json()[0]
        paginas.append("/?p=" + str(prod["id"]))
        prod_permalink = prod.get("permalink", "")
        if prod_permalink:
            paginas.append(prod_permalink.replace(WC, ""))
except Exception:
    pass

for ruta in paginas:
    try:
        r = requests.get(WC + ruta, headers=UA, timeout=40, allow_redirects=True)
        size = len(r.content)
        flag = "OK" if r.status_code == 200 else "<<< PROBLEMA"
        # detectar pantalla blanca / fatal
        blanco = "FATAL/BLANCA" if size < 2000 else ""
        print(f"  {r.status_code} {flag:12s} {size:>8d}b {blanco:12s} {ruta[:50]}")
    except Exception as e:
        print(f"  ERR {ruta[:50]}: {e}")

print()
print("=" * 60)
print("3) BUG CARRITO 3173 (cuántos botones apuntan al 3173)")
print("=" * 60)
for cat in ["/categoria-producto/accesorios/", "/tienda/"]:
    try:
        r = requests.get(WC + cat, headers=UA, timeout=40)
        html = r.text
        # contar value="3173" en contexto add-to-cart
        total_3173 = len(re.findall(r'add-to-cart[=/"\s]*3173\b', html)) + \
            len(re.findall(r'value=["\']3173["\']', html))
        # contar productos distintos en la grilla (data-product_id)
        ids = re.findall(r'data-product_id=["\'](\d+)["\']', html)
        ids_unicos = set(ids)
        # contar también botones add_to_cart_button
        botones = len(re.findall(r'add_to_cart_button', html))
        print(f"  {cat}")
        print(f"    referencias a 3173: {total_3173}")
        print(f"    data-product_id distintos: {len(ids_unicos)} (de {len(ids)} botones)")
        print(f"    botones add_to_cart_button: {botones}")
        if total_3173 > 1:
            print(f"    >>> BUG PRESENTE (varios botones apuntan al 3173)")
        elif len(ids_unicos) > 1:
            print(f"    >>> OK (botones apuntan a productos distintos)")
    except Exception as e:
        print(f"    ERR: {e}")
