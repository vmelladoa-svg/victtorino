import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich import print as rprint
from config import AGENT_STYLES, CHANNELS, COMPANY
from orchestrator import Orchestrator

console = Console(legacy_windows=False)

HELP_TEXT = """
**Comandos disponibles:**
- `/agentes` — lista los 7 agentes y sus áreas
- `/reset` — borra el historial de conversación
- `/ayuda` — muestra este mensaje
- `/salir` — cierra el sistema

**Tip:** Escribe tu pregunta con naturalidad. El sistema detecta automáticamente qué agente responde.
"""

AGENTS_INFO = {
    "ventas":           "📈  Ventas        — GMV, SKUs, canales, conversión",
    "inventario":       "📦  Inventario    — Stock, reposición, quiebres",
    "marketing":        "📣  Marketing     — Campañas, ROAS, redes sociales",
    "finanzas":         "💰  Finanzas      — Márgenes, P&L, flujo de caja",
    "operaciones":      "⚙️   Operaciones   — Despachos, publicaciones, KPIs",
    "atencion_cliente": "🎧  At. Cliente   — Reclamos, satisfacción, reputación",
    "estrategico":      "🧭  Estratégico   — Visión global y decisiones clave",
}


def print_banner():
    console.print()
    console.print(Rule(style="dim"))
    title = Text(f"  {COMPANY} — Sistema Multi-Agente  ", style="bold white on dark_blue")
    console.print(title, justify="center")
    channels_line = Text("  " + " · ".join(CHANNELS) + "  ", style="dim")
    console.print(channels_line, justify="center")
    console.print(Rule(style="dim"))
    console.print()
    console.print("  Escribe tu consulta o [bold]/ayuda[/bold] para ver comandos.", style="dim")
    console.print()


def print_agent_response(agent_key: str, response: str):
    color, emoji, display_name = AGENT_STYLES.get(agent_key, ("white", "🤖", agent_key.title()))
    title = f"{emoji}  {display_name}"
    console.print(
        Panel(
            Markdown(response),
            title=title,
            title_align="left",
            border_style=color,
            padding=(1, 2),
        )
    )
    console.print()


def print_routing_indicator(agent_key: str):
    color, emoji, display_name = AGENT_STYLES.get(agent_key, ("white", "🤖", agent_key.title()))
    console.print(f"  [{color}]→ {emoji} {display_name}[/{color}]", style="dim")


def handle_command(cmd: str, orchestrator: Orchestrator) -> bool:
    """Returns True if the loop should continue, False to exit."""
    cmd = cmd.strip().lower()

    if cmd in ("/salir", "/exit", "/quit"):
        console.print("\n  Hasta luego. 👋\n", style="dim")
        return False

    if cmd == "/reset":
        orchestrator.reset_history()
        console.print("  [dim]Historial borrado.[/dim]\n")
        return True

    if cmd == "/agentes":
        console.print()
        for line in AGENTS_INFO.values():
            console.print(f"  {line}")
        console.print()
        return True

    if cmd in ("/ayuda", "/help"):
        console.print(Markdown(HELP_TEXT))
        return True

    console.print(f"  [dim]Comando desconocido: {cmd}. Escribe /ayuda para ver opciones.[/dim]\n")
    return True


def main():
    print_banner()
    orchestrator = Orchestrator()

    while True:
        try:
            query = console.input("[bold white]Tú:[/bold white] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n  Hasta luego. 👋\n", style="dim")
            break

        if not query:
            continue

        if query.startswith("/"):
            if not handle_command(query, orchestrator):
                break
            continue

        console.print()
        with console.status("[dim]Consultando...[/dim]", spinner="dots"):
            try:
                agent_key, response = orchestrator.chat(query)
            except Exception as e:
                console.print(f"  [red]Error:[/red] {e}\n")
                continue

        print_routing_indicator(agent_key)
        console.print()
        print_agent_response(agent_key, response)


if __name__ == "__main__":
    main()
