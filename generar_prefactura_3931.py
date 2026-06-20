# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

W, H = A4
c = canvas.Canvas("prefactura_3931.pdf", pagesize=A4)
M = 18*mm; x0, x1 = M, W-M
NAVY=(0.07,0.20,0.45); GREY=(0.4,0.4,0.4); LIGHT=(0.90,0.93,0.98)

def t(x,y,s,sz=10,f="Helvetica",col=(0,0,0)):
    c.setFont(f,sz); c.setFillColorRGB(*col); c.drawString(x,y,s)
def tr(x,y,s,sz=10,f="Helvetica",col=(0,0,0)):
    c.setFont(f,sz); c.setFillColorRGB(*col); c.drawRightString(x,y,s)

y=H-M
# Encabezado
c.setFillColorRGB(*NAVY); c.rect(x0,y-20*mm,x1-x0,20*mm,fill=1,stroke=0)
t(x0+5*mm,y-9*mm,"TRADE  ·  victtorino.cl",18,"Helvetica-Bold",(1,1,1))
t(x0+5*mm,y-16*mm,"Trade Global Solutions SpA",10,"Helvetica",(1,1,1))
# recuadro tipo doc
c.setStrokeColorRGB(*NAVY); c.setLineWidth(1.4); c.rect(x1-52*mm,y-20*mm,52*mm,20*mm)
tr(x1-2*mm,y-7*mm,"PRE-FACTURA",13,"Helvetica-Bold",NAVY)
tr(x1-2*mm,y-12.5*mm,"Borrador DTE 33",9,"Helvetica",GREY)
tr(x1-2*mm,y-17*mm,"Orden #3931",11,"Helvetica-Bold")
y-=20*mm

# Aviso
y-=6*mm
t(x0,y,"DOCUMENTO PRELIMINAR - no valido como factura tributaria. Emitir folio oficial en Defontana/SII.",8,"Helvetica-Oblique",(0.7,0,0))
y-=4*mm

# EMISOR / FECHA
y-=8*mm
t(x0,y,"EMISOR",9,"Helvetica-Bold",GREY)
tr(x1,y,"FECHA: 12/06/2026",10,"Helvetica")
y-=6*mm
t(x0,y,"Trade Global Solutions SpA  ·  RUT 78.103.712-5",10,"Helvetica-Bold"); y-=5*mm
t(x0,y,"Madame Adriana Bolland 430, La Cisterna, Santiago",10,"Helvetica"); y-=5*mm
t(x0,y,"victtorino.cl  ·  +56 9 2178 9322",10,"Helvetica")

# RECEPTOR box
y-=10*mm
bh=34*mm
c.setFillColorRGB(*LIGHT); c.rect(x0,y-7*mm,x1-x0,7*mm,fill=1,stroke=0)
c.setStrokeColorRGB(0.7,0.7,0.7); c.setLineWidth(0.8); c.rect(x0,y-bh,x1-x0,bh)
t(x0+3*mm,y-5*mm,"SEÑOR(ES) / RECEPTOR",9,"Helvetica-Bold",NAVY)
iy=y-13*mm
t(x0+3*mm,iy,"Myra RaYú social club spa",12,"Helvetica-Bold")
tr(x1-3*mm,iy,"RUT: 78.418.876-0",11,"Helvetica-Bold"); iy-=6*mm
t(x0+3*mm,iy,"Giro: Restaurante",10,"Helvetica"); iy-=6*mm
t(x0+3*mm,iy,"Dirección: Camino Azapa 5954, Arica - Región de Arica y Parinacota",10,"Helvetica"); iy-=6*mm
t(x0+3*mm,iy,"Contacto: Yubitza Aldunate Torres  ·  983602337  ·  yu.aldunate@gmail.com",9,"Helvetica",GREY)
y-=bh

# Tabla detalle
y-=10*mm
c.setFillColorRGB(*NAVY); c.rect(x0,y-7*mm,x1-x0,7*mm,fill=1,stroke=0)
t(x0+3*mm,y-5*mm,"CANT.",9,"Helvetica-Bold",(1,1,1))
t(x0+22*mm,y-5*mm,"DETALLE",9,"Helvetica-Bold",(1,1,1))
tr(x1-35*mm,y-5*mm,"P. UNIT. NETO",9,"Helvetica-Bold",(1,1,1))
tr(x1-3*mm,y-5*mm,"NETO",9,"Helvetica-Bold",(1,1,1))
y-=7*mm
def row(q,det,sub,unit,neto):
    global y
    y-=8*mm
    t(x0+3*mm,y,q,10); 
    t(x0+22*mm,y,det,10,"Helvetica-Bold")
    if sub: t(x0+22*mm,y-4.5*mm,sub,8,"Helvetica",GREY)
    tr(x1-35*mm,y,unit,10); tr(x1-3*mm,y,neto,10)
    c.setStrokeColorRGB(0.85,0.85,0.85); c.setLineWidth(0.6); c.line(x0,y-6.5*mm,x1,y-6.5*mm)
row("2","Llave Temporizada Para Urinario Plateado","SKU: ML-MLC1307819379","$20.590","$41.180")
y-=4.5*mm
row("1","Despacho a domicilio (afecto IVA)","Envío a Arica","$4.990","$4.990")

# Totales
y-=14*mm
tx=x1-58*mm
def tot(lbl,val,bold=False,big=False):
    global y
    f="Helvetica-Bold" if bold else "Helvetica"; sz=13 if big else 10
    t(tx,y,lbl,sz,f); tr(x1-3*mm,y,val,sz,f, NAVY if big else (0,0,0)); y-=7*mm
tot("Neto","$46.170")
tot("IVA 19%","$8.772")
c.setStrokeColorRGB(*NAVY); c.setLineWidth(1.2); c.line(tx,y+3*mm,x1-3*mm,y+3*mm); y-=2*mm
tot("TOTAL","$54.942",bold=True,big=True)

# Pie
t(x0,M+6*mm,"Pago: Webpay Plus (PAGADO)  ·  Tipo entrega: domicilio  ·  Origen: orden web #3931",8,"Helvetica",GREY)
t(x0,M,"Generado para carga en Defontana. Verificar folio y giro del emisor antes de timbrar.",8,"Helvetica-Oblique",GREY)

c.showPage(); c.save()
print("OK -> prefactura_3931.pdf")
