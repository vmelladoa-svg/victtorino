"""Extraer versiones de Elementor/WC/plugins desde el HTML del front (?ver=)."""
import sys, io, re, requests
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC = "https://victtorino.cl"
UA = {"User-Agent": "Mozilla/5.0"}

r = requests.get(WC + "/", headers=UA, timeout=40)
html = r.text

# asset urls con ?ver=
assets = re.findall(r'(https://victtorino\.cl/wp-content/plugins/[^"\']+?\?ver=[\d.]+)', html)
ver = defaultdict(set)
for a in assets:
    m = re.search(r'/plugins/([^/]+)/.*?\?ver=([\d.]+)', a)
    if m:
        ver[m.group(1)].add(m.group(2))

print("== Versiones detectadas por asset ?ver= (plugins en la home) ==")
for plug in sorted(ver):
    print(f"  {plug:35s} {', '.join(sorted(ver[plug]))}")

# meta generator
gens = re.findall(r'<meta name="generator" content="([^"]+)"', html)
print("\n== <meta generator> ==")
for g in gens:
    print(f"  {g}")

# elementor version a veces en comentario o data
for pat in [r'elementor[^"]*?ver=([\d.]+)', r'"elementorVersion":"([\d.]+)"',
            r'"proVersion":"([\d.]+)"', r'WooCommerce[^<]*?([\d.]+)']:
    m = re.findall(pat, html)
    if m:
        print(f"  pat {pat[:30]}: {set(m)}")

# readme de woocommerce (a veces accesible)
print("\n== Intento leer versiones por readme.txt ==")
for plug in ["woocommerce", "elementor", "elementor-pro"]:
    try:
        rr = requests.get(f"{WC}/wp-content/plugins/{plug}/readme.txt",
                          headers=UA, timeout=20)
        if rr.status_code == 200:
            mm = re.search(r"Stable tag:\s*([\d.]+)", rr.text)
            print(f"  {plug}: {mm.group(1) if mm else '(sin stable tag)'}")
        else:
            print(f"  {plug}: HTTP {rr.status_code}")
    except Exception as e:
        print(f"  {plug}: ERR {e}")
