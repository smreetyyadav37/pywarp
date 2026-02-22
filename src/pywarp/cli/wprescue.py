import typer
import json
from pathlib import Path
from rich.console import Console

app = typer.Typer(help="Warp Rescue - Dead Letter Queue Management")
console = Console()

@app.command()
def retry(
    dlq_file: str = typer.Option("data/out_dat/dynamic_demo.json", "--file", "-f", help="The sink file containing errors"),
    target: str = typer.Option("data/in_dat/gen.dat", "--target", "-t", help="The source file to requeue to")
):
    """Scans for logs tagged with '_error' and requeues them."""
    console.print(f"[bold red]🚑 Inspecting Dead Letter Queue: {dlq_file}[/bold red]")
    
    path = Path(dlq_file)
    if not path.exists():
        console.print("✅ Target file does not exist. No errors to rescue!")
        return
        
    rescued_count = 0
    valid_lines = []
    
    # 1. Read the file and separate errors from good data
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if "_error" in data and "raw_payload" in data:
                    # It's an error! Send the raw payload to the rescue queue
                    with open(target, "a", encoding="utf-8") as target_f:
                        target_f.write(data["raw_payload"].strip() + "\n")
                    rescued_count += 1
                else:
                    valid_lines.append(line)
            except json.JSONDecodeError:
                pass
                
    # 2. Rewrite the original file without the errors
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(valid_lines)
        
    console.print(f"✅ Rescued {rescued_count} failed logs and queued them back to {target}")

if __name__ == "__main__":
    app()