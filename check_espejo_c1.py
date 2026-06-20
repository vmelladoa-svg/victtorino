import json, requests
from pathlib import Path
base = 'https://api.mercadolibre.com'
h = {'Authorization': 'Bearer ' + json.loads(Path('tokens_cuenta1.json').read_text())['access_token']}

me = requests.get(f'{base}/users/me', headers=h).json()
uid = me['id']

all_ids = []
offset = 0
while True:
    r = requests.get(f'{base}/users/{uid}/items/search', headers=h, params={'offset': offset, 'limit': 50}).json()
    all_ids.extend(r.get('results', []))
    offset += 50
    if offset >= r.get('paging', {}).get('total', 0): break

print(f'Total IDs: {len(all_ids)}')

# Buscar espejos redondos y ver handling time
for i in range(0, len(all_ids), 20):
    chunk = ','.join(all_ids[i:i+20])
    batch = requests.get(f'{base}/items', headers=h, params={'ids': chunk}).json()
    for entry in batch:
        if entry.get('code') == 200:
            b = entry['body']
            t = b.get('title', '').lower()
            if 'espejo' in t and ('doble' in t or 'aumento' in t):
                print(f'\n{b["id"]} | status={b.get("status")} | stock={b.get("available_quantity")} | ${b.get("price")}')
                print(f'  Titulo: {b.get("title")}')
                print(f'  processing_time: {b.get("processing_time")}')

# Muestra de handling time en items activos
print('\n--- Handling times muestra ---')
sample_batch = requests.get(f'{base}/items', headers=h, params={'ids': ','.join(all_ids[:10])}).json()
for entry in sample_batch:
    if entry.get('code') == 200:
        b = entry['body']
        if b.get('status') == 'active':
            pt = b.get('processing_time', 'N/A')
            print(f'  {b["id"]} | processing_time={pt} | {b.get("title","")[:40]}')
