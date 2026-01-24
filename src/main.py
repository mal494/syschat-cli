import sys
import os
import json
import time
from pathlib import Path

# Add src to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer import get_file_metadata, read_file_safe, scan_directory
from brain import ask_llm, extract_json
from desktop import DesktopController

def main():
    if len(sys.argv) < 2:
        print("\nUsage: python src/main.py <mode> [path]")
        print("Modes:")
        print("  auto       -> Control the mouse/keyboard")
        print("  dir <path> -> Audit a folder")
        print("  file <path> -> Analyze a file")
        return

    mode = sys.argv[1]
    system_context = ""
    
    # --- MODE 1: AUTOMATION 🤖 ---
    if mode == "auto":
        print("--- SysChat: Desktop Automation Mode ---")
        ctrl = DesktopController()
        screen_info = ctrl.get_screen_info()
        
        system_context = f"""
        ROLE: You are an AI Agent capable of controlling the user's desktop.
        SCREEN RESOLUTION: {screen_info['resolution']}
        
        AVAILABLE TOOLS (You must output strictly JSON to use these):
        1. {{"tool": "move", "x": 100, "y": 100}} -> Moves mouse to coordinates.
        2. {{"tool": "click"}} -> Left mouse click.
        3. {{"tool": "type", "text": "hello"}} -> Types text.
        4. {{"tool": "press", "key": "win"}} -> Presses a special key. 
           (Valid keys: win, enter, esc, tab, space, backspace, up, down, left, right)
        5. {{"tool": "screenshot", "name": "capture.png"}} -> Saves a screenshot.
        
        RULES:
        - If the user asks for an action, ONLY return the JSON object. Do not add conversational filler.
        - If the user asks a question, reply with normal text.
        """
        print(f"Agent Ready. Screen: {screen_info['resolution']}")
        print("⚠️  SAFETY: Slam mouse to any corner to abort script.")

    # --- MODE 2: DIRECTORY 📂 ---
    elif mode == "dir":
        if len(sys.argv) < 3:
            print("Error: Missing path. Usage: python src/main.py dir <path>")
            return
        path = sys.argv[2]
        print(f"Scanning {path}...")
        tree, content = scan_directory(path)
        system_context = f"""
        ROLE: Lead Developer.
        [PROJECT TREE]
        {tree}
        [CODE CONTENT]
        {content}
        INSTRUCTIONS: Analyze the architecture based on the files above.
        """
        print("Context Loaded.")

    # --- MODE 3: SINGLE FILE 📄 ---
    else:
        # Fallback to file mode. Takes the argument as the path.
        target_path = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
        
        print(f"Scanning {target_path}...")
        meta = get_file_metadata(target_path)
        if "error" in meta:
            print(meta['error'])
            return
        _, content = read_file_safe(target_path)
        system_context = f"ROLE: SysAdmin.\n[METADATA]\n{meta}\n[CONTENT]\n{content}"
        print("File Loaded.")

    # --- MAIN INTERACTION LOOP ---
    print("--------------------------------------------------")
    print("Type 'exit' to quit.")

    # Initialize controller for tool execution
    desktop = DesktopController()

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # 1. Get AI Response
            print("Thinking...", end="\r")
            raw_response = ask_llm(system_context, user_input)
            print(" " * 20, end="\r") # Clear the 'Thinking...' line

            # 2. Check for Tools (JSON Extraction)
            is_cmd, cmd_data = extract_json(raw_response)
            
            if is_cmd and mode == "auto" and isinstance(cmd_data, dict):
                tool = cmd_data.get("tool")
                print(f"⚡ EXECUTING: {str(tool).upper()}...")
                
                result = "Unknown tool"
                
                # EXECUTION LOGIC
                if tool == "move":
                    result = desktop.move_mouse(cmd_data.get("x"), cmd_data.get("y"))
                elif tool == "click":
                    result = desktop.click()
                elif tool == "type":
                    result = desktop.type_text(cmd_data.get("text"))
                elif tool == "press":
                    result = desktop.press_key(cmd_data.get("key"))
                elif tool == "screenshot":
                    result = desktop.take_screenshot(cmd_data.get("name", "scr.png"))
                
                print(f"✅ Result: {result}")
                
            else:
                # Normal Text Response
                print(f"SysChat: {raw_response}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()