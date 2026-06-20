# -*- coding: utf-8 -*-
"""
Auditoria ML Ads en las 3 cuentas.
Revisa campanas activas, presupuesto, ROAS y estado.
"""
import json, requests, time
from pathlib import Path

base = 'https://api.mercadolibre.com'

cuentas = [
    ('C1', 'tokens_cuenta1.json'),
    ('C2', 'tokens_cuenta2.json'),
    ('C3', 'tokens_cuenta3.json'),
]

for nombre, token_file in cuentas:
    print(f'\n{"="*50}')
    print(f'ML ADS — {nombre}')
    print('='*50)

    tokens = json.loads(Path(token_file).read_text())
    h = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}

    me = requests.get(f'{base}/users/me', headers=h).json()
    uid = me['id']
    print(f'Cuenta: {me.get("nickname")} (uid={uid})')

    # Campanas activas
    r = requests.get(f'{base}/advertising/product_ads/{uid}/campaigns', headers=h).json()
    if isinstance(r, dict) and r.get('status') == 404:
        print('  Sin campanas configuradas')
        continue
    if isinstance(r, dict) and 'error' in r:
        print(f'  Error: {r.get("message", r)}')
        continue

    campaigns = r if isinstance(r, list) else r.get('campaigns', [])
    print(f'  Campanas encontradas: {len(campaigns)}')

    for c in campaigns:
        cid = c.get('id')
        status = c.get('status')
        name = c.get('name', '')
        budget = c.get('daily_budget', 0)
        print(f'\n  [{status}] {name} (id={cid})')
        print(f'    Presupuesto diario: ${budget:,.0f}')

        # Metricas de la campana
        time.sleep(0.2)
        metrics_r = requests.get(
            f'{base}/advertising/product_ads/{uid}/campaigns/{cid}/metrics',
            headers=h,
            params={'date_range': 'last_30_days'}
        ).json()

        if isinstance(metrics_r, dict) and not metrics_r.get('error'):
            impressions = metrics_r.get('impressions', 0)
            clicks = metrics_r.get('clicks', 0)
            spend = metrics_r.get('amount', 0)
            revenue = metrics_r.get('revenue', 0)
            orders = metrics_r.get('orders', 0)
            roas = (revenue / spend) if spend > 0 else 0
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            acos = (spend / revenue * 100) if revenue > 0 else 0

            print(f'    --- Ultimos 30 dias ---')
            print(f'    Impresiones: {impressions:,}')
            print(f'    Clicks: {clicks:,} | CTR: {ctr:.2f}%')
            print(f'    Gasto: ${spend:,.0f} | Ordenes: {orders}')
            print(f'    Revenue atribuido: ${revenue:,.0f}')
            print(f'    ROAS: {roas:.1f}x | ACOS: {acos:.1f}%')

            if roas < 3 and spend > 0:
                print(f'    ALERTA: ROAS {roas:.1f}x bajo el minimo (3x) — revisar pausar')
            elif roas > 7:
                print(f'    OPORTUNIDAD: ROAS {roas:.1f}x alto — considerar aumentar presupuesto')
        else:
            print(f'    Sin metricas disponibles: {metrics_r}')

        # Items en la campana
        time.sleep(0.2)
        items_r = requests.get(
            f'{base}/advertising/product_ads/{uid}/campaigns/{cid}/items',
            headers=h
        ).json()
        items_list = items_r if isinstance(items_r, list) else items_r.get('items', [])
        print(f'    Items en campana: {len(items_list)}')
        for it in items_list[:5]:
            print(f'      {it.get("item_id")} | bid=${it.get("bid",0):,.0f} | status={it.get("status")}')

    time.sleep(0.3)
