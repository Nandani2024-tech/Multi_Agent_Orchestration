from src.engine.llm import llm_client

print("🧠 Connecting to Local Brain (Ollama Llama 3.2)...")

response = llm_client.call(
    system_prompt="You are a helpful AI assistant.",
    user_prompt="Explain what a Multi-Agent System is in one sentence.",
    model="ollama/llama3.2"  # <--- The model you pulled earlier
)

print(f"\n🤖 Response:\n{response}")