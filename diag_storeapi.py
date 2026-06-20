"""Probar Store API (cliente) vs admin REST, e identificar alcance del 500."""
import sys, io, re, requests, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}
UA = {"User-Agent": "Mozilla/5.0"}

print("== STORE API (cara al cliente, sin auth) ==")
store_eps = [
    "/wp-json/wc/store/v1/products?per_page=1",
    "/wp-json/wc/store/v1/cart",
    "/wp-json/wc/store/v1/products/categories?per_page=1",
]
for ep in store_eps:
    try:
        r = requests.get(WC + ep, headers=UA, timeout=40)
        ok = "OK" if r.status_code == 200 else "<<< FALLA"
        print(f"  {r.status_code} {ok:10s} {ep}")
    except Exception as e:
        print(f"  ERR {ep}: {e}")

print("\n== Namespaces registrados en /wp-json/ ==")
try:
    r = requests.get(f"{WC}/wp-json/", headers=UA, timeout=40)
    ns = r.json().get("namespaces", [])
    print("  " + ", ".join(ns))
except Exception as e:
    print(f"  ERR: {e}")

print("\n== ¿El 500 es solo WC o también otros namespaces de plugins? ==")
test = [
    "/wp-json/wc/v3/products?per_page=1",
    "/wp-json/wc/v2/products?per_page=1",
    "/wp-json/wc/v1/products?per_page=1",
    "/wp-json/wc-analytics/products?per_page=1",
    "/wp-json/wc-admin/options?options=woocommerce_default_country",
    "/wp-json/elementor/v1/globals",
    "/wp-json/yoast/v1/get_head?url=https://victtorino.cl/",
]
for ep in test:
    try:
        r = requests.get(WC + ep, params=P, headers=UA, timeout=40)
        print(f"  {r.status_code}  {ep}")
    except Exception as e:
        print(f"  ERR {ep}: {e}")

print("\n== ¿La home muestra 'critical error' o banner de error en algún lado? ==")
try:
    r = requests.get(WC + "/", headers=UA, timeout=40)
    for pat in ["critical error", "ha ocurrido un error", "error crítico",
                "There has been a critical"]:
        if pat.lower() in r.text.lower():
            print(f"  >> Home contiene: '{pat}'")
    print("  (si no hay líneas '>>', la home está limpia)")
except Exception as e:
    print(f"  ERR: {e}")
