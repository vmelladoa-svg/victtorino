import anthropic
from config import ANTHROPIC_API_KEY, ROUTER_MODEL
from agents.sales import SalesAgent
from agents.inventory import InventoryAgent
from agents.marketing import MarketingAgent
from agents.finance import FinanceAgent
from agents.operations import OperationsAgent
from agents.customer_service import CustomerServiceAgent
from agents.strategic import StrategicAgent

ROUTER_SYSTEM = """Eres un enrutador de consultas para el sistema multi-agente de Victtorino.
Tu única tarea es determinar qué agente especializado debe responder cada consulta.

Agentes disponibles:
- ventas: ventas, ingresos, GMV, SKUs más vendidos, canales, conversión, ticket promedio
- inventario: stock, quiebre, reposición, existencias, bodega, movimientos de inventario
- marketing: campañas, publicidad, ROAS, redes sociales, contenido, palabras clave, posicionamiento
- finanzas: márgenes, P&L, flujo de caja, costos, rentabilidad, presupuesto, EBITDA
- operaciones: publicaciones, despachos, fulfillment, KPIs operativos, listings, pedidos
- atencion_cliente: reclamos, devoluciones, satisfacción, calificaciones, reputación, garantías
- estrategico: análisis global, estrategia, decisiones de alto nivel, cruce de múltiples áreas

Responde ÚNICAMENTE con el nombre del agente (una sola palabra en minúsculas, sin puntuación).
Ejemplos: ventas | inventario | marketing | finanzas | operaciones | atencion_cliente | estrategico"""

AGENTS = {
    "ventas": SalesAgent,
    "inventario": InventoryAgent,
    "marketing": MarketingAgent,
    "finanzas": FinanceAgent,
    "operaciones": OperationsAgent,
    "atencion_cliente": CustomerServiceAgent,
    "estrategico": StrategicAgent,
}


class Orchestrator:
    def __init__(self):
        self._client: anthropic.Anthropic | None = None
        self._agent_instances: dict = {}
        self.history: list[dict] = []
        self.last_agent_key: str | None = None

    @property
    def client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        return self._client

    def _get_agent(self, key: str):
        if key not in self._agent_instances:
            self._agent_instances[key] = AGENTS[key]()
        return self._agent_instances[key]

    def _route(self, query: str) -> str:
        response = self.client.messages.create(
            model=ROUTER_MODEL,
            max_tokens=16,
            system=ROUTER_SYSTEM,
            messages=[{"role": "user", "content": query}],
        )
        raw = response.content[0].text.strip().lower()
        for key in AGENTS:
            if key in raw:
                return key
        return "estrategico"

    def chat(self, query: str) -> tuple[str, str]:
        """
        Returns (agent_key, response_text).
        Appends the exchange to self.history so context accumulates.
        """
        agent_key = self._route(query)
        agent = self._get_agent(agent_key)
        response = agent.respond(query, self.history)

        self.history.append({"role": "user", "content": query})
        self.history.append({"role": "assistant", "content": response})
        self.last_agent_key = agent_key

        return agent_key, response

    def reset_history(self):
        self.history.clear()
        self.last_agent_key = None
