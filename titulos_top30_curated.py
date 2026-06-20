"""
Títulos optimizados redactados manualmente para los TOP 30 items SEO de cero.
Cada uno construido con: producto + spec principal + material + color/acabado + marca.
Cuidando: 55-60 chars, capitalización tipo Título, sin redundancia.
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
TOP30 = json.loads((ROOT / "top30_con_atributos.json").read_text(encoding="utf-8"))
OUT = ROOT / "titulos_top30_aprobacion.xlsx"

# Diccionario: iid → título sugerido
CURATED = {
    # 1. Flexible Gas Hi-hi 100cm - C1
    "MLC1859010123": "Flexible Para Gas Hi-Hi 1/2 X 3/8 100cm Trenzado Täumm",
    # 2. Monomando Tina Ducha Notte - C1
    "MLC1858982017": "Monomando Tina Ducha Notte Acero Negro Mate Täumm Baño",
    # 3-5. Kit Wc Anclaje Antifuga (3 cuentas, mismo SKU)
    "MLC2961406356": "Kit Wc Anclaje Antifuga Admisión Acero Inoxidable Täumm",
    "MLC589408143":  "Kit Wc Anclaje Antifuga Admisión Acero Inoxidable Täumm",
    "MLC2992444340": "Kit Wc Anclaje Antifuga Admisión Acero Inoxidable Täumm",
    # 6. Monomando Tina Ducha Notte (sin color en título) - C2
    "MLC1879566481": "Monomando Mezclador Tina Ducha Notte Negro Mate Täumm",
    # 7. Dispensador Jabón Schwarz Negro - C1
    "MLC3585586956": "Dispensador De Jabón Schwarz Plástico Negro Pared Täumm",
    # 8. Monomando Lavaplato Colomba Plateado Brillante - C1
    "MLC1858804939": "Monomando Lavaplatos Vertical Colomba Plateado Brillante Täumm",
    # 9. Kit Wc Anclaje 4ta copia - C2
    "MLC589408232":  "Kit Wc Anclaje Antifuga Admisión Acero Inoxidable Täumm",
    # 10. Válvula Electrónica Urinario - C3
    "MLC3724919200": "Válvula Electrónica Urinario Descarga Sensor Acero Täumm",
    # 11. Porta Toalla Mano Acero Inox Premium - C2
    "MLC1524613562": "Toallero Barra Mano Acero Inoxidable Cepillado Plateado Täumm",
    # 12-13. Brazo Ducha Techo 25cm - C1 + C2
    "MLC1366197832": "Brazo Tubo Ducha Techo Redondo 25cm Cromado Victtorino",
    "MLC1366185046": "Brazo Tubo Ducha Techo Redondo 25cm Cromado Victtorino",
    # 14. Barra Seguridad con Jabonera 40cm - C1
    "MLC1858919499": "Barra Seguridad Jabonera Baño 40cm Acero Inox Cromado Täumm",
    # 15-17. Toalla Papel Interfoliada 200 Un (3 cuentas)
    "MLC2300909570": "Toalla Papel Interfoliada Doble Hoja 200 Unidades Victtorino",
    "MLC2300794346": "Toalla Papel Interfoliada Doble Hoja 200 Unidades Victtorino",
    "MLC2300604098": "Toalla Papel Interfoliada Doble Hoja 200 Unidades Victtorino",
    # 18. Llave Monomando Modern (redundancia "Plateado Cepillado x2") - C2
    "MLC1882285803": "Llave Monomando Lavatorio Modern Plateado Cepillado Inox Täumm",
    # 19. Llave Monomando Modern Lavamanos - C3
    "MLC1513791879": "Llave Monomando Lavatorio Modern Inox Plateado Cepillado Täumm",
    # 20. Barra Soporte Ducha 65cm (Color "52053" mal seteado) - C1
    "MLC2189367944": "Barra Seguridad Soporte Ducha Teléfono Adaptable 65cm Cromado",
    # 21. Ducha Fija Difusor ABS - C3
    "MLC1307531930": "Ducha Fija Con Difusor Al Muro Abs Cromado Plateado Täumm",
    # 22. Agarradera 135° Barra Curva - C3
    "MLC2999177164": "Agarradera Barra Curva Seguridad 135° 46cm Cromada Täumm",
    # 23. Flexible Lavadora 150cm Lila Cromado - C2
    "MLC3746556806": "Flexible Lavadora Curva Hi-Hi 3/4 150cm Lila Cromado Täumm",
    # 24. Dispensador Jabón Schawarz "Negro Negro" - C2
    "MLC3741395942": "Dispensador De Jabón Schawarz Plástico Negro Pared Täumm",
    # 25. Flexible Agua He-Hi M10 35cm - C1
    "MLC580694958":  "Flexible Agua He-Hi M10 X1 X 1/2 35cm Trenzado Täumm",
    # 26. Sifón Desagüe Tina - C2
    "MLC1877730931": "Sifón Desagüe Para Tina Acero Inoxidable Cromado Täumm",
    # 27. Perchero Multifuncional - C1
    "MLC3585376560": "Perchero Multifuncional Baño Acero Inox Plateado Täumm",
    # 28. Dispensador Papel Higiénico Acrílico - C1
    "MLC581330829":  "Dispensador Papel Higiénico Acrílico Llave Plateado Täumm",
    # 29. Grifo Monomando Profesional Lavaplatos - C3
    "MLC2117169726": "Monomando Lavaplatos Cuello Extensible Cromado Inox Täumm",
    # 30. Grifo Lavaplatos Profesional - C2
    "MLC1882260683": "Monomando Lavaplatos Profesional Plateado Brillante Inox Täumm",
}


def title_score(title):
    import re
    if not title: return 0
    s = 0
    L = len(title)
    if L >= 55: s += 30
    elif L >= 40: s += 20
    elif L >= 30: s += 10
    if re.search(r"\d", title): s += 15
    if re.search(r"\b(blanco|negro|cromado|plateado|dorado|azul|rojo|verde|transparente|mate|brillante|gris|lila)\b", title, re.I): s += 15
    if re.search(r"\b(acero|inoxidable|inox|pl[áa]stico|vidrio|porcelana|cer[áa]mica|metal|cromado|abs|tr[ée]nzado)\b", title, re.I): s += 15
    if re.search(r"\b(victtorino|t[aä]umm|notte|colomba|modern|schwarz|schawarz|hi-hi|hi-he|he-hi)\b", title, re.I): s += 10
    words = title.split()
    if words and sum(1 for w in words if w[0:1].isupper()) > len(words) * 0.7: s += 10
    if "  " not in title: s += 5
    return min(s, 100)


def main():
    rows = []
    for it in TOP30:
        iid = it["iid"]
        current = it["title"]
        new = CURATED.get(iid, current)
        rows.append({
            "Cuenta": it["cuenta"],
            "ItemID": iid,
            "Cat": it["category_id"],
            "Precio": it["precio"],
            "Stock": it["stock"],
            "Título actual": current,
            "Long actual": len(current),
            "Score actual": title_score(current),
            "Título sugerido": new,
            "Long sugerido": len(new),
            "Score sugerido": title_score(new),
            "Δ Score": title_score(new) - title_score(current),
            "Urgencia": it["urgencia"],
            "Permalink": f"https://articulo.mercadolibre.cl/{iid[:3]}-{iid[3:]}",
        })
    df = pd.DataFrame(rows).sort_values("Δ Score", ascending=False)
    df.to_excel(OUT, index=False)
    print(f"OK {OUT}")
    print(f"\nDistribución mejora:")
    print(df["Δ Score"].describe())
    print(f"\nItems con Δ >= 10: {(df['Δ Score']>=10).sum()}")
    print(f"\n=== Diff por item ===")
    for _, r in df.iterrows():
        print(f"\n  Δ{r['Δ Score']:+3d}  {r['Cuenta']} {r['ItemID']}  ({r['Score actual']}→{r['Score sugerido']}, {r['Long actual']}→{r['Long sugerido']} chars)")
        print(f"        ANTES: {r['Título actual']}")
        print(f"        DESPUÉS: {r['Título sugerido']}")


if __name__ == "__main__":
    main()
