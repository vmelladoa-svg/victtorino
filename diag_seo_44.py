"""
Diagnostica SEO de los 44 productos del lote NO + reparados.
Identifica los debiles (focus count <=3, palabras <280) para retocar.
"""
import re
import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

IDS = [2719, 2727, 2734, 2739, 2746, 2762, 2765, 2770, 2778, 2783,
       2793, 2797, 2803, 2816, 2824, 2828, 2834, 2838, 2844, 2852,
       2857, 2865, 2868, 2873, 2876, 2885, 2892, 2896, 2901, 2909,
       2914, 2923, 2926, 2938, 2947, 2960, 2963, 2968, 2975, 2983,
       2992, 2999, 3009, 3024]

print(f"{'ID':5} {'pal':5} {'fk#':4} {'lnk':4} {'H2':3} {'meta':4} {'focus':30} titulo")
print("-" * 120)

debiles = []
for pid in IDS:
    r = requests.get(f"{WC}/wp-json/wc/v3/products/{pid}", params=P, timeout=30)
    if r.status_code != 200:
        print(f"{pid}: HTTP {r.status_code}")
        continue
    d = r.json()
    desc = d.get("description", "")
    plain = re.sub(r"<[^>]+>", " ", desc)
    plain = re.sub(r"\s+", " ", plain).strip()
    palabras = len(plain.split())

    m = {x["key"]: x["value"] for x in d.get("meta_data", []) if "rank_math" in x["key"]}
    fk = m.get("rank_math_focus_keyword", "").lower()
    fk_count = plain.lower().count(fk) if fk else 0

    links = desc.count('href="')
    h2 = re.findall(r"<h2[^>]*>([^<]+)</h2>", desc)
    h2_fk = "SI" if fk and any(fk in h.lower() for h in h2) else "no"
    meta_d = m.get("rank_math_description", "")
    meta_fk = "SI" if fk and fk in meta_d.lower() else "no"

    nombre = d.get("name", "")[:38]
    print(f"{pid:5} {palabras:5} {fk_count:4} {links:4} {h2_fk:3} {meta_fk:4} {fk[:30]:30} {nombre}")

    # Criterio: focus count <=3 o palabras <280 o focus no en H2 o focus no en meta_desc
    if fk_count <= 3 or palabras < 280 or h2_fk == "no" or meta_fk == "no":
        debiles.append({"pid": pid, "name": d["name"], "palabras": palabras,
                        "fk": fk, "fk_count": fk_count, "h2_fk": h2_fk, "meta_fk": meta_fk})

print()
print(f"DÉBILES: {len(debiles)} / {len(IDS)}")
print("=" * 70)
for d in debiles:
    print(f"  {d['pid']:5} pal={d['palabras']:3} fk={d['fk_count']:2} focus='{d['fk']}'  {d['name'][:50]}")

with open(r"C:\Users\dell\victtorino\diag_seo_44.json", "w", encoding="utf-8") as f:
    json.dump(debiles, f, ensure_ascii=False, indent=2)
