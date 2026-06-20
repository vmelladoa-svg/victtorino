"""
Audita Ventas mensuales (GMV) por cuenta via API de ordenes.
Uso: python auditoria_costos_mensual.py <tokens_file>
Suma total_amount de ordenes pagadas, agrupado por mes (2026 Ene - Jun 11).
"""
import json, requests, sys, time
from collections import defaultdict

base = 'https://api.mercadolibre.com'
tok_file = sys.argv[1] if len(sys.argv) > 1 else 'tokens_cuenta3.json'
t = json.load(open(tok_file))
h = {'Authorization': 'Bearer ' + t['access_token']}
uid = t['user_id']

me = requests.get(f'{base}/users/me', headers=h)
print(f'Cuenta: {me.json().get("nickname")} (uid={uid}) | token {tok_file}')

desde = '2026-01-01T00:00:00.000-03:00'
hasta = '2026-06-11T23:59:59.000-03:00'

orders = []
offset = 0
while True:
    r = requests.get(f'{base}/orders/search', headers=h, params={
        'seller': uid, 'order.status': 'paid',
        'order.date_created.from': desde, 'order.date_created.to': hasta,
        'sort': 'date_asc', 'offset': offset, 'limit': 50
    })
    if r.status_code != 200:
        print('ERR orders', r.status_code, r.text[:200]); break
    j = r.json()
    batch = j.get('results', [])
    orders.extend(batch)
    total = j.get('paging', {}).get('total', 0)
    offset += 50
    if offset >= total or not batch:
        break
    time.sleep(0.3)

print(f'Ordenes pagadas: {len(orders)}')

por_mes = defaultdict(lambda: {'ventas': 0.0, 'n': 0})
for o in orders:
    mes = o.get('date_created', '')[:7]  # YYYY-MM
    por_mes[mes]['ventas'] += o.get('total_amount', 0) or 0
    por_mes[mes]['n'] += 1

print('\nMes      | Ordenes | Ventas (total_amount)')
tot = 0
for mes in sorted(por_mes):
    d = por_mes[mes]
    tot += d['ventas']
    print(f'{mes}  | {d["n"]:>6}  | ${d["ventas"]:>14,.0f}')
print(f'TOTAL    |         | ${tot:>14,.0f}')

# guardar crudo para reuso
json.dump([{'id':o.get('id'),'date':o.get('date_created'),'total':o.get('total_amount'),
            'items':[{'item':it['item']['id'],'qty':it.get('quantity'),
                      'unit_price':it.get('unit_price'),'sale_fee':it.get('sale_fee')}
                     for it in o.get('order_items',[])]} for o in orders],
          open(f'orders_{uid}.json','w'), ensure_ascii=False)
print(f'\nGuardado orders_{uid}.json')
