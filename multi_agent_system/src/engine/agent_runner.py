import json
import re
from src.schema import AgentConfig
from src.engine.llm import llm_client
from src.interface.tools import ToolRegistry
from src.interface.console import ui
from src.interface.database import db

class AgentRunner:
    @staticmethod
    def run(agent: AgentConfig, context: str, task_input: str) -> str:
        """
        Executes a single agent's task.
        It allows the agent to use ONE tool step before giving a final answer.
        """
        
        # 1. SETUP: Build the System Prompt
        # We explicitly tell Llama 3.2 how to format tool calls
        tool_names = list(ToolRegistry.list_tools())
        
        system_prompt = (
            f"You are {agent.role}. Your goal: {agent.goal}.\n"
            f"Instructions: {agent.instructions}\n"
            f"Available Tools: {json.dumps(tool_names)}\n"
            "CRITICAL RULES:\n"
            "1. If you need to use a tool, output ONLY a JSON object like this:\n"
            '   {"tool": "tool_name", "args": {"arg_name": "value"}}\n'
            "2. If you do NOT need a tool, just answer normally.\n"
            "3. Do not add markdown like ```json```."
        )
        
        user_msg = f"Context: {context}\nCurrent Task: {task_input}"

        # 2. THINKING: Call the Brain
        ui.log_agent_start(agent.id, agent.role)
        
        # We default to 'ollama/llama3.2' if the YAML model isn't set/valid
        model_to_use = "ollama/llama3.2" 
        
        response = llm_client.call(system_prompt, user_msg, model=model_to_use)

        # 3. DETECT TOOL USAGE
        # We look for a JSON pattern in the response
        tool_call = AgentRunner._extract_json(response)

        if tool_call:
            # The agent wants to use a tool!
            t_name = tool_call.get("tool")
            t_args = tool_call.get("args", {})
            
            ui.log_tool_use(t_name, str(t_args))
            
            # Execute the tool
            try:
                tool_result = ToolRegistry.execute(t_name, **t_args)
            except Exception as e:
                tool_result = f"Tool Error: {e}"
                
            ui.log_tool_result(str(tool_result))
            
            # 4. FINAL SYNTHESIS: Feed the tool result back to the brain
            final_prompt = (
                f"Original Task: {task_input}\n"
                f"Tool Output: {tool_result}\n"
                "Based on this output, give a final concise answer."
            )
            final_response = llm_client.call(system_prompt, final_prompt, model=model_to_use)
            
            ui.stream_output(agent.id, final_response)
            return final_response
            
        else:
            # No tool used, just return the answer
            ui.stream_output(agent.id, response)
            return response

    @staticmethod
    def _extract_json(text: str):
        """
        Helper to find JSON inside a potentially messy LLM response.
        """
        try:
            # Attempt 1: Direct parse
            return json.loads(text)
        except:
            pass
        
        try:
            # Attempt 2: Find the first { and last }
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
            
        return None