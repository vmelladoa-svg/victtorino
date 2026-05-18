import os
import anthropic
from config import ANTHROPIC_API_KEY, AGENT_MODEL, MAX_TOKENS, HISTORY_LIMIT, COMPANY, CATEGORY, CHANNELS, DATA_DIR
from data.loader import load_excel, format_data


class BaseAgent:
    """
    Clase base para todos los agentes especializados de Victtorino.

    Cada agente hijo define su rol, instrucciones y archivos Excel de datos.
    Los datos se recargan automáticamente cuando detecta que algún archivo
    fue modificado — basta con reemplazar el Excel sin reiniciar el agente.
    """

    def __init__(
        self,
        name: str,
        emoji: str,
        role: str,
        instructions: str,
        data_files: list[str] | None = None,
    ):
        self.name = name
        self.emoji = emoji
        self.role = role
        self.instructions = instructions
        self.data_files = data_files or []
        self._client: anthropic.Anthropic | None = None
        self._data_cache: str = ""
        self._file_mtimes: dict[str, float] = {}

    @property
    def client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        return self._client

    def _files_changed(self) -> bool:
        """Devuelve True si algún archivo de datos fue modificado desde la última carga."""
        for filename in self.data_files:
            # Buscar el archivo sin importar mayúsculas/minúsculas
            path = DATA_DIR / filename
            if not path.exists():
                for candidate in DATA_DIR.iterdir():
                    if candidate.stem.lower() == path.stem.lower():
                        path = candidate
                        break
            if path.exists():
                mtime = os.path.getmtime(path)
                if self._file_mtimes.get(str(path)) != mtime:
                    return True
        return False

    def _update_mtimes(self):
        """Actualiza el registro de fechas de modificación."""
        for filename in self.data_files:
            path = DATA_DIR / filename
            if not path.exists():
                for candidate in DATA_DIR.iterdir():
                    if candidate.stem.lower() == path.stem.lower():
                        path = candidate
                        break
            if path.exists():
                self._file_mtimes[str(path)] = os.path.getmtime(path)

    def _load_data(self) -> str:
        """Carga los datos, usando caché si los archivos no cambiaron."""
        if self._data_cache and not self._files_changed():
            return self._data_cache

        # Recargar
        parts = []
        for filename in self.data_files:
            sheets = load_excel(filename)
            parts.append(f"## Datos de {filename}")
            parts.append(format_data(sheets))

        self._data_cache = "\n\n".join(parts)
        self._update_mtimes()

        if self._files_changed() is False and self._data_cache:
            pass  # carga exitosa

        return self._data_cache

    def _build_system(self) -> list[dict]:
        """Construye el system prompt con los datos más recientes."""
        context_lines = [
            f"Eres el {self.role} de {COMPANY}, empresa chilena especializada en {CATEGORY}.",
            f"Canales de venta activos: {', '.join(CHANNELS)}.",
            "",
            self.instructions,
        ]

        data = self._load_data()
        if data:
            context_lines += ["", "## DATOS ACTUALES", data]

        context_lines += [
            "",
            "## INSTRUCCIONES DE RESPUESTA",
            "- Responde siempre en español.",
            "- Sé conciso y accionable: prioriza insights y recomendaciones concretas.",
            "- Si los datos son insuficientes, indícalo claramente y sugiere qué archivo cargar.",
            "- Usa formato Markdown cuando ayude a la claridad (tablas, listas).",
            "- Números en formato chileno: usa puntos para miles (ej: $45.990).",
        ]

        return [
            {
                "type": "text",
                "text": "\n".join(context_lines),
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def respond(self, query: str, history: list[dict]) -> str:
        """Genera una respuesta usando el historial de conversación."""
        messages = history[-HISTORY_LIMIT:] + [{"role": "user", "content": query}]

        response = self.client.messages.create(
            model=AGENT_MODEL,
            max_tokens=MAX_TOKENS,
            system=self._build_system(),
            messages=messages,
        )
        return response.content[0].text
