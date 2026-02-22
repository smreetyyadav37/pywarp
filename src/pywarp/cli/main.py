import typer
import asyncio
from pathlib import Path
from rich.console import Console

from pywarp.core.engine import WarpEngine

# Initialize Typer app and Rich console for beautiful terminal output
app = typer.Typer(help="Warp Parse - High-performance Python ETL Engine")
console = Console()

@app.command()
def daemon(
    work_root: str = typer.Option(".", "--work-root", help="Root directory of the project"),
    config: str = typer.Option("conf/wparse.toml", "--config", "-c", help="Main config file"),
    workers: int = typer.Option(4, "--parse-workers", "-w", help="Number of CPU workers to use")
):
    """
    Run the ETL engine in continuous DAEMON mode.
    """
    console.print(f"[bold green]🚀 Starting PyWarp Daemon from {work_root}[/bold green]")
    console.print(f"[dim]Using config: {config} | Workers: {workers}[/dim]")
    
    # In a full run, we would load `WparseConfig` here and pass it to the engine.
    engine = WarpEngine(parse_workers=workers)
    
    try:
        asyncio.run(engine.run_daemon())
    except KeyboardInterrupt:
        console.print("\n[bold red]Engine stopped safely by user.[/bold red]")

@app.command()
def batch():
    """
    Run the engine in BATCH mode for historical log files.
    """
    console.print("[bold yellow]Batch mode execution starting... (Simulated)[/bold yellow]")

if __name__ == "__main__":
    app()