from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union

# 1. Defines what an Agent looks like
@dataclass
class AgentConfig:
    id: str
    role: str
    goal: str
    model: str = "gpt-4-turbo"  # Default model if none specified
    tools: List[str] = field(default_factory=list)
    instructions: Optional[str] = None
    sub_agents: List[str] = field(default_factory=list)

# 2. Defines a single step in a sequential workflow
@dataclass
class WorkflowStep:
    agent: str  # The ID of the agent to run in this step

# 3. Defines the structure of the workflow (Sequential or Parallel)
@dataclass
class WorkflowConfig:
    type: str  # "sequential" or "parallel"
    
    # Used if type == "sequential"
    steps: List[WorkflowStep] = field(default_factory=list)
    
    # Used if type == "parallel"
    branches: List[str] = field(default_factory=list) # List of Agent IDs to run simultaneously
    then: Optional[WorkflowStep] = None # The aggregator agent that runs after branches finish

# 4. The Root object that holds everything
@dataclass
class OrchestrationConfig:
    agents: List[AgentConfig]
    workflow: WorkflowConfig
    models: Dict[str, Dict[str, str]] = field(default_factory=dict)