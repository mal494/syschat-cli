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
    Scans the text for a JSON object OR a JSON list.
    Returns: (is_json, data)
    """
    import re
    
    # 1. Try to find a JSON List [ ... ]
    match_list = re.search(r'\[.*\]', response_text, re.DOTALL)
    if match_list:
        try:
            return True, json.loads(match_list.group(0))
        except:
            pass

    # 2. Try to find a JSON Object { ... }
    match_obj = re.search(r'\{.*?\}', response_text, re.DOTALL)
    if match_obj:
        try:
            return True, json.loads(match_obj.group(0))
        except:
            pass
            
    return False, response_text


def ask_agent(user_question, screen_context):
    """
    A specialized brain function for Desktop Automation.
    Forces the AI to return JSON commands.
    """
    model = os.getenv("LLM_MODEL", "llama3") 
    
    # 1. Define the Tools (The API for the AI)
    tools_def = """
    AVAILABLE TOOLS:
    1. {"tool": "move_mouse", "args": [x, y]} -> Moves cursor to coordinates.
    2. {"tool": "click", "args": []} -> Clicks current position.
    3. {"tool": "type", "args": ["text"]} -> Types text.
    4. {"tool": "screenshot", "args": ["filename.png"]} -> Saves screen to file.
    5. {"tool": "response", "args": ["text"]} -> Just talk to the user.
    """

    # 2. The Strict System Prompt
    system_prompt = f"""
    ROLE: You are an AI Desktop Agent. You control the user's mouse and keyboard.
    
    CURRENT STATE:
    {screen_context}
    
    {tools_def}
    
    INSTRUCTIONS:
    - You MUST reply with valid JSON only.
    - Do not write explanations outside the JSON.
    - Example: {{"tool": "move_mouse", "args": [500, 500]}}
    """
    
    # Re-use the ask_llm logic but with our agent prompt
    # Note: We just call the existing logic to handle the API connection
    # (We are assuming the ask_llm function uses the /api/chat endpoint we set up earlier)
    
    # For local Ollama, we construct the message manually to ensure formatting
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        "stream": False,
        "format": "json",  # <--- CRITICAL: Forces Ollama to output valid JSON
        "temperature": 0.0
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except Exception as e:
        return json.dumps({"tool": "response", "args": [f"Error: {str(e)}"]})