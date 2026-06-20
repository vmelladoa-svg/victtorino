# -*- coding: utf-8 -*-
"""Precia los pendientes con stock y costo: competidor TAUMM (1 escalon abajo) o
factor por ticket (<40k->2.3, >=40k->1.8). Solo si baja (sobreprecio). Genera tabla
y archivo de carga."""
import json, glob, re, openpyxl

def load(f):
    raw=open(f,encoding='utf-8').read().strip(); d=json.loads(raw); return json.loads(d) if isinstance(d,str) else d

admin=json.load(open('admin_full.json',encoding='utf-8'))
# done
spec=open('generar_excel_master.py',encoding='utf-8').read()
ns={}; exec(spec[spec.index('VENTA = {'):spec.index('}\n# costos manuales')+1], ns)
done=set(ns['VENTA'].keys())
# cost
wv=openpyxl.load_workbook('validacion_costos.xlsx',data_only=True).active
rv=list(wv.iter_rows(values_only=True)); Hv=rv[0]
val={r[Hv.index('Codigo')]:r[Hv.index('COSTO A USAR')] for r in rv[1:] if r[Hv.index('Codigo')] and isinstance(r[Hv.index('COSTO A USAR')],(int,float))}
vig=json.load(open('costos_vigentes.json',encoding='utf-8'))
def costo(s):
    if s in val: return val[s]
    if s in vig and vig[s].get('vig'): return vig[s]['vig']
    return None
# template shopsku
tpl=openpyxl.load_workbook('SellerPriceTemplate.xlsx',data_only=True).active
shop={}
for r in list(tpl.iter_rows(values_only=True))[1:]:
    shop[re.sub(r'_\d+$','',str(r[0]))]={'sku':r[0],'shop':r[1],'name':r[6]}
# TAUMM competidores
taumm=[]
for f in sorted(glob.glob('taumm_[0-9].json')):
    try: taumm+=load(f)
    except: pass
comp=[c for c in taumm if 'Trade' not in c.get('seller','')]
MOD=['NOTTE','COLOMBA','DOMENICA','VANDER','MODERN','BONN','SWERTT','ANTONELLA','MILAN','PROFESIONAL','TEMPORIZADA','CISNE','VERTICAL','ALTO','BIDET','MONOBLOCK','LAVACOPA','CUELLO']
TIP=['LAVAPLATO','LAVATORIO','LAVAMANOS','DUCHA','TINA','BIDET','LAVACOPA','JARDIN','ANGULAR','DISPENSADOR','BARRA','SIFON','BANDEJA','RECEPTACULO','URINARIO','FLUXOMETRO','ESPEJO','TOALLERO','PLATO']
MS=set(MOD)
def tk(n):
    n=n.upper(); s=set()
    for m in MOD:
        if m in n: s.add(m)
    for t in TIP:
        if t in n: s.add(t)
    return s
def bestc(desc):
    mt=tk(desc); my=mt&MS; b=None
    for c in comp:
        ct=tk(c['name'])
        if mt and len(mt&ct)>=2 and (not my or (my&ct)):
            if b is None or c['price']<b['price']: b=c
    return b
def r990(x): x=int(round(x)); return (x//1000)*1000+990 if x>=1000 else max(0,x)

DECIDIDOS={'020101009-T':'dejado $44.871','040201008-T':'no compite'}
pend=[(s,a) for s,a in admin.items() if a.get('stock') and a['stock']>0 and s not in done and costo(s)]
batch=[]; flag=[]
for s,a in pend:
    if s in DECIDIDOS: flag.append((s,DECIDIDOS[s])); continue
    cur=a.get('special') or a.get('price') or 0
    civa=costo(s)*1.19
    desc=a.get('name','') or s
    b=bestc(str(desc)); via='factor'
    if b:
        venta=r990(b['price']-1000); via='comp %d'%b['price']
        if venta<civa*1.15: flag.append((s,'competidor %d ~ costo %d'%(b['price'],int(civa)))); continue
    else:
        fac=1.8 if cur>=40000 else 2.3; venta=r990(civa*fac); via='x%s'%fac
    venta=r990(venta*1.07)   # +7% pedido por Victor
    OVR={'010703013-T':76990}   # precios finales fijados por Victor
    if s in OVR:
        venta=OVR[s]
    elif cur<=venta*1.05:
        flag.append((s,'no sobreprecio (hoy %d vs %d)'%(cur,venta))); continue
    sm=shop.get(s)
    if not sm: flag.append((s,'sin shopsku')); continue
    batch.append({'sku':sm['sku'],'shop':sm['shop'],'name':sm['name'],'venta':venta,'tach':r990(venta/0.5),
                  'cur':cur,'via':via,'margen':1-civa/venta,'desc':str(desc)[:34],'ads':a.get('sponsored')})

# upload file
wb=openpyxl.Workbook(); w=wb.active; w.title='Sheet'
w.append(['SellerSku','ShopSku','PriceFalabella','SalePriceFalabella','SaleStartDateFalabella','SaleEndDateFalabella','Name'])
for b in batch:
    w.append([b['sku'],b['shop'],float(b['tach']),float(b['venta']),'2026-06-16 00:00:01','2026-07-16 23:59:59',b['name']])
wb.save('SellerPriceTemplate_UPLOAD_nuevo.xlsx')

print('A SUBIR:',len(batch),'| flag:',len(flag))
print('%-13s %8s %8s %5s %-12s %s'%('SKU','hoy','venta','marg','via','desc'))
for b in sorted(batch,key=lambda z:-z['cur']):
    print('%-13s %8d %8d %4.0f%% %-12s %s%s'%(b['sku'],b['cur'],b['venta'],b['margen']*100,b['via'],b['desc'],'  [ADS]' if b['ads'] else ''))
print('\nFLAG:')
for fl in flag: print('  ',fl[0],fl[1])
