from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.theme import Theme
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live
from typing import Optional
from src.interface.database import db

# Custom theme for consistent coloring
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "agent": "bold blue",
    "workflow": "magenta"
})

class ConsoleUI:
    """
    Handles all terminal output using the Rich library.
    Provides methods for logging workflow progress, agent actions, and results.
    """
    
    def __init__(self):
        self.console = Console(theme=custom_theme)
        self.current_spinner = None

    def print_welcome(self):
        """Prints the startup banner."""
        self.console.print()
        self.console.rule("[bold magenta]Multi-Agent Orchestrator[/bold magenta]")
        self.console.print("🚀 Engine Initialized. Reading Configuration...", justify="center")
        self.console.print()

    def log_workflow_start(self, name: str, mode: str):
        """Logs the start of a workflow sequence."""
        self.console.print(f"[workflow]► Starting Workflow:[/workflow] [bold]{name}[/bold] ({mode})")
        self.console.print()

    def log_agent_start(self, agent_id: str, role: str):
        """
        Logs that an agent is beginning its task.
        """
        self.console.print(f"[agent]● Agent Active:[/agent] [bold white]{agent_id}[/bold white] ({role})")
        
    def log_agent_completion(self, agent_id: str, duration: float = 0.0):
        """Logs that an agent has finished."""
        self.console.print(f"[success]✓ {agent_id} completed[/success] [dim]({duration:.2f}s)[/dim]")
        self.console.print()

    def stream_output(self, agent_id: str, content: str):
        """
        Renders AI output in a nice Markdown panel.
        """
        md = Markdown(content)
        panel = Panel(
            md,
            title=f"[bold blue]{agent_id}[/bold blue]",
            border_style="blue",
            expand=False
        )
        self.console.print(panel)
        self.console.print()

    def log_tool_use(self, tool_name: str, input_data: str):
        """Logs when an agent uses a tool."""
        self.console.print(f"  [warning]🛠  Using Tool:[/warning] {tool_name}")
        self.console.print(f"  [dim]Input: {input_data}[/dim]")
        db.log_event("system", "tool_use", f"Tool: {tool_name}, Input: {input_data}")

    def log_tool_result(self, result: str):
        """Logs the output of a tool."""
        # Truncate long results for display
        display_result = result[:200] + "..." if len(result) > 200 else result
        self.console.print(f"  [success]➔ Result:[/success] [dim]{display_result}[/dim]")
        self.console.print()

    def print_error(self, message: str):
        """Prints error messages prominently."""
        self.console.print(f"[error]ERROR:[/error] {message}")

    def status_spinner(self, message: str):
        """
        Returns a context manager for a loading spinner.
        Usage:
            with ui.status_spinner("Thinking..."):
                do_work()
        """
        return self.console.status(f"[bold cyan]{message}[/bold cyan]", spinner="dots")

# Create a singleton instance to be used throughout the app
ui = ConsoleUI()

# Simple test to run this file directly and see the colors
if __name__ == "__main__":
    import time
    
    ui.print_welcome()
    ui.log_workflow_start("Research Team", "Sequential")
    
    with ui.status_spinner("Initializing agents..."):
        time.sleep(1.5)
        
    ui.log_agent_start("researcher", "Analyst")
    with ui.status_spinner("Researcher is thinking..."):
        time.sleep(1)
        ui.log_tool_use("google_search", "Electric Vehicle Sales 2024")
        time.sleep(0.5)
        ui.log_tool_result("Found 14,000 results...")
    
    ui.stream_output("researcher", "# Analysis Report\n* EV sales are up **40%**.\n* key player is Tesla.")
    ui.log_agent_completion("researcher", 2.5)