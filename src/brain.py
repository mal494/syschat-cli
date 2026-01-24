import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def ask_llm(system_context, user_question):
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL", "llama3") 

    # --- CLOUD MODE (OpenAI) ---
    if api_key:
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_question}
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Cloud Error: {str(e)}"

    # --- LOCAL MODE (Ollama Chat) ---
    else:
        # We use /api/chat now because your Modelfile handles the formatting
        url = "http://localhost:11434/api/chat"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_question}
            ],
            "stream": False,
            # Temperature 0 makes it boring but obedient (Good for code analysis)
            "temperature": 0.0 
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            # Safety check: did the model return a message?
            if "message" in data:
                return data["message"]["content"]
            else:
                return f"Error: Unexpected response format from Ollama: {data}"
                
        except Exception as e:
            return f"Local Error: {str(e)}"

def extract_json(response_text):
    """
    Scans the text for a JSON object.
    Returns: (is_json_boolean, dictionary_data_or_original_text)
    """
    import re
    
    # Attempt 1: Look for standard Markdown JSON blocks ```json ... ```
    match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if match:
        try:
            return True, json.loads(match.group(1))
        except:
            pass

    # Attempt 2: Look for the first outer bracket pair { ... }
    # This regex looks for a curly brace, followed by anything (non-greedy), ending with a curly brace
    match = re.search(r'\{.*?\}', response_text, re.DOTALL)
    if match:
        try:
            return True, json.loads(match.group(0))
        except:
            pass
            
    # Attempt 3: Sometimes Llama3 returns just the JSON without markdown
    try:
        return True, json.loads(response_text)
    except:
        pass

    return False, response_text