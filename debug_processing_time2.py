import json, requests
from pathlib import Path

base = 'https://api.mercadolibre.com'
h = {'Authorization': 'Bearer ' + json.loads(Path('tokens_cuenta1.json').read_text())['access_token'],
     'Content-Type': 'application/json'}

# Usar item sin bids
iid = 'MLC579967481'  # Item que tuvo pocas fotos, deberia ser sin bids

r1 = requests.get(f'{base}/items/{iid}', headers=h).json()
print(f'Status: {r1.get("status")} | has_bids: {r1.get("has_bids")}')
print(f'processing_time actual: {r1.get("processing_time")}')

# Intentar actualizar
r = requests.put(f'{base}/items/{iid}', headers=h, json={'processing_time': 1})
print(f'processing_time=1 -> {r.status_code}: {r.text[:300]}')

# Ver que campos retorna el error
try:
    err = r.json()
    for cause in err.get('cause', []):
        print(f'  cause: {cause}')
except Exception:
    pass

# Intentar con un item que definitivamente sea activo y sin bids
iid2 = 'MLC3518310792'
r2 = requests.get(f'{base}/items/{iid2}', headers=h).json()
print(f'\n{iid2}: Status={r2.get("status")} | has_bids={r2.get("has_bids")}')
r3 = requests.put(f'{base}/items/{iid2}', headers=h, json={'processing_time': 1})
print(f'processing_time=1 -> {r3.status_code}: {r3.text[:300]}')
