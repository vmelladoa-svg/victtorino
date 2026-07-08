# -*- coding: utf-8 -*-
"""Utilidades para independizar el catalogo de Alila:
 - rehost_fotos(): sube las fotos de un producto a Cloudinary (TU storage) y
   devuelve URLs propias. Cloudinary descarga la imagen desde su servidor, asi
   que evita el bloqueo por referer del CDN de Alila.
 - limpiar_desc(): descripcion sin chino, sin HTML, sin URLs ni rastros del
   proveedor (Alila / bspapp / 1688 / MercadoLibre) ni notas de packaging.
 - limpiar_nombre(): nombre sin caracteres chinos.
Requiere env: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET."""
import os, re, requests
import cloudinary, cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
    secure=True,
)

# ---------- limpieza de texto ----------
_CJK = re.compile(r'[　-〿㐀-䶿一-鿿豈-﫿＀-￯]+')
_TAGS = re.compile(r'<[^>]+>')
_URLS = re.compile(r'https?://\S+')
# rastros del proveedor que NO deben aparecer al cliente
_RASTROS = re.compile(r'(alila\s*top|alilatop|alila|bspapp|1688|mercado\s*libre|mercadolibre)', re.I)
# lineas de packaging del proveedor ("Cantidad de envase: 12pcs", "10 set", etc.)
_PACK = re.compile(r'^\s*(cantidad de (envase|caja|cajas|env(a|á)ses?|bulto).*|\d+\s*(pcs|set|sets|unidades?)?)\s*$', re.I)

def limpiar_nombre(mc):
    if not mc: return None
    s = _CJK.sub('', str(mc))
    s = re.sub(r'\s{2,}', ' ', s).strip(' ,-·|/').strip()
    return s or None

def limpiar_desc(html):
    if not html: return None
    s = str(html)
    s = _URLS.sub(' ', s)                              # fuera URLs (Alila/ML/1688)
    s = re.sub(r'<\s*br\s*/?\s*>', '\n', s, flags=re.I)
    s = re.sub(r'</\s*p\s*>', '\n', s, flags=re.I)
    s = _TAGS.sub('', s)                               # fuera HTML
    s = _CJK.sub('', s)                                # fuera chino
    s = s.replace('﻿', '').replace('​', '')  # zero-width
    out = []
    for ln in s.split('\n'):
        t = re.sub(r'\s{2,}', ' ', ln).strip(' \t·-|,')
        if not t: continue
        if _RASTROS.search(t): continue                # menciona al proveedor
        if _PACK.match(t): continue                    # nota de packaging
        if re.fullmatch(r'[\d\s\.\-]+', t): continue   # linea solo-numeros
        out.append(t)
    txt = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()
    return txt or None

# ---------- re-hospedar fotos en Cloudinary ----------
def rehost_foto(url, public_id):
    """Sube UNA foto (desde su URL) a Cloudinary optimizada. Devuelve URL propia o None."""
    if not url: return None
    try:
        safe = requests.utils.requote_uri(str(url))    # encodea espacios/no-ASCII
        r = cloudinary.uploader.upload(
            safe, public_id=public_id, folder="catalogo",
            overwrite=True, resource_type="image", format="jpg",
            transformation=[{"width": 800, "height": 800, "crop": "limit", "quality": "auto:good"}],
        )
        return r.get("secure_url")
    except Exception as e:
        print(f"    rehost fallo {public_id}: {str(e)[:120]}")
        return None

def rehost_fotos(cod, urls):
    """Sube TODAS las fotos de un producto. Devuelve lista de URLs Cloudinary (sin duplicados)."""
    out, seen = [], set()
    for i, u in enumerate(urls or []):
        if not u or u in seen: continue
        seen.add(u)
        nu = rehost_foto(u, f"{cod}_{i}")
        if nu: out.append(nu)
    return out
