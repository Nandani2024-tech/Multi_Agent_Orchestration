import os
from litellm import completion
from typing import List, Dict, Any, Optional

class LLMEngine:
    def __init__(self):
        # Ollama runs locally, so no API key is needed.
        # We ensure the base_url is pointing to localhost.
        pass

    def call(self, system_prompt: str, user_prompt: str, model: str = "ollama/llama3.2") -> str:
        """
        Sends a request to the Local LLM (Ollama).
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # LiteLLM connects to http://localhost:11434 by default for 'ollama/...' models
            response = completion(
                model=model, 
                messages=messages, 
                api_base="http://localhost:11434"  # Explicitly pointing to local server
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Local LLM Error: {str(e)}"

# Singleton Instance
llm_client = LLMEngine()