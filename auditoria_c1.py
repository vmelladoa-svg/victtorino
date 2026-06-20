# -*- coding: utf-8 -*-
"""
Auditoria completa C1 (PREMIUMGRIFERIAS1):
- Ventas (60 dias)
- Preguntas sin responder
- Stock critico
- Rentabilidad (precios bajos)
- Rotacion (stock muerto, pocas fotos)
"""
import json, requests, time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter

base = 'https://api.mercadolibre.com'
tokens = json.loads(Path('tokens_cuenta1.json').read_text())
h = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}

me = requests.get(f'{base}/users/me', headers=h).json()
uid = me['id']
nickname = me.get('nickname', 'C1')
print(f'Cuenta: {nickname} (uid={uid})')

# =====================================================
# 1. VENTAS - ultimos 60 dias
# =====================================================
print('\n=== 1. VENTAS ULTIMOS 60 DIAS ===')
fecha_desde = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT00:00:00.000-03:00')

orders = []
offset = 0
while True:
    r = requests.get(f'{base}/orders/search', headers=h, params={
        'seller': uid, 'order.status': 'paid',
        'order.date_created.from': fecha_desde,
        'offset': offset, 'limit': 50
    }).json()
    batch = r.get('results', [])
    orders.extend(batch)
    offset += 50
    if offset >= r.get('paging', {}).get('total', 0): break
    time.sleep(0.2)

total_ventas = len(orders)
revenue = sum(o.get('total_amount', 0) for o in orders)
print(f'  Ordenes pagadas: {total_ventas}')
print(f'  Facturacion: ${revenue:,.0f} CLP')

ventas_por_item = defaultdict(lambda: {'qty': 0, 'revenue': 0, 'title': ''})
for o in orders:
    for it in o.get('order_items', []):
        iid = it['item']['id']
        ventas_por_item[iid]['qty'] += it.get('quantity', 1)
        ventas_por_item[iid]['revenue'] += it.get('unit_price', 0) * it.get('quantity', 1)
        ventas_por_item[iid]['title'] = it['item'].get('title', '')[:45]

top10 = sorted(ventas_por_item.items(), key=lambda x: x[1]['qty'], reverse=True)[:10]
print(f'\n  Top 10 mas vendidos:')
for iid, d in top10:
    print(f'    {iid}: {d["qty"]}u - ${d["revenue"]:,.0f} - {d["title"]}')

# =====================================================
# 2. PREGUNTAS SIN RESPONDER
# =====================================================
print('\n=== 2. PREGUNTAS SIN RESPONDER ===')
r = requests.get(f'{base}/my/received_questions/search', headers=h,
                 params={'status': 'UNANSWERED', 'limit': 50}).json()
q_unanswered = r.get('questions', [])
print(f'  Total sin responder: {len(q_unanswered)}')
for q in q_unanswered[:8]:
    item_id = q.get('item_id', '')
    text = q.get('text', '')[:80]
    date = q.get('date_created', '')[:10]
    print(f'    [{date}] {item_id}: {text}')
if len(q_unanswered) > 8:
    print(f'    ... y {len(q_unanswered)-8} mas')

# =====================================================
# 3. CARGAR TODOS LOS ITEMS ACTIVOS
# =====================================================
print('\n  Cargando items activos...')
all_ids = []
offset = 0
while True:
    r = requests.get(f'{base}/users/{uid}/items/search', headers=h,
                     params={'offset': offset, 'limit': 50}).json()
    all_ids.extend(r.get('results', []))
    offset += 50
    if offset >= r.get('paging', {}).get('total', 0): break
    time.sleep(0.1)

items_data = []
for i in range(0, len(all_ids), 20):
    chunk = ','.join(all_ids[i:i+20])
    r = requests.get(f'{base}/items', headers=h, params={'ids': chunk}).json()
    for entry in r:
        if entry.get('code') == 200 and entry['body'].get('status') == 'active':
            b = entry['body']
            sku = b.get('seller_custom_field') or ''
            if not sku:
                for attr in b.get('attributes', []):
                    if attr.get('id') == 'SELLER_SKU':
                        sku = attr.get('value_name', '')
                        break
            items_data.append({
                'id': b['id'],
                'title': b.get('title', '')[:50],
                'sku': sku,
                'stock': b.get('available_quantity', 0),
                'price': b.get('price', 0),
                'pics': len(b.get('pictures', [])),
                'attrs': len(b.get('attributes', [])),
                'has_bids': b.get('has_bids', False),
                'catalog': bool(b.get('catalog_product_id')),
            })
    time.sleep(0.2)

print(f'  Items activos: {len(items_data)}')

# =====================================================
# 4. STOCK CRITICO
# =====================================================
print('\n=== 3. STOCK CRITICO ===')
vel_ventas = {iid: d['qty'] for iid, d in ventas_por_item.items()}

sin_stock = []
criticos = []
muertos = []

for it in items_data:
    vel = vel_ventas.get(it['id'], 0)
    stock = it['stock']
    dias_stock = (stock / (vel / 60)) if vel > 0 else 9999

    if stock == 0:
        sin_stock.append(it)
    elif stock <= 3 and vel >= 3:
        criticos.append({**it, 'vel': vel, 'dias_stock': round(dias_stock, 1)})
    elif vel == 0 and stock >= 15:
        muertos.append({**it, 'vel': vel})

print(f'  Stock = 0: {len(sin_stock)} items activos sin stock')
print(f'  Stock critico (<=3u, >=3 ventas/60d): {len(criticos)} items')
print(f'  Stock muerto (>=15u, 0 ventas/60d): {len(muertos)} items')

if criticos:
    print('\n  Criticos - reponer urgente:')
    for it in sorted(criticos, key=lambda x: x['dias_stock'])[:10]:
        print(f'    {it["id"]}: stock={it["stock"]}u, vel={it["vel"]}u/60d, ~{it["dias_stock"]}d - {it["title"]}')

if sin_stock[:5]:
    print('\n  Sin stock (activos - posible error):')
    for it in sin_stock[:5]:
        vel = vel_ventas.get(it['id'], 0)
        print(f'    {it["id"]}: vel={vel}u/60d - {it["title"]}')

if muertos:
    print('\n  Stock muerto - revisar precio/visibilidad:')
    for it in sorted(muertos, key=lambda x: x['stock'], reverse=True)[:5]:
        print(f'    {it["id"]}: {it["stock"]}u - ${it["price"]:,.0f} - {it["title"]}')

# =====================================================
# 5. RENTABILIDAD - items con precio potencialmente bajo
# =====================================================
print('\n=== 4. RENTABILIDAD ===')
print('  (Sin datos de costo C1 - mostrando items con precio < $5.000 y con ventas)')
precios_bajos = [it for it in items_data if it['price'] < 5000 and vel_ventas.get(it['id'], 0) > 0]
print(f'  Items precio < $5.000 con ventas: {len(precios_bajos)}')
for it in sorted(precios_bajos, key=lambda x: vel_ventas.get(x['id'], 0), reverse=True)[:8]:
    vel = vel_ventas.get(it['id'], 0)
    cargo_ml = it['price'] * 0.34
    print(f'    {it["id"]}: ${it["price"]:,.0f} | cargo ML=${cargo_ml:,.0f} | {vel}u/60d - {it["title"]}')

# =====================================================
# 6. ROTACION Y OPTIMIZACION
# =====================================================
print('\n=== 5. ROTACION Y OPTIMIZACION ===')

pocas_fotos = [it for it in items_data if it['pics'] < 4]
print(f'  Items con < 4 fotos: {len(pocas_fotos)}')
for it in sorted(pocas_fotos, key=lambda x: vel_ventas.get(x['id'], 0), reverse=True)[:5]:
    vel = vel_ventas.get(it['id'], 0)
    print(f'    {it["id"]}: {it["pics"]} fotos, {vel}u/60d - {it["title"]}')

promo_candidates = [it for it in items_data
                    if it['stock'] >= 10 and 0 < vel_ventas.get(it['id'], 0) < 3]
print(f'\n  Stock alto (>=10) + ventas bajas (1-2/60d): {len(promo_candidates)}')
for it in sorted(promo_candidates, key=lambda x: x['stock'], reverse=True)[:5]:
    vel = vel_ventas.get(it['id'], 0)
    print(f'    {it["id"]}: {it["stock"]}u, {vel}u/60d - ${it["price"]:,.0f} - {it["title"]}')

# =====================================================
# RESUMEN EJECUTIVO
# =====================================================
print('\n=== RESUMEN EJECUTIVO C1 ===')
print(f'  Cuenta: {nickname}')
print(f'  Ventas 60d: {total_ventas} ordenes | ${revenue:,.0f} CLP')
print(f'  Preguntas sin responder: {len(q_unanswered)}')
print(f'  Items activos: {len(items_data)}')
print(f'  Stock = 0 (activos): {len(sin_stock)}')
print(f'  Stock critico: {len(criticos)}')
print(f'  Stock muerto: {len(muertos)}')
print(f'  Items < 4 fotos: {len(pocas_fotos)}')
print(f'  Precio bajo con ventas: {len(precios_bajos)}')
