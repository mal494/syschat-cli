import os
import re
import time
import json
import requests
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

REQUEST_TIMEOUT = 30  # seconds


def retry_api_call(max_retries=3, delay=1.0):
    """Decorator factory that retries a function on exception."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        return f"API Error after {max_retries} retries: {str(e)}"
                    time.sleep(delay)
        return wrapper
    return decorator


def ask_llm(system_context, user_question, image_data=None):
    """
    Sends a prompt to the configured LLM (cloud or local).
    Optionally accepts a base64-encoded image for multimodal models.
    """
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL", "llama3")

    # --- CLOUD MODE (OpenAI) ---
    if api_key:
        url = "https://api.openai.com/v1/chat/completions"

        # Build user message — multimodal if image provided
        if image_data:
            user_msg = {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_question},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                ]
            }
        else:
            user_msg = {"role": "user", "content": user_question}

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_context},
                user_msg
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Cloud Error: {str(e)}"

    # --- LOCAL MODE (Ollama Chat) ---
    else:
        url = "http://localhost:11434/api/chat"

        # Build user message — attach images list if image provided
        if image_data:
            user_msg = {"role": "user", "content": user_question, "images": [image_data]}
        else:
            user_msg = {"role": "user", "content": user_question}

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_context},
                user_msg
            ],
            "stream": False,
            "temperature": 0.0
        }

        try:
            response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json()
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
    # 1. Try to find a JSON List [ ... ]
    match_list = re.search(r'\[.*\]', response_text, re.DOTALL)
    if match_list:
        try:
            return True, json.loads(match_list.group(0))
        except (json.JSONDecodeError, ValueError):
            pass

    # 2. Try to find a JSON Object { ... }
    match_obj = re.search(r'\{.*?\}', response_text, re.DOTALL)
    if match_obj:
        try:
            return True, json.loads(match_obj.group(0))
        except (json.JSONDecodeError, ValueError):
            pass

    return False, response_text


def ask_agent(user_question, screen_context):
    """
    Specialized brain function for Desktop Automation.
    Forces the AI to return JSON commands via Ollama's format enforcement.
    """
    model = os.getenv("LLM_MODEL", "llama3")

    tools_def = """
    AVAILABLE TOOLS:
    1. {"tool": "move_mouse", "args": [x, y]} -> Moves cursor to coordinates.
    2. {"tool": "click", "args": []} -> Clicks current position.
    3. {"tool": "type", "args": ["text"]} -> Types text.
    4. {"tool": "screenshot", "args": ["filename.png"]} -> Saves screen to file.
    5. {"tool": "response", "args": ["text"]} -> Just talk to the user.
    """

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

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        "stream": False,
        "format": "json",
        "temperature": 0.0
    }

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except Exception as e:
        return json.dumps({"tool": "response", "args": [f"Error: {str(e)}"]})
