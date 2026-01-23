import json
import time
import base64
import os
from datetime import datetime
from pathlib import Path

from brain import ask_llm
from desktop import capture_screen, execute_action
from config import MAX_STEPS, TIMEOUT_SECONDS
from prompts import AGENT_SYSTEM_PROMPT

def save_debug_artifact(step, image_b64, action_json):
    """Saves the screenshot and action log for debugging."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Save Image
    try:
        img_data = base64.b64decode(image_b64)
        with open(log_dir / f"debug_step_{step}_{timestamp}.png", "wb") as f:
            f.write(img_data)
    except Exception as e:
        print(f"Failed to save debug image: {e}")

    # Log Action
    with open(log_dir / "agent_history.json", "a") as f:
        log_entry = {
            "timestamp": timestamp,
            "step": step,
            "action": action_json
        }
        f.write(json.dumps(log_entry) + "\n")

def clean_json_response(response_text):
    """
    Cleans LLM response to extract valid JSON.
    Handles markdown blocks (```json ... ```).
    """
    cleaned = response_text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0]
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0]
    return cleaned.strip()

def run_agent_loop(user_goal):
    """
    The main OODA loop for the desktop agent.
    """
    print(f"--- Agent Started ---\nGoal: {user_goal}")
    print(f"Press Ctrl+C to abort or move mouse to corner (Fail-Safe).")
    
    history = [] # List of previous actions/summaries
    
    for step in range(1, MAX_STEPS + 1):
        print(f"\n[Step {step}/{MAX_STEPS}] Observing...")
        
        # 1. Observe
        try:
            screen_b64 = capture_screen()
        except Exception as e:
            print(f"Error capturing screen: {e}")
            break

        # 2. Orient & Decide
        print("Thinking...")
        
        # Construct Context with Sliding Window (Last 5 steps)
        recent_history = history[-5:]
        history_text = "\n".join([f"Step {i+1}: {act}" for i, act in enumerate(recent_history)])
        if len(history) > 5:
            history_text = f"... (Previous steps omitted) ...\n{history_text}"
            
        current_prompt = f"USER GOAL: {user_goal}\n\nHISTORY:\n{history_text}\n\nWhat is the next action?"
        
        response_text = ask_llm(AGENT_SYSTEM_PROMPT, current_prompt, image_data=screen_b64)
        
        # 3. Parse Action
        try:
            cleaned_json = clean_json_response(response_text)
            action_plan = json.loads(cleaned_json)
        except json.JSONDecodeError:
            print(f"Error parsing LLM response: {response_text}")
            # Retry logic or fail
            # For robustness, we could treat this as a failure or ask LLM to fix json.
            # Here we just skip to next iteration to try again
            continue
            
        print(f"Plan: {action_plan.get('action')} - {action_plan.get('reason')}")
        
        # Save Debug Artifacts
        save_debug_artifact(step, screen_b64, action_plan)
        
        # 4. Act
        if action_plan.get("action") == "DONE":
            print("Goal Achieved!")
            break
            
        if action_plan.get("action") == "FAIL":
            print(f"Agent Failed: {action_plan.get('reason')}")
            break
            
        success = execute_action(action_plan)
        
        if success:
            history.append(f"Executed {action_plan['action']}: {action_plan.get('reason')}")
        else:
            print("Action failed execution.")
            history.append(f"Failed to execute {action_plan['action']}")
            
        # Wait a bit before next observation to let UI settle
        time.sleep(2)

    print("--- Agent Stopped ---")