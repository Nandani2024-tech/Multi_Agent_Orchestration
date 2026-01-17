import time
from src.interface.parser import ConfigParser
from src.interface.console import ui
from src.interface.tools import ToolRegistry

# 1. CREATE A DUMMY YAML FILE
yaml_content = """
agents:
  - id: researcher
    role: Analyst
    goal: Analyze data
    tools: [python]
workflow:
  type: sequential
  steps:
    - agent: researcher
"""

with open("test_config.yaml", "w") as f:
    f.write(yaml_content)

def run_mock_engine():
    # --- STEP 1: PARSING (Testing parser.py) ---
    ui.print_welcome()
    
    try:
        config = ConfigParser.load_config("test_config.yaml")
        ui.console.print("[bold green]✅ YAML Parsed Successfully![/bold green]")
    except Exception as e:
        ui.print_error(f"Parser Failed: {e}")
        return

    # --- STEP 2: SIMULATE WORKFLOW (Testing console.py) ---
    ui.log_workflow_start("Test Workflow", config.workflow.type)
    
    for step in config.workflow.steps:
        agent_id = step.agent
        
        # Find the agent config
        agent = next(a for a in config.agents if a.id == agent_id)
        
        ui.log_agent_start(agent.id, agent.role)
        
        # Simulate "Thinking"
        with ui.status_spinner(f"{agent.id} is thinking..."):
            time.sleep(1.5)
            
            # --- STEP 3: SIMULATE TOOL USAGE (Testing tools.py) ---
            # Pretend the AI asked to run python code
            if "python" in agent.tools:
                code = "print('Hello from the Tool Registry!')"
                ui.log_tool_use("python", code)
                
                # ACTUALLY execute the tool
                result = ToolRegistry.execute("python", code=code)
                time.sleep(0.5)
                ui.log_tool_result(result)

        # Simulate Final Output
        ui.stream_output(agent.id, f"I have finished my analysis using the **{agent.tools[0]}** tool.")
        ui.log_agent_completion(agent.id, 2.0)

    # Cleanup
    import os
    os.remove("test_config.yaml")
    ui.console.print("[bold green]🎉 PERSON 2 WORK IS COMPLETE![/bold green]")

if __name__ == "__main__":
    run_mock_engine()