import sys
import os
from rich.panel import Panel  # <--- NEW IMPORT
from src.interface.parser import ConfigParser
from src.engine.orchestrator import Orchestrator
from src.interface.console import ui

def main():
    # 1. Welcome Banner
    ui.print_welcome()

    # 2. Determine path
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = "config.yaml"

    # Smart path checking
    possible_paths = [
        input_path,
        os.path.join("examples", input_path),
        os.path.join("example", input_path)
    ]

    final_config_path = None
    for path in possible_paths:
        if os.path.exists(path):
            final_config_path = path
            break

    if not final_config_path:
        ui.print_error(f"Could not find configuration file: '{input_path}'")
        return

    # 3. Parse Config
    try:
        ui.console.print(f"[dim]Loading configuration from: {final_config_path}...[/dim]")
        config = ConfigParser.load_config(final_config_path)
        ui.console.print("[bold green]✅ Configuration Loaded![/bold green]")
    except Exception as e:
        ui.print_error(f"Configuration Error: {e}")
        return

    # 4. Run Workflow
    try:
        orchestrator = Orchestrator(config)
        final_result = orchestrator.run()
        
        ui.console.print("\n[bold green]🎉 Workflow Completed Successfully![/bold green]")
        # FIX: Correct way to print a Panel in Rich
        ui.console.print(Panel(final_result, title="Final Output", border_style="green"))
        
    except Exception as e:
        ui.print_error(f"Runtime Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()