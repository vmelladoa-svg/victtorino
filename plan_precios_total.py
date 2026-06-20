# -*- coding: utf-8 -*-
"""Consolida stock+precio del Administrador (12 paginas) + costos + estandar TAUMM,
y clasifica TODO el catalogo Falabella para cerrar precios hoy."""
import json, re, glob, openpyxl

def load(f):
    raw = open(f, encoding='utf-8').read().strip()
    d = json.loads(raw)
    if isinstance(d, str): d = json.loads(d)
    return d

# 1) Admin consolidado (stock/precio/special/sponsored) por SKU
admin = {}
for f in sorted(glob.glob('admin_p*.json')):
    d = load(f)
    rows = d['rows'] if isinstance(d, dict) and 'rows' in d else d
    for r in rows:
        admin[r['seller']] = r
print('Admin: productos unicos =', len(admin))
con_stock = {k: v for k, v in admin.items() if v.get('stock') and v['stock'] > 0}
print('con stock > 0 =', len(con_stock))

# 2) Master: costo c/IVA, venta 1.8, descripcion
ws = openpyxl.load_workbook('precios_descuentos_falabella.xlsx', data_only=True).active
rows = list(ws.iter_rows(values_only=True)); H = rows[0]
ic = H.index('Costo c/IVA'); idesc = H.index('Descripcion'); iv18 = H.index('VENTA real (oferta)')
master = {}
for r in rows[1:]:
    if isinstance(r[ic], (int, float)):
        master[r[0]] = {'civa': r[ic], 'desc': r[idesc], 'v18': r[iv18]}

# 3) Catalogo TAUMM competidores
taumm = []
for f in sorted(glob.glob('taumm_[0-9].json')):
    try: taumm += load(f)
    except Exception: pass
comp = [c for c in taumm if 'Trade' not in c.get('seller', '')]

MODELOS = ['NOTTE','COLOMBA','DOMENICA','VANDER','MODERN','BONN','SWERTT','ANTONELLA','MILAN',
           'PROFESIONAL','TEMPORIZADA','CISNE','VERTICAL','ALTO','BIDET','MONOBLOCK','LAVACOPA','EXTRAIBLE','CUELLO']
TIPOS = ['LAVAPLATO','LAVATORIO','LAVAMANOS','DUCHA','TINA','BIDET','LAVACOPA','JARDIN','ANGULAR']
MS = set(MODELOS)
def toks(n):
    n = n.upper(); s = set()
    for m in MODELOS:
        if m in n: s.add(m)
    for t in TIPOS:
        if t in n: s.add(t)
    return s
def r990(x):
    x = int(round(x)); return (x//1000)*1000+990 if x >= 1000 else max(0, x)

def taumm_price(desc):
    mt = toks(desc); my = mt & MS; best = None
    for c in comp:
        ct = toks(c['name'])
        if mt and len(mt & ct) >= 2 and (not my or (my & ct)):
            if best is None or c['price'] < best['price']: best = c
    return best

# 4) Clasificar SOLO los que tienen stock y estan en master
GRIF = re.compile(r'MONOMANDO|LLAVE|GRIFO|MONOBLOCK|LAVACOPA')
griferia, commodity, flag_alto = [], [], []
for sku, a in con_stock.items():
    m = master.get(sku)
    if not m: continue
    cur = a.get('special') or a.get('price') or 0
    desc = str(m['desc'])
    rec = {'sku': sku, 'desc': desc[:34], 'cur': cur, 'civa': m['civa'], 'stock': a['stock'], 'ads': a.get('sponsored')}
    if GRIF.search(desc.upper()):
        best = taumm_price(desc)
        if best:
            venta = r990(best['price'] - 1000)
            rec.update({'venta': venta, 'comp': best['price'], 'margen': 1 - m['civa']/venta})
            griferia.append(rec)
        else:
            commodity.append(rec)   # griferia sin competidor -> commodity bucket
    elif cur >= 60000:
        flag_alto.append(rec)
    else:
        commodity.append(rec)

print('\n--- RESUMEN (con stock + en master) ---')
print('Griferias con estandar TAUMM:', len(griferia))
print('Commodity (default/flag):', len(commodity))
print('Alto valor distintivo (>=60k, flag foto):', len(flag_alto))

print('\n=== GRIFERIAS (precio estandar listo) ===')
for g in sorted(griferia, key=lambda z: -z['cur']):
    print(f"  {g['sku']:13} stk{g['stock']:>3} hoy {g['cur']:>8,} -> {g['venta']:>7,} (m{g['margen']*100:.0f}%) comp{g['comp']:>7,}{'  ADS' if g['ads'] else ''}  {g['desc']}")

import json as J
J.dump({'griferia':griferia,'commodity':commodity,'flag_alto':flag_alto}, open('plan_precios.json','w',encoding='utf-8'), ensure_ascii=False)
