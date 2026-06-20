# -*- coding: utf-8 -*-
"""Lote 2: los 14 productos antes sin costo, ahora con Costo Vigente (valorizado).
Regla: competidor TAUMM si existe (1 escalon abajo, margen>=20%); si no, factor por
ticket (<40k ->2.3, >=40k ->1.8). Tachado 50%, vigencia 30 dias."""
import json, glob, re, openpyxl

def load(f):
    raw=open(f,encoding='utf-8').read().strip(); d=json.loads(raw); return json.loads(d) if isinstance(d,str) else d

admin={}
for f in sorted(glob.glob('admin_p*.json')):
    d=load(f); rows=d['rows'] if isinstance(d,dict) and 'rows' in d else d
    for r in rows: admin[r['seller']]=r

vig=load('costos_vigentes.json')  # {cod:{vig,rep,stock}}
tpl=openpyxl.load_workbook('SellerPriceTemplate.xlsx',data_only=True).active
shop={}
for r in list(tpl.iter_rows(values_only=True))[1:]:
    shop[re.sub(r'_\d+$','',str(r[0]))]={'sku':r[0],'shop':r[1],'name':r[6]}

# competidores TAUMM
taumm=[]
for f in sorted(glob.glob('taumm_[0-9].json')):
    try: taumm+=load(f)
    except: pass
comp=[c for c in taumm if 'Trade' not in c.get('seller','')]
MOD=['NOTTE','COLOMBA','DOMENICA','VANDER','MODERN','BONN','SWERTT','ANTONELLA','MILAN','PROFESIONAL','TEMPORIZADA','CISNE','VERTICAL','ALTO','BIDET','MONOBLOCK','LAVACOPA','CUELLO']
TIP=['LAVAPLATO','LAVATORIO','LAVAMANOS','DUCHA','TINA','BIDET','LAVACOPA','JARDIN','ANGULAR','DISPENSADOR','BARRA','SIFON','BANDEJA','RECEPTACULO','URINARIO']
MS=set(MOD)
def tk(n):
    n=n.upper(); s=set()
    for m in MOD:
        if m in n: s.add(m)
    for t in TIP:
        if t in n: s.add(t)
    return s
def r990(x): x=int(round(x)); return (x//1000)*1000+990 if x>=1000 else max(0,x)
def bestc(desc):
    mt=tk(desc); my=mt&MS; b=None
    for c in comp:
        ct=tk(c['name'])
        if mt and len(mt&ct)>=2 and (not my or (my&ct)):
            if b is None or c['price']<b['price']: b=c
    return b

S14=['040302001-T','010403001-T','010603003-T','010103003-T','040301001-T','040202001-T','020102002-T','010701008-T','020102001-T','040201001-T','020103001-T','020201003-T','010102007-C','010102002-T']
SALE_START='2026-06-16 00:00:01'; SALE_END='2026-07-16 23:59:59'

batch=[]; flag=[]
for sku in S14:
    a=admin.get(sku); v=vig.get(sku)
    if not a or not v or not v.get('vig'): flag.append((sku,'sin dato')); continue
    cur=a.get('special') or a.get('price') or 0
    civa=v['vig']*1.19
    desc=a.get('name','') or sku
    b=bestc(str(desc))
    via='factor'; comp_price=None
    if b:
        venta=r990(b['price']-1000); comp_price=b['price']; via='competidor'
        if venta<civa*1.15:   # competidor bajo costo -> no competir
            flag.append((sku, 'competidor %s ~ costo %d' % (b['price'], int(civa)))); continue
    else:
        fac=1.8 if cur>=40000 else 2.3
        venta=r990(civa*fac); via=f'x{fac}'
    margen=1-civa/venta
    if cur<=venta*1.05:
        flag.append((sku,f'no sobreprecio (hoy {cur} vs {venta})')); continue
    sm=shop.get(sku)
    if not sm: flag.append((sku,'sin shopsku')); continue
    tach=r990(venta/0.5)
    batch.append({'sku':sm['sku'],'shop':sm['shop'],'name':sm['name'],'tach':tach,'venta':venta,
                  'cur':cur,'via':via,'comp':comp_price,'margen':margen,'desc':str(desc)[:30]})

wb=openpyxl.Workbook(); w=wb.active; w.title='Sheet'
w.append(['SellerSku','ShopSku','PriceFalabella','SalePriceFalabella','SaleStartDateFalabella','SaleEndDateFalabella','Name'])
for b in batch:
    w.append([b['sku'],b['shop'],float(b['tach']),float(b['venta']),SALE_START,SALE_END,b['name']])
wb.save('SellerPriceTemplate_UPLOAD_nuevo.xlsx')

print('LOTE 2:',len(batch),'a subir |',len(flag),'flag')
print('%-13s %8s %8s %8s %5s %-11s %s'%('SKU','hoy','venta','tachado','marg','via','desc'))
for b in sorted(batch,key=lambda z:-z['cur']):
    print('%-13s %8d %8d %8d %4.0f%% %-11s %s'%(b['sku'],b['cur'],b['venta'],b['tach'],b['margen']*100,b['via'],b['desc']))
print('\nFLAG:')
for fl in flag: print('  ',fl[0],fl[1])
