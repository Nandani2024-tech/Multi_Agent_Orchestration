import yaml
import os
import difflib
from typing import Dict, Any, List
from src.schema import OrchestrationConfig, AgentConfig, WorkflowConfig, WorkflowStep

class ConfigParser:
    """
    Responsible for reading YAML files and validating them against the schema.
    INCLUDES: Smart typo correction and synonym mapping.
    """

    @staticmethod
    def load_config(file_path: str) -> OrchestrationConfig:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found at: {file_path}")

        with open(file_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"CRITICAL: YAML Syntax Error. {e}")

        if not data:
            raise ValueError("YAML file is empty")

        # 1. Parse Agents
        if 'agents' not in data:
            raise ValueError("Config missing required section: 'agents'")
        
        agents = []
        # Handle case where agents might be a single dict instead of list
        raw_agents = data['agents'] if isinstance(data['agents'], list) else [data['agents']]
        
        for agent_data in raw_agents:
            agents.append(ConfigParser._parse_agent(agent_data))

        # 2. Parse Workflow
        if 'workflow' not in data:
            raise ValueError("Config missing required section: 'workflow'")
        
        workflow = ConfigParser._parse_workflow(data['workflow'])

        return OrchestrationConfig(
            agents=agents,
            workflow=workflow,
            models=data.get('models', {})
        )

    @staticmethod
    def _parse_agent(data: Dict[str, Any]) -> AgentConfig:
        # ID is mandatory
        if 'id' not in data:
            raise ValueError(f"Agent definition missing required field: 'id' in {data}")

        # --- SYNONYM MAPPING ---
        # 1. Role: accept 'role', 'description', 'job', 'position'
        role = (data.get('role') or 
                data.get('description') or 
                data.get('job') or 
                data.get('position') or 
                "Assistant")
        
        # 2. Goal: accept 'goal', 'objective', 'task'
        goal = (data.get('goal') or 
                data.get('objective') or 
                data.get('task'))
        
        # 3. Instructions: accept 'instruction', 'instructions', 'system_prompt'
        instructions = (data.get('instructions') or 
                        data.get('instruction') or 
                        data.get('system_prompt'))

        # If goal is missing but instructions exist, use instructions as goal
        if not goal:
            if instructions:
                goal = "Follow the provided instructions."
            else:
                goal = "Complete the assigned task."

        # 4. Tools: accept 'tools', 'toolsets', 'tool_list'
        tools = (data.get('tools') or 
                 data.get('toolsets') or 
                 data.get('tool_list') or 
                 [])
        
        # Normalize tools to list if string
        if isinstance(tools, str):
            tools = [tools]

        return AgentConfig(
            id=data['id'],
            role=role,
            goal=goal,
            model=data.get('model', 'gpt-4-turbo'),
            tools=tools,
            instructions=instructions,
            sub_agents=data.get('sub_agents', [])
        )

    @staticmethod
    def _parse_workflow(data: Dict[str, Any]) -> WorkflowConfig:
        raw_type = data.get('type', 'sequential')
        
        # --- SPELLING CORRECTION ---
        valid_types = ['sequential', 'parallel']
        # 1. Exact match
        if raw_type.lower() in valid_types:
            w_type = raw_type.lower()
        else:
            # 2. Fuzzy match (e.g. "sequntial" -> "sequential")
            matches = difflib.get_close_matches(raw_type.lower(), valid_types, n=1, cutoff=0.6)
            if matches:
                print(f"[Notice] Auto-corrected workflow type '{raw_type}' to '{matches[0]}'")
                w_type = matches[0]
            else:
                raise ValueError(f"Unknown workflow type: '{raw_type}'. Expected: {valid_types}")

        steps = []
        branches = []
        then_step = None

        if w_type == 'sequential':
            # Handle 'steps', 'sequence', 'flow'
            raw_steps = (data.get('steps') or 
                         data.get('sequence') or 
                         data.get('flow') or 
                         [])
            
            for s in raw_steps:
                if isinstance(s, dict) and 'agent' in s:
                    steps.append(WorkflowStep(agent=s['agent']))
                elif isinstance(s, str):
                    steps.append(WorkflowStep(agent=s))

        elif w_type == 'parallel':
            # Handle 'branches', 'parallel_tasks'
            branches = (data.get('branches') or 
                        data.get('parallel_tasks') or 
                        [])
            
            raw_then = data.get('then') or data.get('aggregator')
            if raw_then:
                if isinstance(raw_then, dict) and 'agent' in raw_then:
                    then_step = WorkflowStep(agent=raw_then['agent'])
                elif isinstance(raw_then, str):
                    then_step = WorkflowStep(agent=raw_then)
        
        return WorkflowConfig(type=w_type, steps=steps, branches=branches, then=then_step)