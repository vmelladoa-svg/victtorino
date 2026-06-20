import sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC = "https://victtorino.cl"
P = {"consumer_key":"ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret":"cs_3604e7ebdb8ff78442731344cc95af50516188a5"}
UA = {"User-Agent":"Mozilla/5.0"}
tests = [
 ("wc/v3/products SIN llave", "/wp-json/wc/v3/products?per_page=1", None),
 ("wc/v3/products CON llave", "/wp-json/wc/v3/products?per_page=1", P),
 ("wc/v3 raiz CON llave",     "/wp-json/wc/v3", P),
 ("wc/v3/settings CON llave", "/wp-json/wc/v3/settings", P),
 ("wc/v3/data CON llave",     "/wp-json/wc/v3/data", P),
 ("wc/v3/orders CON llave",   "/wp-json/wc/v3/orders?per_page=1", P),
 ("wc-admin/options",         "/wp-json/wc-admin/options?options=woocommerce_version", P),
]
for label, ep, auth in tests:
    try:
        r = requests.get(WC+ep, params=auth, headers=UA, timeout=40)
        print(f"  {r.status_code}  {label}")
    except Exception as e:
        print(f"  ERR {label}: {e}")
