"""
Obtiene el precio de mercado actual en MercadoLibre para los productos de alila
cuyo ml_lj apunta a un producto de catalogo (/p/MLC...) o user product (/up/MLCU...).
Usa la API /products/{id}/items (token ML cuenta C3). Cachea en alila_precio_mercado.json.
Salida final: actualiza el cruce con margen de reventa.
"""
import json, requests, re, time, pandas as pd
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
CACHE = ROOT / "alila_precio_mercado.json"
tok = json.load(open(ROOT / "tokens_cuenta3.json"))["access_token"]
HA = {"Authorization": f"Bearer {tok}"}

def extract_id(u):
    if not isinstance(u, str): return None
    m = re.search(r'/p/(MLC\d+)', u) or re.search(r'/up/(MLCU\d+)', u)
    return m.group(1) if m else None

def market(pid):
    """devuelve dict con precio min/median y n ofertas, o None."""
    for intento in range(3):
        try:
            r = requests.get(f"https://api.mercadolibre.com/products/{pid}/items",
                             params={"limit": 50}, headers=HA, timeout=20)
            if r.status_code == 429:
                time.sleep(2); continue
            if r.status_code != 200:
                return {"status": r.status_code}
            res = r.json().get("results", []) or []
            precios = [it.get("price") for it in res
                       if it.get("price") and it.get("condition") == "new"]
            if not precios:
                precios = [it.get("price") for it in res if it.get("price")]
            if not precios:
                return {"status": "sin_precio"}
            precios.sort()
            n = len(precios)
            return {"status": 200, "precio_min": precios[0],
                    "precio_mediano": precios[n // 2], "n_ofertas": n}
        except Exception as e:
            time.sleep(1)
    return {"status": "error"}

if __name__ == "__main__":
    al = pd.read_excel(ROOT / "alila_app_catalogo.xlsx")
    al["mkt_id"] = al["Link MercadoLibre"].apply(extract_id)
    ids = [i for i in al["mkt_id"].dropna().unique().tolist()]
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    print(f"IDs de mercado a consultar: {len(ids)} | ya en cache: {len(cache)}")
    pend = [i for i in ids if i not in cache]
    print(f"Pendientes: {len(pend)}")
    for k, pid in enumerate(pend, 1):
        cache[pid] = market(pid)
        if k % 100 == 0:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False))
            ok = sum(1 for v in cache.values() if v.get("status") == 200)
            print(f"  {k}/{len(pend)} consultados | con precio: {ok}")
        time.sleep(0.08)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False))
    ok = sum(1 for v in cache.values() if v.get("status") == 200)
    print(f"=== Precios obtenidos: {ok}/{len(ids)} -> {CACHE.name} ===")
