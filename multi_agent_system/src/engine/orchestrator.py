import concurrent.futures
from typing import List, Dict, Any
from src.schema import OrchestrationConfig, WorkflowConfig
from src.engine.agent_runner import AgentRunner
from src.interface.console import ui

class Orchestrator:
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.agents_map = {a.id: a for a in config.agents}

    def run(self):
        """
        Main entry point. Decides which workflow strategy to use.
        """
        workflow_type = self.config.workflow.type
        ui.log_workflow_start("Main Workflow", workflow_type)

        final_result = ""

        if workflow_type == "sequential":
            final_result = self._run_sequential()
        elif workflow_type == "parallel":
            final_result = self._run_parallel()
        else:
            ui.print_error(f"Unknown workflow type: {workflow_type}")

        return final_result

    def _run_sequential(self) -> str:
        """
        Runs agents one by one. The output of the previous agent 
        becomes the CONTEXT for the next agent.
        """
        context = "Start of workflow."
        
        for step in self.config.workflow.steps:
            agent_id = step.agent
            if agent_id not in self.agents_map:
                ui.print_error(f"Agent '{agent_id}' not found in configuration.")
                continue

            # Run the agent
            agent = self.agents_map[agent_id]
            
            # The 'task_input' is the context from the previous agent
            output = AgentRunner.run(agent, context=context, task_input=context)
            
            # Update context for the next agent
            context = output
            
        return context

    def _run_parallel(self) -> str:
        """
        Runs multiple agents at the same time (conceptually).
        Useful for brainstorming or voting.
        """
        branches = self.config.workflow.branches
        results = []

        print("\n⚡ Starting Parallel Execution...")
        
        # We use a ThreadPool to run them truly in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_agent = {}
            
            for branch_agent_id in branches:
                if branch_agent_id in self.agents_map:
                    agent = self.agents_map[branch_agent_id]
                    # Submit the job
                    future = executor.submit(
                        AgentRunner.run, 
                        agent=agent, 
                        context="Parallel Task", 
                        task_input="Execute your specific goal independently."
                    )
                    future_to_agent[future] = branch_agent_id
            
            # Collect results as they finish
            for future in concurrent.futures.as_completed(future_to_agent):
                agent_id = future_to_agent[future]
                try:
                    res = future.result()
                    results.append(f"Agent {agent_id} said: {res}")
                except Exception as e:
                    results.append(f"Agent {agent_id} failed: {e}")

        # Aggregation Step (if a 'then' step exists)
        aggregated_context = "\n".join(results)
        
        if self.config.workflow.then:
            final_agent_id = self.config.workflow.then.agent
            ui.console.print(f"\n[bold magenta]🔄 Aggregating results with {final_agent_id}...[/bold magenta]")
            
            final_agent = self.agents_map[final_agent_id]
            return AgentRunner.run(
                final_agent, 
                context=aggregated_context, 
                task_input="Summarize these parallel results."
            )
            
        return aggregated_context