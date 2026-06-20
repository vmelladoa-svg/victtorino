#!/usr/bin/env python3
# Empuja las descripciones humanizadas a WooCommerce.
# Uso: python hum_push.py CK CS   (claves R/W)
import sys, json, time, urllib.request, urllib.parse

BASE = "https://tradeglobalchile.cl"
CK, CS = sys.argv[1], sys.argv[2]
data = json.load(open("hum_final.json", encoding="utf-8"))

ok = err = 0
for pid, v in data.items():
    body = json.dumps({"description": v["long"], "short_description": v["short"]}).encode()
    qs = urllib.parse.urlencode({"consumer_key": CK, "consumer_secret": CS})
    url = f"{BASE}/wp-json/wc/v3/products/{pid}?{qs}"
    req = urllib.request.Request(url, data=body, method="PUT",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read(); ok += 1; print(f"OK  {pid}")
    except Exception as e:
        err += 1; print(f"ERR {pid}: {e}")
    time.sleep(0.3)  # ponytail: serial + sleep evita rate-limit; paraleliza si 66 fueran miles

print(f"\nListo: {ok} actualizados, {err} con error")
