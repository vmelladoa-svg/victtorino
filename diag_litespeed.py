import sys, io, requests, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC="https://victtorino.cl"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"}

# Pedir home FRESCA (cache-buster -> origen, no Cloudflare)
r=requests.get(WC+"/?nocache=zzz123",headers={**UA,"Cache-Control":"no-cache"},timeout=40)
html=r.text
print(f"home fresca: {r.status_code}, cf={r.headers.get('cf-cache-status')}, xcache={r.headers.get('X-Cache','-')}\n")

# Qué CSS referencia el origen ahora
css=re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']', html)
css2=re.findall(r'href=["\']([^"\']*litespeed[^"\']*\.css[^"\']*)["\']', html)
print("CSS que referencia el ORIGEN fresco:")
for c in set(css+css2):
    full=c if c.startswith("http") else WC+c
    rr=requests.get(full,headers=UA,timeout=20)
    print(f"  {rr.status_code} {len(rr.content):>7d}b  {c[-80:]}")

# ¿Cuántos <link stylesheet> totales? (si LiteSpeed combine OFF, habría muchos individuales)
todos=re.findall(r'<link[^>]+stylesheet', html)
print(f"\nTotal <link stylesheet> en el HTML: {len(todos)}")

# ¿Aparece /wp-content/plugins/.../style.css individuales o solo el combinado?
indiv=re.findall(r'href=["\']([^"\']*/wp-content/(?:plugins|themes)/[^"\']+\.css[^"\']*)["\']', html)
print(f"CSS individuales de plugins/themes referenciados: {len(indiv)}")
for i in indiv[:8]:
    rr=requests.get(i if i.startswith('http') else WC+i,headers=UA,timeout=15)
    print(f"  {rr.status_code}  {i[-70:]}")

# Header del servidor de origen: ¿es LiteSpeed o Apache/nginx?
print(f"\nServer del origen (via cache-buster): {r.headers.get('Server')}")
print(f"X-LiteSpeed-Cache presente: {'X-LiteSpeed-Cache' in r.headers}")
