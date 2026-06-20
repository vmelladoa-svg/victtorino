"""
Establece processing_time = 1 dia en todos los items activos de C1.
Razon: processing_time=None le dice a ML que el despacho es el mismo dia,
y cualquier envio al dia siguiente cuenta como demora.
Con processing_time=1, ordenes post-10am que van al dia siguiente estan dentro del SLA.
"""
import json, requests, time
from pathlib import Path

base = 'https://api.mercadolibre.com'
tokens = json.loads(Path('tokens_cuenta1.json').read_text())
h = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}

me = requests.get(f'{base}/users/me', headers=h).json()
uid = me['id']
print(f'Cuenta: {me.get("nickname")} (uid={uid})')

# Obtener todos los items
all_ids = []
offset = 0
while True:
    r = requests.get(f'{base}/users/{uid}/items/search', headers=h,
                     params={'offset': offset, 'limit': 50}).json()
    all_ids.extend(r.get('results', []))
    offset += 50
    if offset >= r.get('paging', {}).get('total', 0): break
    time.sleep(0.1)

print(f'Total IDs: {len(all_ids)}')

ok = 0
ya_ok = 0
errores = 0

for i in range(0, len(all_ids), 20):
    chunk = ','.join(all_ids[i:i+20])
    batch = requests.get(f'{base}/items', headers=h, params={'ids': chunk}).json()
    time.sleep(0.2)

    for entry in batch:
        if entry.get('code') != 200: continue
        b = entry['body']
        if b.get('status') != 'active': continue

        iid = b['id']
        current_pt = b.get('processing_time')

        if current_pt == 1:
            ya_ok += 1
            continue

        r = requests.put(f'{base}/items/{iid}', headers=h,
                         json={'processing_time': 1})
        if r.ok:
            ok += 1
        else:
            errores += 1
            try:
                msg = r.json().get('message', '')[:80]
            except Exception:
                msg = r.text[:80]
            if errores <= 5:
                print(f'  ERR {iid}: {msg}')
        time.sleep(0.25)

print(f'\nActualizados: {ok}')
print(f'Ya tenian 1 dia: {ya_ok}')
print(f'Errores: {errores}')
print('\nListo. Ahora ML contara como SLA cumplido cuando despachas al dia siguiente.')
