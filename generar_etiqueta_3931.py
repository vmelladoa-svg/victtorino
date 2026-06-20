# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

W, H = A4
c = canvas.Canvas("etiqueta_3931.pdf", pagesize=A4)

M = 15 * mm
x0, x1 = M, W - M
y = H - M

def box(x, yt, w, h):
    c.setLineWidth(1.2); c.rect(x, yt - h, w, h)

def text(x, yt, s, size=11, font="Helvetica", color=(0,0,0)):
    c.setFont(font, size); c.setFillColorRGB(*color); c.drawString(x, yt, s)

def wrap(x, yt, s, size, font, maxw, lh):
    c.setFont(font, size)
    for ln in simpleSplit(s, font, size, maxw):
        c.drawString(x, yt, ln); yt -= lh
    return yt

# ---- Encabezado marca ----
c.setFillColorRGB(0.07,0.20,0.45); c.rect(x0, y-18*mm, x1-x0, 18*mm, fill=1, stroke=0)
text(x0+5*mm, y-9*mm, "TRADE  ·  victtorino.cl", 20, "Helvetica-Bold", (1,1,1))
text(x0+5*mm, y-15*mm, "ETIQUETA DE DESPACHO", 11, "Helvetica", (1,1,1))
text(x1-45*mm, y-9*mm, "ORDEN", 11, "Helvetica", (1,1,1))
text(x1-45*mm, y-16*mm, "#3931", 22, "Helvetica-Bold", (1,1,1))
y -= 18*mm

# ---- DESTINATARIO (grande) ----
y -= 5*mm
bh = 52*mm
box(x0, y, x1-x0, bh)
c.setFillColorRGB(0.90,0.93,0.98); c.rect(x0, y-8*mm, x1-x0, 8*mm, fill=1, stroke=0)
text(x0+4*mm, y-6*mm, "DESTINATARIO", 11, "Helvetica-Bold", (0.07,0.20,0.45))
iy = y - 16*mm
text(x0+4*mm, iy, "Yubitza Aldunate", 18, "Helvetica-Bold"); iy -= 9*mm
text(x0+4*mm, iy, "Humberto Palza 5951  -  Depto/Casa 2590", 13, "Helvetica"); iy -= 7*mm
text(x0+4*mm, iy, "Comuna: ARICA", 13, "Helvetica-Bold"); iy -= 7*mm
text(x0+4*mm, iy, "Region de Arica y Parinacota", 12, "Helvetica"); iy -= 7*mm
text(x0+4*mm, iy, "Telefono: +56 9 8360 2337", 13, "Helvetica-Bold")
text(x1-55*mm, y-16*mm, "RUT: 78418876-0", 11, "Helvetica")
y -= bh

# ---- REMITENTE ----
y -= 5*mm
bh2 = 26*mm
box(x0, y, x1-x0, bh2)
c.setFillColorRGB(0.95,0.95,0.95); c.rect(x0, y-7*mm, x1-x0, 7*mm, fill=1, stroke=0)
text(x0+4*mm, y-5.2*mm, "REMITENTE", 10, "Helvetica-Bold", (0.3,0.3,0.3))
iy = y - 13*mm
text(x0+4*mm, iy, "Trade Global Solutions SpA  -  RUT 78.103.712-5", 11, "Helvetica-Bold"); iy -= 6*mm
text(x0+4*mm, iy, "Madame Adriana Bolland 430, La Cisterna, Santiago", 11, "Helvetica"); iy -= 6*mm
text(x0+4*mm, iy, "Contacto: +56 9 2178 9322  ·  victtorino.cl", 11, "Helvetica")
y -= bh2

# ---- DETALLE ----
y -= 5*mm
bh3 = 30*mm
box(x0, y, x1-x0, bh3)
c.setFillColorRGB(0.90,0.93,0.98); c.rect(x0, y-7*mm, x1-x0, 7*mm, fill=1, stroke=0)
text(x0+4*mm, y-5.2*mm, "CONTENIDO DEL ENVIO", 10, "Helvetica-Bold", (0.07,0.20,0.45))
iy = y-13*mm
text(x0+4*mm, iy, "2 x  Llave Temporizada Para Urinario Plateado", 12, "Helvetica-Bold"); iy -= 6*mm
text(x0+4*mm, iy, "SKU: ML-MLC1307819379", 10, "Helvetica")
text(x1-60*mm, iy, "Total: $54.942", 11, "Helvetica-Bold"); iy -= 6*mm
text(x0+4*mm, iy, "Pago: Webpay Plus (PAGADO)", 10, "Helvetica")
text(x1-60*mm, iy, "Doc: FACTURA", 11, "Helvetica-Bold", (0.7,0,0))
y -= bh3

# ---- Bultos / peso (a completar) ----
y -= 5*mm
text(x0, y, "BULTOS: ______        PESO: ______ kg        FECHA: ____/____/2026", 12, "Helvetica")
y -= 8*mm
text(x0, y, "Courier / N de guia: ______________________________", 11, "Helvetica")

# pie
c.setFillColorRGB(0.5,0.5,0.5)
text(x0, M, "Generado desde orden #3931 - victtorino.cl  ·  Frágil: contiene grifería metálica", 8, "Helvetica", (0.5,0.5,0.5))

c.showPage(); c.save()
print("OK -> etiqueta_3931.pdf")
