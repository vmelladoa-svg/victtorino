import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open(r"C:\Users\dell\victtorino\tokens_cuenta3.json") as f:
    tk = json.load(f)
H = {"Authorization": f"Bearer {tk['access_token']}"}
uid = tk["user_id"]

r = requests.get(f"https://api.mercadolibre.com/users/{uid}/items/search",
                 headers=H, params={"q": "plato ducha cuadrado", "status": "active"}, timeout=30)
ids = r.json().get("results", [])
print(f"matches en C3: {len(ids)}")
if ids:
    r2 = requests.get("https://api.mercadolibre.com/items", headers=H,
                      params={"ids": ",".join(ids[:10]),
                              "attributes": "id,title,price,available_quantity,permalink,pictures"},
                      timeout=30)
    for it in r2.json():
        if it.get("code") == 200:
            b = it["body"]
            print(f"  {b['id']}  ${b.get('price')} stock={b.get('available_quantity')} "
                  f"pics={len(b.get('pictures',[]))}  {b['title']}")
            print(f"    {b.get('permalink')}")
