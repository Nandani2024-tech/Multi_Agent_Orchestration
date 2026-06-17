import os
from litellm import completion
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

class LLMEngine:
    def __init__(self):
        pass

    def call(self, system_prompt: str, user_prompt: str, model: Optional[str] = None) -> str:
        """
        Sends a request to an LLM provider via LiteLLM.
        The model is determined by the provider prefix (e.g., 'groq/', 'openai/', 'ollama/').
        """
        # Fallback to environment variable or hardcoded default
        target_model = model or os.getenv("DEFAULT_MODEL", "groq/llama-3.3-70b-versatile")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # LiteLLM automatically handles API keys and base URLs from environment variables
            # based on the model prefix (e.g., GROQ_API_KEY for groq/...)
            response = completion(
                model=target_model, 
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ LLM Error ({target_model}): {str(e)}"

# Singleton Instance
llm_client = LLMEngine()