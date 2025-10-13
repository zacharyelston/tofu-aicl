"""Rich output utilities - separated for reuse"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax


console = Console()


def print_success(message: str):
    """Print success message - one function, one job"""
    console.print(f"✅ [green]{message}[/green]")


def print_error(message: str):
    """Print error message"""
    console.print(f"❌ [red]{message}[/red]")


def print_info(message: str):
    """Print info message"""
    console.print(f"ℹ️  [blue]{message}[/blue]")


def create_resource_table(resources: dict) -> Table:
    """Create resource table - reusable component"""
    table = Table(title="📊 Resources", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Provider", style="yellow")
    table.add_column("Status", style="blue")
    
    for res_id, resource in resources.items():
        status_icon = "✅" if resource.status == "ready" else "⏳"
        table.add_row(
            res_id,
            resource.type,
            resource.provider,
            f"{status_icon} {resource.status}"
        )
    
    return table


def show_syntax(code: str, language: str = "json", title: str = None):
    """Display syntax-highlighted code"""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    
    if title:
        console.print(Panel(syntax, title=title, border_style="green"))
    else:
        console.print(syntax)
