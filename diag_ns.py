import sys, io, socket, ssl, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
host="victtorino.cl"

print("== Certificado SSL que sirve el sitio ==")
try:
    ctx=ssl.create_default_context()
    with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
        s.settimeout(15); s.connect((host,443))
        c=s.getpeercert()
    print("   subject:", dict(x[0] for x in c['subject']).get('commonName'))
    print("   issuer :", dict(x[0] for x in c['issuer']).get('organizationName'))
    print("   válido hasta:", c.get('notAfter'))
    print("   SAN:", [v for k,v in c.get('subjectAltName',()) ][:6])
except Exception as e:
    print("   ERR", e)

print("\n== Resolución DNS pública (Cloudflare DoH 1.1.1.1) NS y A ==")
for tipo in ["NS","A","AAAA","CNAME"]:
    try:
        r=requests.get("https://1.1.1.1/dns-query",
            params={"name":host,"type":tipo},
            headers={"accept":"application/dns-json"}, timeout=15)
        ans=r.json().get("Answer",[])
        vals=[a.get("data") for a in ans]
        print(f"   {tipo}: {vals if vals else '(ninguno)'}")
    except Exception as e:
        print(f"   {tipo}: ERR {e}")

print("\n== Google DNS 8.8.8.8 (comparar por si hay split) ==")
for tipo in ["NS","A"]:
    try:
        r=requests.get("https://8.8.8.8/resolve",
            params={"name":host,"type":tipo}, timeout=15)
        ans=r.json().get("Answer",[])
        print(f"   {tipo}: {[a.get('data') for a in ans]}")
    except Exception as e:
        print(f"   {tipo}: ERR {e}")
