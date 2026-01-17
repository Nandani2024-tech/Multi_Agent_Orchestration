from src.schema import AgentConfig
from src.engine.agent_runner import AgentRunner

def test_single_agent():
    print("🕵️ --- TESTING AGENT RUNNER ---")
    
    # 1. Define a fake agent
    # We give it a goal that REQUIRES using the 'save_memory' tool
    agent = AgentConfig(
        id="memory_agent",
        role="Archivist",
        goal="Save important data to the database.",
        instructions="Save the user's favorite color as 'Blue' to the memory.",
        tools=["save_memory"], # Access to the tool
        model="ollama/llama3.2"
    )

    # 2. Run the agent
    print("🚀 Running Agent...")
    result = AgentRunner.run(
        agent=agent,
        context="No prior context",
        task_input="Please remember that the user's favorite color is Blue."
    )

    print("\n✅ Final Result from Agent:")
    print(result)

if __name__ == "__main__":
    test_single_agent()