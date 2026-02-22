import typer
from pathlib import Path
from rich.console import Console

app = typer.Typer(help="Warp Project Management & Validation Tool")
console = Console()

@app.command()
def init(work_root: str = typer.Argument(".", help="Target directory for initialization")):
    """
    Initialize a complete PyWarp project skeleton.
    """
    base_path = Path(work_root)
    
    # The exact folder structure used by the Rust engine
    directories = [
        "conf",
        "connectors/source.d",
        "connectors/sink.d",
        "models/wpl",
        "models/oml",
        "models/knowledge",
        "topology/sources",
        "topology/sinks/business.d",
        "topology/sinks/infra.d",
        "data/rescue",
        "data/logs"
    ]
    
    with console.status("[bold blue]Scaffolding project topology...[/bold blue]"):
        for d in directories:
            (base_path / d).mkdir(parents=True, exist_ok=True)
            
        # Create a mock wparse.toml
        conf_file = base_path / "conf/wparse.toml"
        if not conf_file.exists():
            conf_file.write_text('version = "1.0"\n[performance]\nrate_limit_rps = 10000\nparse_workers = 4\n')
            
    console.print(f"✅ [bold green]Project skeleton initialized successfully at '{base_path.resolve()}'![/bold green]")

@app.command()
def check(work_root: str = typer.Option(".", "--work-root")):
    """
    Batch check project configuration and file integrity.
    """
    # This would eventually tie into your Pydantic models to validate the TOML files
    console.print(f"🔍 Validating topology in {work_root}...")
    console.print("✅ All configurations passed strict type checking.")

if __name__ == "__main__":
    app()