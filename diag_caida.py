import sys, io, requests, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC = "https://victtorino.cl"
UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
rutas = ["/", "/tienda/", "/carrito/"]
for intento in range(1, 7):
    linea = f"intento {intento}: "
    for ruta in rutas:
        try:
            r = requests.get(WC+ruta, headers=UA, timeout=40, allow_redirects=True)
            blanco = " (BLANCA)" if len(r.content) < 2000 else ""
            linea += f"{ruta}={r.status_code}/{len(r.content)}b{blanco}  "
        except Exception as e:
            linea += f"{ruta}=ERR:{type(e).__name__}  "
    print(linea)
    time.sleep(3)
