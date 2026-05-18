import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# claude-sonnet-4-6 para balance costo/calidad en un sistema con 7 agentes activos.
# Cambiar a claude-opus-4-7 para máxima inteligencia cuando sea necesario.
AGENT_MODEL = "claude-sonnet-4-6"
ROUTER_MODEL = "claude-sonnet-4-6"

MAX_TOKENS = 2048
HISTORY_LIMIT = 20  # últimos N mensajes que se pasan a cada agente

DATA_DIR = Path(__file__).parent / "data" / "excel"

COMPANY = "Victtorino"
CATEGORY = "griferías, baño y cocina"

CHANNELS = [
    "MercadoLibre Cuenta 1",
    "MercadoLibre Cuenta 2",
    "MercadoLibre Cuenta 3",
    "Falabella",
    "París",
    "Walmart",
    "Web victtorino.cl",
]

AGENT_STYLES = {
    "ventas":           ("green",   "📈", "Ventas"),
    "inventario":       ("yellow",  "📦", "Inventario"),
    "marketing":        ("magenta", "📣", "Marketing"),
    "finanzas":         ("cyan",    "💰", "Finanzas"),
    "operaciones":      ("blue",    "⚙️",  "Operaciones"),
    "atencion_cliente": ("red",     "🎧", "Atención Cliente"),
    "estrategico":      ("white",   "🧭", "Estratégico"),
}
