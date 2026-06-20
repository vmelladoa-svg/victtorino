# -*- coding: utf-8 -*-
"""Reporte semanal de Product Ads (C2 + C3): aplica la banda de KPI a las
campanas MANUALES y manda el resumen por WhatsApp (CallMeBot). Pensado para
correr por Tarea Programada de Windows (semanal). Las campanas AUTOMATICAS se
omiten (ML las gestiona solo)."""
import json, requests, datetime, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
B='https://api.mercadolibre.com'
CID='3959231945649654'; CSEC='PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG'
WA_PHONE='56996953815'; WA_KEY='5759352'
ACC={'C2':(79006,'tokens_cuenta2.json'),'C3':(79197,'tokens_cuenta3.json')}
AUTOMATICAS={355145983, 354999960}  # Mercado Libre C2 (auto) + Mercado Libre C3 (auto)
BREAK_EVEN=3.9   # ROAS break-even con canibalizacion (margen ~47%)
hoy=datetime.date.today()
DF=(hoy-datetime.timedelta(days=30)).isoformat(); DT=(hoy-datetime.timedelta(days=1)).isoformat()

def refresh(tok,f):
    d=requests.post(B+'/oauth/token',data={'grant_type':'refresh_token','client_id':CID,'client_secret':CSEC,'refresh_token':tok['refresh_token']},timeout=30).json()
    if 'access_token' in d:
        tok['access_token']=d['access_token']; tok['refresh_token']=d.get('refresh_token',tok['refresh_token']); json.dump(tok,open(f,'w'),indent=2)
def g(f,path):
    tok=json.load(open(f))
    for i in range(2):
        r=requests.get(B+path,headers={'Authorization':'Bearer '+tok['access_token'],'api-version':'1'},timeout=40)
        if r.status_code==401 and i==0: refresh(tok,f); continue
        return r
    return r
def pe(x):
    try: return '$'+format(int(round(x)),',d').replace(',','.')
    except: return str(x)

lineas=[f"Reporte ads semanal {hoy.isoformat()} (30d)"]
detalle=[lineas[0],""]
tot_pausar=tot_estrella=0
for acc,(adv,f) in ACC.items():
    camps=[c for c in g(f,f'/advertising/advertisers/{adv}/product_ads/campaigns?limit=50').json().get('results',[]) if c['status']=='active' and c['id'] not in AUTOMATICAS]
    detalle.append(f"== {acc} ==")
    muertos=[]; perd=[]; estrellas=[]
    for c in camps:
        cid=c['id']; items={}; off=0
        while True:
            j=g(f,f'/advertising/advertisers/{adv}/product_ads/items?campaign_id={cid}&limit=50&offset={off}&date_from={DF}&date_to={DT}&metrics=acos,clicks').json()
            res=j.get('results',[])
            for it in res:
                if it.get('campaign_id')!=cid: continue
                if it.get('status')!='active': continue  # solo anuncios activos (no flaggear ya pausados)
                iid=it.get('item_id')
                if iid in items: continue
                m=it.get('metrics',{}) or {}
                items[iid]={'t':(it.get('title') or '')[:34],'cost':m.get('cost',0) or 0,'sales':m.get('total_amount',0) or 0,
                            'clicks':m.get('clicks',0) or 0,'roas':round((m.get('total_amount',0) or 0)/m.get('cost',1),2) if m.get('cost') else 0}
            tot=j.get('paging',{}).get('total',0); off+=50
            if off>=tot or not res: break
        for iid,r in items.items():
            if r['sales']==0 and r['clicks']>=30 and r['cost']>=1000: muertos.append((iid,r,c.get('name')))
            elif r['sales']>0 and r['roas']<BREAK_EVEN and r['cost']>=3000: perd.append((iid,r,c.get('name')))
            elif r['roas']>=6 and r['cost']>=2000: estrellas.append((iid,r,c.get('name')))
    detalle.append(f"  PAUSAR muertos: {len(muertos)}")
    for iid,r,cn in sorted(muertos,key=lambda x:-x[1]['cost']): detalle.append(f"    {iid} {pe(r['cost'])} {r['clicks']}clic 0vta [{cn}] {r['t']}")
    detalle.append(f"  REVISAR perdedores (ROAS<{BREAK_EVEN}): {len(perd)}")
    for iid,r,cn in sorted(perd,key=lambda x:x[1]['roas']): detalle.append(f"    {iid} ROAS{r['roas']} {pe(r['cost'])} [{cn}] {r['t']}")
    detalle.append(f"  ESCALAR estrellas (ROAS>=6): {len(estrellas)}")
    for iid,r,cn in sorted(estrellas,key=lambda x:-x[1]['roas']): detalle.append(f"    {iid} ROAS{r['roas']} {pe(r['cost'])} [{cn}] {r['t']}")
    detalle.append("")
    tot_pausar+=len(muertos)+len(perd); tot_estrella+=len(estrellas)

# archivo detalle
fn=f"ml_ads_reporte_{hoy.strftime('%Y%m%d')}.txt"
open(fn,'w',encoding='utf-8').write("\n".join(detalle))

# whatsapp (plano, sin emojis)
msg=(f"Reporte ads semanal {hoy.isoformat()}: {tot_pausar} productos para pausar/revisar y "
     f"{tot_estrella} estrellas para escalar. Detalle en {fn}. "
     f"Recorda: pausar por producto (no campana), no bajar ROAS a 3,1x, y los de mucho clic/poca venta son problema de precio.")
try:
    r=requests.get('https://api.callmebot.com/whatsapp.php',params={'phone':WA_PHONE,'apikey':WA_KEY,'text':msg},timeout=40)
    print("WhatsApp:",r.status_code, 'queued' if 'queued' in r.text.lower() else r.text[:100])
except Exception as e:
    print("WhatsApp ERROR:",e)
print("Reporte guardado:",fn)
print("\n".join(detalle))
