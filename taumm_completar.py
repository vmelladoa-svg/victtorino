# -*- coding: utf-8 -*-
"""Extrae el raster EMBEBIDO (aislado, sin texto de catalogo) del producto Taumm
correcto para los 8 SKU con <4 fotos, lo normaliza a cuadrado blanco 1080 y lo deja
como foto adicional. Reemplaza cualquier version previa."""
import fitz, os, glob
from PIL import Image, ImageChops
ROOT=r'C:\Users\dell\victtorino'
PDFB=os.path.join(ROOT,'taumm_fichas')

MAP={
 '030101005-T1':('05_Flexibles-Agua-Gas.pdf',1,3,False),
 '030102003-T1':('05_Flexibles-Agua-Gas.pdf',0,190,False),
 '010301010-T1':('21_Accesorios-WC.pdf',0,320,False),
 '010301004-T1':('21_Accesorios-WC.pdf',1,8,False),
 '010301011-T1':('21_Accesorios-WC.pdf',1,16,False),
 '010403001-T1':('04_Griferia-General.pdf',0,202,False),
 '020102001-T1':('19_Lavaplatos-Accesorios.pdf',0,156,False),
 '020101006-T1':('19_Lavaplatos-Accesorios.pdf',0,158,True),
}

def trim_white(im,thr=12):
    g=im.convert('RGB')
    bg=Image.new('RGB',g.size,(255,255,255))
    diff=ImageChops.difference(g,bg).convert('L').point(lambda p:255 if p>thr else 0)
    bbox=diff.getbbox()
    return im.crop(bbox) if bbox else im

def square(im,target=1080,pad=50):
    im=trim_white(im)
    w,h=im.size; lado=max(w,h)+pad*2
    lienzo=Image.new('RGB',(lado,lado),(255,255,255))
    lienzo.paste(im,((lado-w)//2,(lado-h)//2))
    return lienzo.resize((target,target),Image.LANCZOS)

for sku,(pdf,pno,xref,rep) in MAP.items():
    d=fitz.open(os.path.join(PDFB,pdf))
    pix=fitz.Pixmap(d,xref)
    if pix.colorspace is None or pix.colorspace.name not in ('DeviceRGB','DeviceGray'):
        pix=fitz.Pixmap(fitz.csRGB,pix)
    if pix.alpha: pix=fitz.Pixmap(pix,0)
    img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    d.close()
    # limpiar versiones previas taumm
    od=os.path.join(ROOT,'falabella_contenido',sku)
    for f in glob.glob(os.path.join(od,'*_taumm.jpg')): os.remove(f)
    n=len([f for f in os.listdir(od) if f.endswith('.jpg')])+1
    img.save(os.path.join(od,f'{sku}_{n:02d}_taumm.jpg'),quality=95)
    # listo: el cupo de fotos validas era 3 -> esta es la #4
    ld=os.path.join(ROOT,'falabella_fotos_listo',sku)
    sq=square(img)
    sq.save(os.path.join(ld,f'{sku}_04.jpg'),quality=92)
    print(f'{sku}: raster {pix.width}x{pix.height} -> #4 listo{"  (REPRESENTATIVA)" if rep else ""}')
