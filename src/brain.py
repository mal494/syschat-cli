import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables (look for .env file)
load_dotenv()

def ask_llm(system_context, user_question):
    """
    Sends the system context and user question to the LLM.
    Auto-switches between OpenAI (Cloud) and Ollama (Local).
    """
    
    api_key = os.getenv("LLM_API_KEY")
    # Default to llama3 for local, or whatever model you have pulled in Ollama
    model = os.getenv("LLM_MODEL", "darkidol") 

    try:
        if not api_key:
            # --- LOCAL MODE (Ollama) ---
            # Ensure Ollama is running (`ollama serve` in another terminal)
            url = "http://localhost:11434/api/chat"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": user_question}
                ],
                "stream": False
            }
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=payload, headers=headers, verify=False)
            response.raise_for_status()
            data = response.json()
            
            # Ollama returns 'message' -> 'content'
            return data.get("message", {}).get("content", "Error: No content returned.")

        else:
            # --- CLOUD MODE (OpenAI Compatible) ---
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-4o-mini",  # Cost-effective model
                "messages": [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": user_question}
                ]
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            response = requests.post(url, json=payload, headers=headers, verify=False)
            response.raise_for_status()
            data = response.json()
            
            # OpenAI returns 'choices' -> list
            return data["choices"][0]["message"]["content"]

    except requests.exceptions.ConnectionError:
        return "Connection Error: Is Ollama running? (Try running 'ollama serve')"
    except Exception as e:
        return f"API Error: {str(e)}"