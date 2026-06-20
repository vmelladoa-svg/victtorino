"""
Auditoria completa C3 (NOVAGRIFERIAS3):
- Reputacion
- Ventas (ultimos 60 dias)
- Preguntas sin responder
- Stock critico
- Rentabilidad (items en perdida o bajo margen)
- Rotacion (stock muerto)
"""
import json, requests, time
from pathlib import Path
from datetime import datetime, timedelta

base = 'https://api.mercadolibre.com'
tokens = json.loads(Path('tokens_cuenta3.json').read_text())
h = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}

me = requests.get(f'{base}/users/me', headers=h).json()
uid = me['id']
nickname = me.get('nickname', 'C3')
print(f'Cuenta: {nickname} (uid={uid})')

# =====================================================
# 1. REPUTACION
# =====================================================
print('\n=== 1. REPUTACION ===')
rep = me.get('seller_reputation', {})
level = rep.get('level_id', 'N/A')
transactions = rep.get('transactions', {})
total_tx = transactions.get('total', 0)
ratings = rep.get('ratings', {})
positive_pct = round(ratings.get('positive', 0) * 100, 1)
negative_pct = round(ratings.get('negative', 0) * 100, 1)
neutral_pct = round(ratings.get('neutral', 0) * 100, 1)
metrics = rep.get('metrics', {})
claims = metrics.get('claims', {})
delayed = metrics.get('delayed_handling_time', {})
cancels = metrics.get('cancellations', {})

print(f'  Nivel: {level}')
print(f'  Transacciones totales: {total_tx}')
print(f'  Calificaciones: +{positive_pct}% / -{negative_pct}% / ~{neutral_pct}%')
print(f'  Reclamos: {claims.get("rate", 0)*100:.2f}% (limite: {claims.get("value", "?")})')
print(f'  Demoras: {delayed.get("rate", 0)*100:.2f}% (limite: {delayed.get("value", "?")})')
print(f'  Cancelaciones: {cancels.get("rate", 0)*100:.2f}% (limite: {cancels.get("value", "?")})')

rep_ok = True
for name, m in [('Reclamos', claims), ('Cancelaciones', cancels), ('Demoras', delayed)]:
    rate = m.get('rate', 0)
    limit = m.get('value', 999)
    if isinstance(limit, (int, float)) and rate > limit:
        print(f'  [ALERTA] {name} sobre el limite!')
        rep_ok = False
if rep_ok:
    print('  Reputacion OK - todos los indicadores dentro de limites')

# =====================================================
# 2. VENTAS - ultimos 60 dias
# =====================================================
print('\n=== 2. VENTAS ULTIMOS 60 DIAS ===')
fecha_desde = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT00:00:00.000-03:00')
fecha_hasta = datetime.now().strftime('%Y-%m-%dT23:59:59.000-03:00')

orders = []
offset = 0
while True:
    r = requests.get(f'{base}/orders/search', headers=h, params={
        'seller': uid, 'order.status': 'paid',
        'order.date_created.from': fecha_desde,
        'order.date_created.to': fecha_hasta,
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

# Top 10 items mas vendidos
from collections import defaultdict
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
# 3. PREGUNTAS SIN RESPONDER
# =====================================================
print('\n=== 3. PREGUNTAS SIN RESPONDER ===')
r = requests.get(f'{base}/my/received_questions/search', headers=h,
                 params={'status': 'UNANSWERED', 'limit': 50}).json()
q_unanswered = r.get('questions', [])
print(f'  Total sin responder: {len(q_unanswered)}')
for q in q_unanswered[:5]:
    item_id = q.get('item_id', '')
    text = q.get('text', '')[:80]
    date = q.get('date_created', '')[:10]
    print(f'    [{date}] {item_id}: {text}')
if len(q_unanswered) > 5:
    print(f'    ... y {len(q_unanswered)-5} mas')

# =====================================================
# 4. STOCK CRITICO
# =====================================================
print('\n=== 4. STOCK CRITICO ===')
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
                'category': b.get('category_id', ''),
                'catalog': bool(b.get('catalog_product_id')),
                'has_bids': b.get('has_bids', False),
            })
    time.sleep(0.2)

print(f'  Items activos totales: {len(items_data)}')

# Calcular velocidad de ventas por item
vel_ventas = {iid: d['qty'] for iid, d in ventas_por_item.items()}

criticos = []
sin_stock = []
muertos = []

for it in items_data:
    vel = vel_ventas.get(it['id'], 0)
    stock = it['stock']
    dias_stock = (stock / (vel / 60)) if vel > 0 else 9999

    if stock == 0:
        sin_stock.append(it)
    elif stock <= 3 and vel >= 3:
        criticos.append({**it, 'vel': vel, 'dias_stock': round(dias_stock, 1)})
    elif vel == 0 and stock >= 20:
        muertos.append({**it, 'vel': vel})

print(f'  Stock = 0: {len(sin_stock)} items')
print(f'  Stock critico (<=3u, >=3 ventas/60d): {len(criticos)} items')
print(f'  Stock muerto (>=20u, 0 ventas/60d): {len(muertos)} items')

if criticos:
    print('\n  Criticos - reponer urgente:')
    for it in sorted(criticos, key=lambda x: x['dias_stock'])[:10]:
        print(f'    {it["id"]}: stock={it["stock"]}u, vel={it["vel"]}u/60d, ~{it["dias_stock"]}d restantes - {it["title"]}')

if muertos:
    print('\n  Stock muerto - revisar precio:')
    for it in sorted(muertos, key=lambda x: x['stock'], reverse=True)[:5]:
        print(f'    {it["id"]}: {it["stock"]}u - ${it["price"]:,.0f} - {it["title"]}')

# =====================================================
# 5. RENTABILIDAD - items con precio bajo (flag)
# =====================================================
print('\n=== 5. RENTABILIDAD ===')
MULTIPLICADOR = 1.34  # 34% cargos ML + margen minimo 15%

# Sin costos reales, estimamos precio minimo = precio / (1 - 0.34 - 0.15) = precio / 0.51
# Si precio < costo estimado × multiplicador, hay riesgo
# Como no tenemos costos en C3, mostramos items con precio muy bajo vs ventas altas
print('  (Sin datos de costo en C3 - mostrando items de alto riesgo por precio bajo)')
precios_bajos = [it for it in items_data if it['price'] < 5000 and vel_ventas.get(it['id'], 0) > 0]
print(f'  Items con precio < $5.000 y con ventas: {len(precios_bajos)}')
for it in precios_bajos[:8]:
    vel = vel_ventas.get(it['id'], 0)
    print(f'    {it["id"]}: ${it["price"]:,.0f} - {vel}u/60d - {it["title"]}')

# =====================================================
# 6. ROTACION - oportunidades de mejora
# =====================================================
print('\n=== 6. ROTACION Y OPTIMIZACION ===')

# Items con pocas fotos
pocas_fotos = [it for it in items_data if it['pics'] < 4]
print(f'  Items con < 4 fotos: {len(pocas_fotos)}')
for it in sorted(pocas_fotos, key=lambda x: vel_ventas.get(x['id'], 0), reverse=True)[:5]:
    vel = vel_ventas.get(it['id'], 0)
    print(f'    {it["id"]}: {it["pics"]} fotos, {vel}u/60d - {it["title"]}')

# Items de alto stock y bajo movimiento (candidatos a promocion)
promo_candidates = [it for it in items_data
                    if it['stock'] >= 10 and 0 < vel_ventas.get(it['id'], 0) < 3]
print(f'\n  Stock alto (>=10) + ventas bajas (1-2/60d): {len(promo_candidates)}')
for it in sorted(promo_candidates, key=lambda x: x['stock'], reverse=True)[:5]:
    vel = vel_ventas.get(it['id'], 0)
    print(f'    {it["id"]}: {it["stock"]}u stock, {vel}u/60d - ${it["price"]:,.0f} - {it["title"]}')

# =====================================================
# RESUMEN EJECUTIVO
# =====================================================
print('\n=== RESUMEN EJECUTIVO C3 ===')
print(f'  Cuenta: {nickname}')
print(f'  Nivel reputacion: {level}')
print(f'  Ventas 60d: {total_ventas} ordenes | ${revenue:,.0f} CLP')
print(f'  Preguntas sin responder: {len(q_unanswered)}')
print(f'  Items activos: {len(items_data)}')
print(f'  Stock critico (reposicion urgente): {len(criticos)}')
print(f'  Stock agotado: {len(sin_stock)}')
print(f'  Stock muerto: {len(muertos)}')
print(f'  Items < 4 fotos: {len(pocas_fotos)}')
