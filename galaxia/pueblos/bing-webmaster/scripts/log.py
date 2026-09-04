"""Logging unificado, legible, para scripts de CLI que llaman APIs externas."""

from __future__ import annotations

from rich.console import Console
from rich.markup import escape

console = Console()

# Los `msg` se escapan SIEMPRE: si vienen de output remoto (wp-cli, PHP, un shell
# ajeno), un mensaje con ruta entre corchetes ("[/var/www/...algo.php::66]") se
# parsea como tag de cierre de Rich -> MarkupError que tumba el script aunque el
# trabajo real haya ido bien. Markup real solo en el literal propio del código.


def step(msg: str) -> None:
    """Anuncia un paso del pipeline."""
    console.print(f"[bold cyan]→[/] {escape(msg)}")


def ok(msg: str) -> None:
    console.print(f"[bold green]✓[/] {escape(msg)}")


def fail(msg: str) -> None:
    console.print(f"[bold red]✗[/] {escape(msg)}")


def warn(msg: str) -> None:
    console.print(f"[bold yellow]![/] {escape(msg)}")


def info(msg: str) -> None:
    console.print(f"[dim]·[/] {escape(msg)}")


def api_call(method: str, url: str, body: dict | None = None) -> None:
    """Loguea una llamada API antes de ejecutarla."""
    console.print(f"[cyan]→ {method}[/] [dim]{escape(url)}[/]")
    if body:
        console.print(f"  [dim]body:[/] {escape(str(body))}")


def api_response(status: int, snippet: str = "") -> None:
    """Loguea respuesta API."""
    color = "green" if 200 <= status < 300 else "red"
    console.print(f"[{color}]✓ {status}[/] {escape(snippet)}")
