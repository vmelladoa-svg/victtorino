# -*- coding: utf-8 -*-
"""Traduce términos chinos de embalaje/dimensiones al español (sin API, gratis).
Reemplazo por términos: cubre los valores actuales y combinaciones futuras del
catálogo mayorista (AlilaTop). Lo que no esté mapeado se limpia de chino al final."""
import re

# Chino -> Español. Se aplica de MÁS LARGO a más corto (para que los compuestos
# ganen a los caracteres sueltos). Mantiene números/medidas (17*17*23cm, etc.).
TERM = {
    # compuestos largos
    "单个彩盒产量尺寸": "tamaño caja individual", "产品彩盒尺寸": "tamaño de caja del producto",
    "透明密封手提袋": "bolsa de mano transparente sellada", "加厚5层纸箱": "caja de cartón reforzada de 5 capas",
    "5层牛皮纸箱": "caja kraft de 5 capas", "牛皮纸盒": "caja de papel kraft",
    "真空压缩袋": "bolsa de compresión al vacío", "真空包装": "envasado al vacío",
    "吸塑卡纸": "blíster con cartón", "收纳网袋": "bolsa de red organizadora",
    "气泡袋": "bolsa de burbujas", "数据线长": "largo del cable de datos", "数据线": "cable de datos",
    "哑铃片": "disco de mancuerna", "哑铃杆": "barra de mancuerna", "大衣架": "perchero",
    "敲琴尺寸": "tamaño del instrumento", "内置海绵": "con esponja interior",
    "彩纸套": "funda de papel a color", "塑封膜": "film termosellado", "牛皮盒": "caja kraft",
    "编织袋": "saco tejido", "塑料袋": "bolsa plástica", "手提袋": "bolsa de mano",
    "过塑封": "laminado", "纸外箱": "caja exterior de cartón",
    # cuantificadores / prefijos
    "单个": "individual", "单套": "por juego", "单包": "por paquete", "单张": "por lámina",
    "盒装": "en caja", "袋装": "en bolsa", "装好": "empacado", "包装": "",
    # tipos de empaque
    "彩盒": "caja a color", "彩卡": "tarjeta a color", "彩色": "a color",
    "纸箱": "caja de cartón", "纸盒": "caja de cartón", "纸卡": "tarjeta de cartón",
    "纸包": "envuelto en papel", "外箱": "caja exterior", "内盒": "caja interior",
    "白盒": "caja blanca", "塑盒": "caja plástica", "塑封": "termosellado",
    "布袋": "bolsa de tela", "袋子": "bolsa", "泡壳": "blíster", "双泡": "doble burbuja",
    "气泡": "burbuja", "皮筋": "banda elástica", "绑带": "con cinta", "插卡": "con tarjeta",
    "收纳": "organizador", "海绵": "esponja", "唛头": "etiqueta de envío",
    "英文": "en inglés", "中性": "neutro", "裸装": "a granel", "外套": "funda exterior",
    "透明": "transparente", "密封": "sellado", "抽真空": "al vacío", "真空": "al vacío",
    "加厚": "reforzado", "均码": "talla única", "角塞": "tapón de esquina", "螺丝": "tornillo",
    "圆珠": "esfera", "底座": "base", "尺寸": "tamaño", "产品": "producto", "产量": "producto",
    "白色": "blanco", "白": "blanco", "含": "incluye",
    # dimensiones
    "长": "largo", "宽": "ancho", "高": "alto", "米": "m", "两": "2",
    # contadores y sueltos (al final)
    "瓶": " botellas", "卷": " rollos", "套": " juego", "根": " u", "把": " u",
    "个": " u", "片": " u", "盒": "caja", "袋": "bolsa", "箱": "caja", "卡": "tarjeta",
    "包": "paquete", "装": "", "膜": "film", "套1袋": "x bolsa",
}
# orden de aplicación: clave más larga primero
_ORDEN = sorted(TERM.keys(), key=len, reverse=True)

_CJK = re.compile(r'[　-〿㐀-䶿一-鿿豈-﫿]')

def traducir(s):
    """Traduce términos chinos a español; limpia puntuación CJK y restos."""
    if not s:
        return s
    for cn in _ORDEN:
        if cn in s:
            s = s.replace(cn, " " + TERM[cn] + " ")
    # puntuación china -> latina
    s = (s.replace("，", ", ").replace("、", ", ").replace("（", " (").replace("）", ")")
           .replace("：", ": ").replace("　", " "))
    # quitar cualquier carácter chino que haya quedado sin mapear
    s = _CJK.sub("", s)
    # normalizar espacios/comas sobrantes
    s = re.sub(r'\s{2,}', ' ', s)
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    s = re.sub(r'\s*,\s*', ', ', s).strip(" ,+-/")
    return s or None


# ── Limpieza de contactos ajenos (proveedor AlilaTop) en descripciones HTML ──
# Quita WhatsApp/WeChat/+86, frases "ponerse en contacto conmigo", teléfonos
# sueltos y atributos data-spm de Alibaba. NO toca usos legítimos ("soporte
# para teléfono", "superficie de contacto", "control por teléfono móvil").
def _es_contacto(p_html):
    t = p_html.lower()
    if re.search(r"whats|wechat|we chat|\+86|微信|qq[:：]", t):
        return True
    if "contacto conmigo" in t or "ponerse en contacto" in t:
        return True
    solo = re.sub(r"<[^>]+>|\s", "", p_html)  # ¿el párrafo es sólo un teléfono?
    if re.fullmatch(r"\+?\d{7,}", solo):
        return True
    return False

def limpiar_contacto(html):
    if not html:
        return html
    s = re.sub(r'\s*data-spm[a-z-]*="[^"]*"', "", html)         # cruft de Alibaba
    s = re.sub(r"<p[^>]*>.*?</p>", lambda m: "" if _es_contacto(m.group(0)) else m.group(0), s, flags=re.S)
    s = re.sub(r"(whats?app?|wechat|we chat)\s*[:+]?\s*\+?\d[\d\s-]{5,}", "", s, flags=re.I)
    s = re.sub(r"\+86[\d\s-]{6,}", "", s)                        # números chinos sueltos
    s = re.sub(r"<p[^>]*>\s*(<br\s*/?>)?\s*</p>", "", s)         # párrafos vacíos
    s = re.sub(r"[ \t]{2,}", " ", s).strip()
    return s or None


if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    pruebas = ["塑料袋", "彩盒", "单个opp袋包装", "纸箱+编织袋包装", "单个英文彩盒包装",
               "加厚5层纸箱", "哑铃杆40cm", "彩盒17*17*23cm", "底座2.5*57，19高cm,2个",
               "10个一把套opp袋（36把）", "单个英文吸塑卡纸包装，10个吸塑一内盒"]
    for p in pruebas:
        print(f"{p}  ->  {traducir(p)}")
