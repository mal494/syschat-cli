import os
import requests
import json
import time
from functools import wraps
from dotenv import load_dotenv

# Load environment variables (look for .env file)
load_dotenv()

def retry_api_call(max_retries=3, delay=2, backoff=2):
    """
    Decorator to retry API calls with exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        # Final attempt failed, return error message
                        return f"API Error (after {max_retries} retries): {str(e)}"
                    print(f"API call failed: {str(e)}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None # Should not be reached
        return wrapper
    return decorator

@retry_api_call()
def ask_llm(system_context, user_question, image_data=None):
    """
    Sends the system context and user question (plus optional image) to the LLM.
    Auto-switches between OpenAI (Cloud) and Ollama (Local).
    
    Args:
        system_context (str): The system prompt/persona.
        user_question (str): The user's query or command.
        image_data (str, optional): Base64 encoded image string.
    """
    
    api_key = os.getenv("LLM_API_KEY")
    # Default to llama3 for local, or whatever model you have pulled in Ollama
    model = os.getenv("LLM_MODEL", "darkidol") 

    if api_key:
        # --- CLOUD MODE (OpenAI Compatible) ---
        url = "https://api.openai.com/v1/chat/completions"
        
        # Construct content payload
        user_content = [{"type": "text", "text": user_question}]
        if image_data:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                }
            })

        payload = {
            "model": "gpt-4o-mini", # Can be overridden if needed
            "messages": [
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": 1000 # Limit output for safety
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    else:
        # --- LOCAL MODE (Ollama) ---
        # Ensure Ollama is running (`ollama serve` in another terminal)
        url = "http://localhost:11434/api/chat"
        
        messages = [
            {"role": "system", "content": system_context},
            {"role": "user", "content": user_question}
        ]
        
        # Ollama handles images by adding them to the message object
        if image_data:
            messages[1]["images"] = [image_data]

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.1 # Keep it factual/precise
            }
        }
        
        # Use verify=False if local cert issues arise, though http usually fine
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        return data.get("message", {}).get("content", "Error: No content returned.")
