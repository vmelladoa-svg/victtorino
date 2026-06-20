import sys, io, requests, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC="https://victtorino.cl"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"}
# URLs que Cloudflare NO cachea (fuerzan origen): wp-login, wp-admin, ?nocache, cart con param
pruebas = [
 ("home cache-buster", "/?cb=99887766"),
 ("wp-login.php",       "/wp-login.php"),
 ("wp-admin",           "/wp-admin/"),
 ("?add-to-cart",       "/?add-to-cart=3173"),
 ("rest wp core",       "/wp-json/"),
 ("admin-ajax",         "/wp-admin/admin-ajax.php?action=heartbeat"),
]
for label, ruta in pruebas:
    try:
        r = requests.get(WC+ruta, headers=UA, timeout=45, allow_redirects=False)
        cc = r.headers.get("cf-cache-status","-")
        xc = r.headers.get("X-Cache","-")
        loc = r.headers.get("Location","")
        srv = r.headers.get("Server","-")
        print(f"  {r.status_code} cf={cc:8s} xcache={xc:6s} {len(r.content):>7d}b  {label:18s} {ruta}  {('-> '+loc) if loc else ''}")
    except requests.Timeout:
        print(f"  TIMEOUT (origen colgado)  {label:18s} {ruta}")
    except Exception as e:
        print(f"  ERR:{type(e).__name__}  {label:18s} {ruta}")
