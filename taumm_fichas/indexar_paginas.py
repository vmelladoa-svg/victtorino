# -*- coding: utf-8 -*-
import subprocess, re, os, json
FAM={"01":"Monomandos","02":"Accesorios para Ducha","03":"Accesorios para Bano",
"04":"Griferia General","05":"Flexibles Agua y Gas","06":"Valvulas","07":"Llaves",
"08":"Fitting Bronce","10":"Griferia Temporizada","11":"Fitting de Laton",
"12":"Piezas para Sanitarias","13":"Repuestos","14_15":"Shower Doors, Espejos y Bowls",
"16":"Griferia Electronica","17":"Teflones","18":"Tinas y sus Accesorios",
"19":"Lavaplatos y Accesorios","21":"Accesorios WC"}
HERE=os.path.dirname(os.path.abspath(__file__))
pdfs=sorted([f for f in os.listdir(HERE) if f.endswith('.pdf')])
pages=[]
for fn in pdfs:
    key=re.match(r'^(\d+(?:_\d+)?)_',fn).group(1)
    raw=subprocess.run(['pdftotext','-raw','-enc','UTF-8',os.path.join(HERE,fn),'-'],
                       capture_output=True).stdout.decode('utf-8','replace')
    for pno,ptext in enumerate(raw.split('\f'),1):
        if not ptext.strip(): continue
        codes=[c for c in re.findall(r'\b\d{2}[0-9A-Z]{7}\b',ptext) if sum(ch.isdigit() for ch in c)>=6]
        pages.append({'pdf':fn,'familia':FAM.get(key,key),'pagina':pno,
                      'codigos':sorted(set(codes)),'texto':ptext})
json.dump(pages,open(os.path.join(HERE,'paginas_catalogo.json'),'w',encoding='utf-8'),ensure_ascii=False)
print('Paginas indexadas:',len(pages))
