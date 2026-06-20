# Victtorino — Sistema Multi-Agente

## Contexto del negocio
Comercializadora Victtorino Victor Mellado SPA — tienda de griferías, baño y cocina.
Canales: MercadoLibre (x3 cuentas), Falabella, París, Walmart, victtorino.cl.
ERP: Defontana. Bodega: La Cisterna, Santiago.

## Cómo iniciar el sistema
```
cd C:\Users\dell\victtorino
python main.py
```

## Estructura del proyecto
```
victtorino/
├── main.py              # Entrada principal — interfaz de chat
├── orchestrator.py      # Enrutador de consultas a los 7 agentes
├── config.py            # Variables de configuración
├── .env                 # API keys (no subir a git)
├── agents/
│   ├── base_agent.py    # Clase base con carga de datos y caché
│   ├── sales.py         # Agente de Ventas — datos Defontana
│   ├── inventory.py     # Agente de Inventario
│   ├── finance.py       # Agente de Finanzas
│   ├── marketing.py     # Agente de Marketing
│   ├── operations.py    # Agente de Operaciones
│   ├── customer_service.py  # Agente de Atención al Cliente
│   └── strategic.py     # Agente Estratégico — acceso a todos los datos
└── data/
    ├── loader.py        # Carga archivos Excel (xlsx reales + xls HTML de Defontana)
    └── excel/           # Archivos de datos
        ├── Ventas.xls       # Exportado desde Defontana — informe consolidado x artículo
        ├── inventario.xlsx
        ├── finanzas.xlsx
        ├── marketing.xlsx
        ├── operaciones.xlsx
        └── atencion_cliente.xlsx
```

## Reglas críticas del proyecto

### Archivos de Defontana
- Defontana exporta archivos `.xls` que son **HTML disfrazado**, NO Excel binario
- Usar `pd.read_html()` con `encoding='iso-8859-1'` — NUNCA `pd.read_excel()` para estos archivos
- El loader detecta automáticamente el tipo de archivo por sus primeros bytes
- Para actualizar datos: reemplazar el archivo en `data/excel/` — el agente recarga automáticamente

### Listas de precios Defontana
- ML: precio base × 1.65
- Falabella: ML + 10%
- París / Walmart: ML + 5%
- Web (victtorino.cl): base + 10%
- Tienda presencial: base + 3%
- Ticket alto: base × 1.55
- Mayorista: base × 1.35

### Dependencias requeridas
```
pip install anthropic pandas lxml openpyxl rich
```

### Variables de entorno (.env)
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Los 7 agentes y sus datos

| Agente | Archivo de datos | Área |
|--------|-----------------|------|
| ventas | Ventas.xls | GMV, SKUs, márgenes Defontana |
| inventario | inventario.xlsx | Stock, quiebres, reposición |
| finanzas | finanzas.xlsx | P&L, márgenes, flujo de caja |
| marketing | marketing.xlsx | Campañas, ROAS, redes sociales |
| operaciones | operaciones.xlsx | Despachos, publicaciones, KPIs |
| atencion_cliente | atencion_cliente.xlsx | Reclamos, satisfacción, ML reputation |
| estrategico | todos los anteriores | Visión global, decisiones clave |

## Comandos del sistema
- `/agentes` — lista los 7 agentes disponibles
- `/reset` — borra historial de conversación
- `/ayuda` — muestra ayuda
- `/salir` — cierra el sistema

## Proyectos relacionados
- **Victoria** — agente IA WhatsApp en Railway: `victoria-agente-production.up.railway.app`
- **Contigo.IA** — proyecto de acompañamiento adultos mayores
- **API Defontana** — reunión pendiente para integración directa

## Anti-patterns — NO hacer
- No usar `pd.read_excel()` para archivos exportados de Defontana
- No hardcodear rutas absolutas — usar `DATA_DIR` de config.py
- No subir `.env` al repositorio
- No modificar `base_agent.py` sin probar que el caché de datos sigue funcionando
