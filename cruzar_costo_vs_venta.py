# -*- coding: utf-8 -*-
"""Cruza costos Defontana (costos_defontana_limpio) con precios de venta web (catalogo-trade.csv)."""
import pandas as pd, warnings
warnings.filterwarnings('ignore')

IVA = 1.19
OUT = r'C:\Users\dell\victtorino\costos_vs_precios_venta.xlsx'

costos = pd.read_excel('costos_defontana_limpio.xlsx')
costos['Codigo'] = costos['Codigo'].astype(str).str.strip()

web = pd.read_csv('catalogo-trade.csv', header=None, dtype=str, keep_default_na=False)
web = web[[2, 4, 25, 26]].copy()
web.columns = ['Codigo', 'Nombre_web', 'precio_oferta', 'precio_normal']
web['Codigo'] = web['Codigo'].str.strip()

def num(v):
    v = str(v).strip().replace('.', '').replace(',', '')
    return int(v) if v.isdigit() else None

web['oferta'] = web['precio_oferta'].map(num)
web['normal'] = web['precio_normal'].map(num)
# precio de venta efectivo = oferta si existe (>0) si no el normal
web['Precio venta web (IVA)'] = web['oferta'].where(web['oferta'].fillna(0) > 0, web['normal'])
web = web.drop_duplicates('Codigo', keep='first')

m = costos.merge(web[['Codigo', 'Nombre_web', 'Precio venta web (IVA)']], on='Codigo', how='left')

pv = m['Precio venta web (IVA)']
costo = m['Costo compra (CLP)']
m['Precio neto (sin IVA)'] = (pv / IVA).round(0)
m['Margen CLP'] = (m['Precio neto (sin IVA)'] - costo).round(0)
m['Margen %'] = ((m['Margen CLP'] / m['Precio neto (sin IVA)']) * 100).round(1)
markup = m['Precio neto (sin IVA)'] / costo.replace(0, pd.NA)
m['Markup x'] = pd.to_numeric(markup, errors='coerce').round(2)

cols = ['Codigo', 'Descripcion', 'Nombre_web', 'Costo compra (CLP)',
        'Precio venta web (IVA)', 'Precio neto (sin IVA)', 'Margen CLP', 'Margen %', 'Markup x']
m = m[cols].sort_values('Margen %', na_position='last')

con = m['Precio venta web (IVA)'].notna()
m.to_excel(OUT, index=False)

print(f'Costos totales:            {len(costos)}')
print(f'Con precio de venta web:   {con.sum()}')
print(f'Sin match en web:          {(~con).sum()}')
neg = m[(m['Margen CLP'] < 0) & con]
print(f'\nMargen NEGATIVO (vende bajo costo): {len(neg)}')
if len(neg):
    print(neg[['Codigo','Descripcion','Costo compra (CLP)','Precio venta web (IVA)','Margen CLP','Margen %']].to_string(index=False))
print('\n--- 8 margenes mas bajos (con precio) ---')
print(m[con].head(8)[['Codigo','Descripcion','Costo compra (CLP)','Precio neto (sin IVA)','Margen %','Markup x']].to_string(index=False))
print('\n--- sin match en web (primeros 10) ---')
print(m[~con].head(10)[['Codigo','Descripcion','Costo compra (CLP)']].to_string(index=False))
print('\nGenerado:', OUT)
