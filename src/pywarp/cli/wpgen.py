import typer
import os
import time
import random
from pathlib import Path
from rich.console import Console

app = typer.Typer(help="Warp Data Generator - Stress Test Your Pipeline")
console = Console()

@app.command()
def generate(
    output: str = typer.Option("data/in_dat/gen.dat", "--output", "-o", help="File to write to"),
    eps: int = typer.Option(100, "--eps", "-e", help="Events Per Second to generate"),
    duration: int = typer.Option(5, "--duration", "-d", help="How many seconds to run")
):
    """Blasts the source file with mock logs at a specific rate."""
    console.print(f"[bold green]🚀 Starting wpgen: {eps} EPS for {duration} seconds...[/bold green]")
    
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # We include 8.8.8.8 here. 
    # To simulate real-world traffic, we can use random.choices with weights 
    # so 'Engineering' and 'Internal' IPs appear more often than 'Malicious' ones.
    ips = ["222.133.52.20", "192.168.1.100", "10.0.0.5", "8.8.8.8"]
    weights = [0.1, 0.4, 0.4, 0.1] # 10% malicious, 40% engineering, 40% HR, 10% Google DNS
    
    methods = ["GET /nginx HTTP/1.1", "POST /login HTTP/1.1", "GET /api/data HTTP/2.0"]
    
    total_logs = 0
    with open(out_path, "a", encoding="utf-8") as f:
        for _ in range(duration):
            start = time.time()
            for _ in range(eps):
                # Using random.choices (plural) with weights for better use-case testing
                ip = random.choices(ips, weights=weights, k=1)[0]
                method = random.choice(methods)
                
                # Generate a log that perfectly matches our WPL Regex
                log = f'{ip} - - [06/Aug/2019:12:12:19 +0800] "{method}"' + os.linesep
                f.write(log)
                total_logs += 1
            
            # Throttle the loop to exactly 1 second
            elapsed = time.time() - start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
                
    console.print(f"✅ Generated {total_logs} logs inside {output}")

if __name__ == "__main__":
    app()
    