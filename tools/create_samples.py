"""
Genera archivos Excel de muestra con datos realistas de Victtorino
para poder probar el sistema multi-agente sin datos reales.

Uso: python tools/create_samples.py
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "excel"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANALES = [
    "MercadoLibre Cuenta 1",
    "MercadoLibre Cuenta 2",
    "MercadoLibre Cuenta 3",
    "Falabella",
    "París",
    "Walmart",
    "Web victtorino.cl",
]

SKUS = [
    ("VIC-001", "Mezcladora Cocina Monomando Cromo"),
    ("VIC-002", "Mezcladora Baño Monomando Negro Mate"),
    ("VIC-003", "Ducha Rain Shower 30cm"),
    ("VIC-004", "Llave Paso Agua 1/2 Pulgada"),
    ("VIC-005", "Grifería Lavabo Cuello Alto Dorado"),
    ("VIC-006", "Set Ducha Termostática 2 Salidas"),
    ("VIC-007", "Mezcladora Bidet Cromo"),
    ("VIC-008", "Válvula Esfera 3/4 Pulgada"),
    ("VIC-009", "Porta Toalla Barra 60cm Inox"),
    ("VIC-010", "Dispensador Jabón Empotrado"),
    ("VIC-011", "Cabezal Ducha Circular 20cm"),
    ("VIC-012", "Mezcladora Cocina Cuello Giratorio"),
    ("VIC-013", "Grifería Lavamanos Dos Palancas"),
    ("VIC-014", "Kit Ducha Completo con Barra"),
    ("VIC-015", "Sifón Lavabo Botella PVC"),
]

PRECIOS = {
    "VIC-001": 45990, "VIC-002": 52990, "VIC-003": 89990, "VIC-004": 4990,
    "VIC-005": 78990, "VIC-006": 189990, "VIC-007": 39990, "VIC-008": 6990,
    "VIC-009": 24990, "VIC-010": 34990, "VIC-011": 29990, "VIC-012": 49990,
    "VIC-013": 41990, "VIC-014": 129990, "VIC-015": 8990,
}

COSTOS = {sku: int(precio * random.uniform(0.42, 0.58)) for sku, precio in PRECIOS.items()}

today = date.today()


def random_date(days_back: int = 90) -> date:
    return today - timedelta(days=random.randint(0, days_back))


# ─── ventas.xlsx ───────────────────────────────────────────────────────────────

def make_ventas():
    rows = []
    for _ in range(600):
        sku, desc = random.choice(SKUS)
        canal = random.choice(CANALES)
        qty = random.randint(1, 8)
        precio = PRECIOS[sku]
        rows.append({
            "Fecha": random_date(90),
            "Canal": canal,
            "SKU": sku,
            "Descripción": desc,
            "Cantidad": qty,
            "Precio_Unit": precio,
            "Monto": precio * qty,
        })
    ventas_df = pd.DataFrame(rows).sort_values("Fecha", ascending=False)

    top_skus = (
        ventas_df.groupby(["SKU", "Descripción"])
        .agg(Unidades=("Cantidad", "sum"), Ingresos=("Monto", "sum"))
        .sort_values("Ingresos", ascending=False)
        .reset_index()
        .head(10)
    )

    resumen = (
        ventas_df.groupby("Canal")
        .agg(Unidades=("Cantidad", "sum"), Ingresos=("Monto", "sum"), Transacciones=("SKU", "count"))
        .reset_index()
    )
    resumen["Ticket_Promedio"] = (resumen["Ingresos"] / resumen["Transacciones"]).astype(int)

    path = OUTPUT_DIR / "ventas.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        ventas_df.to_excel(w, sheet_name="Ventas", index=False)
        top_skus.to_excel(w, sheet_name="Top_SKUs", index=False)
        resumen.to_excel(w, sheet_name="Resumen_Canal", index=False)
    print(f"  [OK] {path}")


# ─── inventario.xlsx ───────────────────────────────────────────────────────────

def make_inventario():
    stock_rows = []
    for sku, desc in SKUS:
        stock = random.randint(0, 150)
        stock_min = random.choice([5, 10, 15, 20])
        stock_rows.append({
            "SKU": sku,
            "Descripción": desc,
            "Stock_Actual": stock,
            "Stock_Mínimo": stock_min,
            "Stock_Estado": "CRÍTICO" if stock <= stock_min else ("OK" if stock > stock_min * 2 else "BAJO"),
            "Ubicación": random.choice(["Bodega A", "Bodega B", "Bodega C"]),
            "Días_Stock_Estimado": stock * random.randint(3, 12),
        })
    stock_df = pd.DataFrame(stock_rows)

    mov_rows = []
    tipos = ["Entrada", "Venta", "Devolución", "Ajuste"]
    for _ in range(200):
        sku, _ = random.choice(SKUS)
        tipo = random.choice(tipos)
        qty = random.randint(1, 30) if tipo == "Entrada" else -random.randint(1, 10)
        mov_rows.append({
            "Fecha": random_date(60),
            "SKU": sku,
            "Tipo": tipo,
            "Cantidad": qty,
            "Motivo": "Compra proveedor" if tipo == "Entrada" else tipo,
        })
    mov_df = pd.DataFrame(mov_rows).sort_values("Fecha", ascending=False)

    alertas_df = stock_df[stock_df["Stock_Estado"].isin(["CRÍTICO", "BAJO"])][
        ["SKU", "Descripción", "Stock_Actual", "Stock_Mínimo", "Stock_Estado"]
    ].copy()

    path = OUTPUT_DIR / "inventario.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        stock_df.to_excel(w, sheet_name="Stock_Actual", index=False)
        mov_df.to_excel(w, sheet_name="Movimientos", index=False)
        alertas_df.to_excel(w, sheet_name="Alertas", index=False)
    print(f"  [OK] {path}")


# ─── marketing.xlsx ────────────────────────────────────────────────────────────

def make_marketing():
    campañas = [
        ("ML Ads - Mezcladoras Cocina", "MercadoLibre"),
        ("ML Ads - Ducha Rain Shower", "MercadoLibre"),
        ("Google Shopping - General", "Google Ads"),
        ("Meta - Renovación Baño", "Meta Ads"),
        ("Falabella Sponsored", "Falabella"),
    ]
    camp_rows = []
    for nombre, plataforma in campañas:
        presupuesto = random.randint(50000, 300000)
        gasto = int(presupuesto * random.uniform(0.6, 1.0))
        clicks = random.randint(200, 3000)
        conv = random.randint(5, int(clicks * 0.08))
        ingresos = conv * random.randint(30000, 90000)
        camp_rows.append({
            "Campaña": nombre,
            "Plataforma": plataforma,
            "Presupuesto": presupuesto,
            "Gasto": gasto,
            "Clicks": clicks,
            "CTR_%": round(clicks / random.randint(3000, 15000) * 100, 2),
            "Conversiones": conv,
            "CPA": int(gasto / conv) if conv else 0,
            "Ingresos_Atribuidos": ingresos,
            "ROAS": round(ingresos / gasto, 2) if gasto else 0,
        })
    camp_df = pd.DataFrame(camp_rows)

    redes_rows = []
    for d in range(30):
        fecha = today - timedelta(days=d)
        for plataforma in ["Instagram", "Facebook", "TikTok"]:
            redes_rows.append({
                "Fecha": fecha,
                "Plataforma": plataforma,
                "Alcance": random.randint(1000, 15000),
                "Impresiones": random.randint(2000, 25000),
                "Engagement": random.randint(50, 800),
                "Seguidores_Total": random.randint(4000, 12000),
                "Nuevos_Seguidores": random.randint(5, 80),
            })
    redes_df = pd.DataFrame(redes_rows)

    tendencias = [
        ("mezcladora cocina", 8900, "Alta"),
        ("ducha lluvia", 5400, "Alta"),
        ("grifería dorada baño", 3200, "Media"),
        ("llave termostatica", 2800, "Media"),
        ("grifo negro mate", 4100, "Alta"),
        ("kit ducha completo", 6700, "Alta"),
        ("bidet eléctrico", 1200, "Baja"),
        ("dispensador jabón empotrado", 900, "Baja"),
    ]
    tend_df = pd.DataFrame(tendencias, columns=["Keyword", "Búsquedas_Mensuales", "Tendencia"])

    path = OUTPUT_DIR / "marketing.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        camp_df.to_excel(w, sheet_name="Campañas_Activas", index=False)
        redes_df.to_excel(w, sheet_name="Redes_Sociales", index=False)
        tend_df.to_excel(w, sheet_name="Tendencias", index=False)
    print(f"  [OK] {path}")


# ─── finanzas.xlsx ─────────────────────────────────────────────────────────────

def make_finanzas():
    pl_rows = []
    for m in range(6):
        mes = (today.replace(day=1) - timedelta(days=m * 30)).strftime("%Y-%m")
        ingresos = random.randint(8_000_000, 18_000_000)
        cogs = int(ingresos * random.uniform(0.45, 0.55))
        margen_bruto = ingresos - cogs
        gastos_op = int(ingresos * random.uniform(0.15, 0.25))
        ebitda = margen_bruto - gastos_op
        pl_rows.append({
            "Período": mes,
            "Ingresos": ingresos,
            "COGS": cogs,
            "Margen_Bruto": margen_bruto,
            "Margen_Bruto_%": round(margen_bruto / ingresos * 100, 1),
            "Gastos_Operativos": gastos_op,
            "EBITDA": ebitda,
            "EBITDA_%": round(ebitda / ingresos * 100, 1),
        })
    pl_df = pd.DataFrame(pl_rows)

    margin_rows = []
    for sku, desc in SKUS:
        precio = PRECIOS[sku]
        costo = COSTOS[sku]
        margen = precio - costo
        margin_rows.append({
            "SKU": sku,
            "Descripción": desc,
            "Precio_Venta": precio,
            "Costo": costo,
            "Margen_$": margen,
            "Margen_%": round(margen / precio * 100, 1),
            "Comisión_ML_%": 12,
            "Margen_Neto_ML": round((precio * 0.88) - costo),
        })
    margin_df = pd.DataFrame(margin_rows)

    flujo_rows = []
    conceptos_ingresos = ["Ventas ML C1", "Ventas ML C2", "Ventas ML C3", "Ventas Falabella", "Ventas Web"]
    conceptos_egresos = ["Proveedores", "Logística", "Publicidad", "Arriendo Bodega", "Sueldos", "Servicios"]
    for d in range(30):
        fecha = today + timedelta(days=d - 5)
        if d % 3 == 0:
            flujo_rows.append({
                "Fecha": fecha,
                "Concepto": random.choice(conceptos_ingresos),
                "Monto": random.randint(500_000, 3_000_000),
                "Tipo": "Ingreso",
            })
        flujo_rows.append({
            "Fecha": fecha,
            "Concepto": random.choice(conceptos_egresos),
            "Monto": -random.randint(100_000, 1_200_000),
            "Tipo": "Egreso",
        })
    flujo_df = pd.DataFrame(flujo_rows).sort_values("Fecha")

    path = OUTPUT_DIR / "finanzas.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        pl_df.to_excel(w, sheet_name="PL_Mensual", index=False)
        margin_df.to_excel(w, sheet_name="Margenes_SKU", index=False)
        flujo_df.to_excel(w, sheet_name="Flujo_Caja", index=False)
    print(f"  [OK] {path}")


# ─── operaciones.xlsx ──────────────────────────────────────────────────────────

def make_operaciones():
    pub_rows = []
    estados = ["Activa", "Activa", "Activa", "Pausada", "Sin Stock"]
    for canal in CANALES:
        for sku, desc in SKUS:
            estado = random.choices(estados, weights=[60, 10, 5, 15, 10])[0]
            pub_rows.append({
                "Canal": canal,
                "SKU": sku,
                "Título": desc,
                "Estado": estado,
                "Precio_Publicado": PRECIOS[sku],
                "Stock_Publicado": random.randint(0, 50) if estado != "Sin Stock" else 0,
                "Visitas_7d": random.randint(0, 300),
            })
    pub_df = pd.DataFrame(pub_rows)

    despacho_rows = []
    estados_despacho = ["Entregado", "Entregado", "Entregado", "En Tránsito", "Pendiente"]
    for i in range(100):
        canal = random.choice(CANALES)
        sku, desc = random.choice(SKUS)
        estado = random.choices(estados_despacho, weights=[50, 15, 10, 15, 10])[0]
        despacho_rows.append({
            "Orden": f"ORD-{10000 + i}",
            "Fecha": random_date(14),
            "Canal": canal,
            "SKU": sku,
            "Estado": estado,
            "Tiempo_Preparación_h": random.randint(1, 48),
            "En_Plazo": random.choice([True, True, True, False]),
        })
    despacho_df = pd.DataFrame(despacho_rows).sort_values("Fecha", ascending=False)

    kpis = [
        ("Tiempo Promedio Preparación (h)", 6.2, 8, "OK"),
        ("% Entregas en Plazo", 94.1, 95, "BAJO"),
        ("Publicaciones Activas", pub_df[pub_df["Estado"] == "Activa"].shape[0], None, "INFO"),
        ("Publicaciones Pausadas", pub_df[pub_df["Estado"] == "Pausada"].shape[0], 0, "ALERTA"),
        ("Publicaciones Sin Stock", pub_df[pub_df["Estado"] == "Sin Stock"].shape[0], 0, "ALERTA"),
        ("Tasa Devolución %", 2.3, 3, "OK"),
    ]
    kpi_df = pd.DataFrame(kpis, columns=["Métrica", "Valor_Actual", "Meta", "Estado"])

    path = OUTPUT_DIR / "operaciones.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        pub_df.to_excel(w, sheet_name="Publicaciones", index=False)
        despacho_df.to_excel(w, sheet_name="Despachos_Recientes", index=False)
        kpi_df.to_excel(w, sheet_name="KPIs_Operativos", index=False)
    print(f"  [OK] {path}")


# ─── atencion_cliente.xlsx ─────────────────────────────────────────────────────

def make_atencion_cliente():
    motivos = [
        "Producto dañado al llegar",
        "Demora en despacho",
        "Producto no coincide con descripción",
        "Solicitud de garantía",
        "Consulta técnica de instalación",
        "Error en pedido (SKU incorrecto)",
        "Solicitud de devolución",
    ]
    urgencias = ["Alta", "Media", "Baja"]
    estados_reclamo = ["Abierto", "En Proceso", "Escalado"]

    reclamo_rows = []
    for i in range(30):
        canal = random.choice(CANALES)
        reclamo_rows.append({
            "ID": f"RC-{2024 + i}",
            "Canal": canal,
            "Fecha": random_date(15),
            "Motivo": random.choice(motivos),
            "Estado": random.choice(estados_reclamo),
            "Urgencia": random.choices(urgencias, weights=[20, 50, 30])[0],
            "SLA_Horas": random.choice([4, 8, 24, 48]),
            "Horas_Transcurridas": random.randint(1, 72),
        })
    reclamo_df = pd.DataFrame(reclamo_rows).sort_values(
        ["Urgencia", "Horas_Transcurridas"], ascending=[True, False]
    )

    faq_data = [
        ("¿Tienen garantía los productos?", "Sí, todos nuestros productos tienen garantía de 12 meses contra defectos de fabricación. Para hacerla efectiva, conserva la boleta y contáctanos por el canal de compra."),
        ("¿Hacen instalación?", "No realizamos instalación directamente, pero podemos recomendar gasfiteres certificados en tu zona. Nuestros productos vienen con manual de instalación detallado."),
        ("¿El producto llegó dañado, qué hago?", "Fotografía el embalaje y el producto dañado y escríbenos de inmediato por el canal donde compraste. Gestionamos el cambio sin costo en un plazo de 48 horas hábiles."),
        ("¿Cuánto demora el despacho?", "Despacho en 24-48 horas hábiles para Región Metropolitana. Regiones entre 3-7 días hábiles según operador logístico."),
        ("¿Puedo devolver un producto que no me gustó?", "Sí, tienes hasta 10 días desde la recepción para devoluciones por arrepentimiento. El producto debe estar sin uso y en su embalaje original."),
        ("¿Los materiales son de calidad certificada?", "Sí, nuestras griferías son de latón niquelado y cromado según norma ISO. Los certificados están disponibles en victtorino.cl/certificaciones"),
    ]
    faq_df = pd.DataFrame(faq_data, columns=["Pregunta", "Respuesta_Sugerida"])

    metricas = []
    for m in range(3):
        mes = (today.replace(day=1) - timedelta(days=m * 30)).strftime("%Y-%m")
        for canal in ["MercadoLibre C1", "MercadoLibre C2", "MercadoLibre C3", "Falabella", "Walmart"]:
            metricas.append({
                "Período": mes,
                "Canal": canal,
                "Calificación_Promedio": round(random.uniform(4.2, 5.0), 1),
                "NPS": random.randint(45, 80),
                "Reclamos_Cerrados": random.randint(5, 30),
                "Tiempo_Respuesta_h": round(random.uniform(1.5, 12), 1),
                "Reputación_ML": random.choice(["Verde", "Verde", "Amarillo"]),
            })
    metricas_df = pd.DataFrame(metricas)

    path = OUTPUT_DIR / "atencion_cliente.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        reclamo_df.to_excel(w, sheet_name="Reclamos_Activos", index=False)
        faq_df.to_excel(w, sheet_name="FAQ", index=False)
        metricas_df.to_excel(w, sheet_name="Metricas_Satisfaccion", index=False)
    print(f"  [OK] {path}")


if __name__ == "__main__":
    print(f"\nGenerando datos de muestra en {OUTPUT_DIR}/\n")
    make_ventas()
    make_inventario()
    make_marketing()
    make_finanzas()
    make_operaciones()
    make_atencion_cliente()
    print("\nListo. Ejecuta: python main.py\n")
