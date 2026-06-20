# -*- coding: utf-8 -*-
"""Lote commodity con costo validado: ticket bajo (<40k) -> factor 2.3,
ticket alto (>=40k) -> factor 1.8. Tachado 50%. Excluye distintivos y no-competibles."""
import json, glob, openpyxl, re

def load(f):
    raw=open(f,encoding='utf-8').read().strip(); d=json.loads(raw); return json.loads(d) if isinstance(d,str) else d

admin={}
for f in sorted(glob.glob('admin_p*.json')):
    d=load(f); rows=d['rows'] if isinstance(d,dict) and 'rows' in d else d
    for r in rows: admin[r['seller']]=r

ws=openpyxl.load_workbook('validacion_costos.xlsx',data_only=True).active
rv=list(ws.iter_rows(values_only=True)); H=rv[0]
ic=H.index('Codigo'); icu=H.index('COSTO A USAR'); icf=H.index('Confianza'); idd=H.index('Descripcion')
cost={r[ic]:{'c':r[icu],'conf':r[icf],'desc':r[idd]} for r in rv[1:] if r[ic] and isinstance(r[icu],(int,float))}

# SellerSku -> ShopSku + Name (de la plantilla Falabella)
tpl=openpyxl.load_workbook('SellerPriceTemplate.xlsx',data_only=True).active
shop={}
for r in list(tpl.iter_rows(values_only=True))[1:]:
    base=re.sub(r'_\d+$','',str(r[0]))
    shop[base]={'sku':r[0],'shop':r[1],'name':r[6]}

YA={'010701007-T','020101010-T','020101011-T','020101001-T','020101002-T','020101003-T','040303003-T','040203017-C','040201006-T','040202005-T'}
EXCL={'010502005-T','010501022-T','010703011-T','040201008-T'}  # distintivos + no competible
def r990(x): x=int(round(x)); return (x//1000)*1000+990 if x>=1000 else max(0,x)
SALE_START='2026-06-16 00:00:01'; SALE_END='2026-07-16 23:59:59'

batch=[]
for sku,a in admin.items():
    if not(a.get('stock') and a['stock']>0) or sku in YA or sku in EXCL: continue
    cv=cost.get(sku)
    if not cv or cv['conf'] not in ('ALTA','MEDIA'): continue
    cur=a.get('special') or a.get('price') or 0
    civa=cv['c']*1.19
    fac=1.8 if cur>=40000 else 2.3
    venta=r990(civa*fac)
    if cur<=venta*1.05: continue  # solo si baja (sobreprecio)
    tach=r990(venta/0.5)
    sm=shop.get(sku)
    if not sm: continue
    batch.append({'sku':sm['sku'],'shop':sm['shop'],'name':sm['name'],'venta':venta,'tach':tach,
                  'cur':cur,'fac':fac,'margen':1-civa/venta,'desc':str(cv['desc'])[:30],'conf':cv['conf']})

# escribir upload
wb=openpyxl.Workbook(); w=wb.active; w.title='Sheet'
w.append(['SellerSku','ShopSku','PriceFalabella','SalePriceFalabella','SaleStartDateFalabella','SaleEndDateFalabella','Name'])
for b in batch:
    w.append([b['sku'],b['shop'],float(b['tach']),float(b['venta']),SALE_START,SALE_END,b['name']])
wb.save('SellerPriceTemplate_UPLOAD_nuevo.xlsx')

print('LOTE COMMODITY:',len(batch),'productos')
print('%-13s %3s %8s %8s %8s %5s  %s'%('SKU','fac','hoy','venta','tachado','marg','desc'))
for b in sorted(batch,key=lambda z:-z['cur']):
    print('%-13s %3.1f %8d %8d %8d %4.0f%%  %s'%(b['sku'],b['fac'],b['cur'],b['venta'],b['tach'],b['margen']*100,b['desc']))
