import sys, io, requests, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC="https://victtorino.cl"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"}
s=requests.Session(); s.headers.update(UA)

print("== wp-login.php ==")
r=s.get(WC+"/wp-login.php",timeout=30)
print(f"  HTTP {r.status_code}, {len(r.content)}b")
print(f"  ¿formulario de login presente?  user={'user_login' in r.text}  pass={'user_pass' in r.text}  boton={'wp-submit' in r.text}")
# ¿su CSS carga?
css=re.findall(r'<link[^>]+stylesheet[^>]*href=["\']([^"\']+)["\']', r.text)
print(f"  CSS del login: {len(css)} archivos")
for c in css[:6]:
    full=c if c.startswith("http") else WC+c
    cr=s.get(full,timeout=15)
    estado="OK" if cr.status_code==200 and len(cr.content)>20 else "<<< ROTO"
    print(f"    {cr.status_code} {estado:9s} {len(cr.content):>7d}b  {c[-60:]}")

print("\n== /wp-admin/ (sin login) ==")
r=s.get(WC+"/wp-admin/",timeout=30,allow_redirects=False)
print(f"  HTTP {r.status_code}  Location={r.headers.get('Location','-')[:80]}")

print("\n== ¿wp-login responde a POST? (probe, sin credenciales reales) ==")
r=s.post(WC+"/wp-login.php",data={"log":"probe","pwd":"probe","wp-submit":"Acceder"},timeout=30,allow_redirects=False)
print(f"  HTTP {r.status_code} (esperado 200 con 'incorrecta' = login funciona)")
print(f"  ¿menciona error de credenciales?  {'incorrect' in r.text.lower() or 'no es correcta' in r.text.lower() or 'desconocido' in r.text.lower() or 'error' in r.text.lower()}")
