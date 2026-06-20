"""Capturar el error 500 del REST y probar endpoints."""
import sys, io, re, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}
UA = {"User-Agent": "Mozilla/5.0"}

endpoints = [
    "/wp-json/",
    "/wp-json/wc/v3/system_status",
    "/wp-json/wc/v3/products?per_page=1",
    "/wp-json/wc/v3/products/categories?per_page=1",
    "/wp-json/wp/v2/posts?per_page=1",
]
for ep in endpoints:
    try:
        r = requests.get(WC + ep, params=P, headers=UA, timeout=60)
        print(f"\n{'='*60}\n{ep}  ->  HTTP {r.status_code}  ({len(r.content)}b)")
        ct = r.headers.get("Content-Type", "")
        print(f"  Content-Type: {ct}")
        if r.status_code != 200:
            # buscar mensajes de error PHP / fatal en el HTML
            txt = r.text
            for pat in [r"Fatal error.{0,300}", r"Parse error.{0,200}",
                        r"Cannot redeclare.{0,200}", r"Uncaught.{0,300}",
                        r"on line \d+", r"in /.{0,120}\.php",
                        r'"message":"[^"]{0,300}"', r'"code":"[^"]{0,100}"',
                        r"memory size of \d+ bytes exhausted.{0,120}"]:
                for m in re.findall(pat, txt):
                    print(f"  >> {m.strip()}")
            # primeras lineas legibles
            limpio = re.sub(r"<[^>]+>", " ", txt)
            limpio = re.sub(r"\s+", " ", limpio).strip()
            print(f"  texto: {limpio[:400]}")
        else:
            print(f"  OK (primeros 120b): {r.text[:120]}")
    except Exception as e:
        print(f"\n{ep}: ERROR {e}")
