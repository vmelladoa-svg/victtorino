import json, requests
from pathlib import Path

base = 'https://api.mercadolibre.com'
h = {'Authorization': 'Bearer ' + json.loads(Path('tokens_cuenta1.json').read_text())['access_token'],
     'Content-Type': 'application/json'}

# Probar distintos campos para handling time
iid = 'MLC911087202'

r1 = requests.get(f'{base}/items/{iid}', headers=h).json()
print(f'processing_time actual: {r1.get("processing_time")}')
print(f'shipping: {json.dumps(r1.get("shipping", {}), indent=2)[:400]}')
print()

# Intentar con processing_time
r = requests.put(f'{base}/items/{iid}', headers=h, json={'processing_time': 1})
print(f'processing_time=1 -> {r.status_code}: {r.text[:200]}')

# Intentar con handling_time dentro de shipping
r2 = requests.put(f'{base}/items/{iid}', headers=h,
                  json={'shipping': {'handling_time': 1}})
print(f'shipping.handling_time=1 -> {r2.status_code}: {r2.text[:200]}')
