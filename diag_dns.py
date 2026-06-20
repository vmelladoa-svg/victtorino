import sys, io, socket, requests, ssl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
host = "victtorino.cl"

print("== DNS: a qué IP(s) resuelve victtorino.cl (desde aquí) ==")
try:
    infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    ips = sorted({i[4][0] for i in infos})
    for ip in ips:
        print(f"   {ip}")
except Exception as e:
    print(f"   ERR {e}")
try:
    print("   www:", sorted({i[4][0] for i in socket.getaddrinfo('www.'+host,443)}))
except Exception as e:
    print("   www ERR", e)

print("\n== Headers del servidor que responde ==")
for url in [f"https://{host}/", f"http://{host}/"]:
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=30, allow_redirects=False)
        print(f"\n  {url} -> {r.status_code}")
        for h in ["Server","X-LiteSpeed-Cache","X-Powered-By","CF-Ray","X-Cache",
                  "Location","X-Served-By","Host-Header","cf-cache-status","X-Turbo-Charged-By"]:
            if h in r.headers:
                print(f"     {h}: {r.headers[h]}")
    except Exception as e:
        print(f"  {url} ERR {e}")
