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
# Note: Ensure prompts.py exists, or remove this import and the AUTO_SYSTEM_PROMPT usage
try:
    from prompts import AUTO_SYSTEM_PROMPT
except ImportError:
    AUTO_SYSTEM_PROMPT = "You are a Desktop Automation Agent. Use the available tools."

def main():
    if len(sys.argv) < 2:
        print("\nUsage: python src/main.py <mode> [path]")
        print("Modes:")
        print("  auto       -> Control the mouse/keyboard (Agent Mode)")
        print("  dir <path> -> Audit a folder")
        print("  file <path> -> Analyze a file")
        return

    mode = sys.argv[1]
    system_context = ""
    
    # Initialize controller (used if mode is auto, or if tools are needed later)
    desktop = DesktopController()

    # --- MODE 1: AUTOMATION (AGENT) 🤖 ---
    if mode == "auto":
        print("--- SysChat: Desktop Automation Mode ---")
        screen_info = desktop.get_screen_info()
        
        # We inject the specific resolution into the system prompt
        system_context = f"{AUTO_SYSTEM_PROMPT}\nCURRENT SCREEN RESOLUTION: {screen_info['resolution']}"
        
        print(f"Agent Ready. Screen: {screen_info['resolution']}")
        print("⚠️  SAFETY: Slam mouse to any corner to abort script.")

    # --- MODE 2: DIRECTORY AUDIT 📂 ---
    elif mode == "dir":
        if len(sys.argv) < 3:
            print("Error: Missing path. Usage: python src/main.py dir <path>")
            return
        path = sys.argv[2]
        print(f"Scanning {path}...")
        
        # Scan the folder
        tree, content = scan_directory(path)
        
        system_context = f"""
        ROLE: Lead Developer.
        [PROJECT TREE]
        {tree}
        [CODE CONTENT]
        {content}
        INSTRUCTIONS: Analyze the architecture based strictly on the files above.
        """
        print(f"Context Loaded ({len(content)} chars).")

    # --- MODE 3: SINGLE FILE ANALYSIS 📄 ---
    else:
        # Fallback to file mode. Takes the argument as the path.
        target_path = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
        
        print(f"Scanning {target_path}...")
        meta = get_file_metadata(target_path)
        if "error" in meta:
            print(f"Error: {meta['error']}")
            return
            
        _, content = read_file_safe(target_path)
        system_context = f"ROLE: SysAdmin.\n[METADATA]\n{meta}\n[CONTENT]\n{content}"
        print("File Loaded.")

    # --- MAIN INTERACTION LOOP ---
    print("--------------------------------------------------")
    print("Type 'exit' to quit.")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # 1. Get AI Response
            print("Thinking...", end="\r")
            raw_response = ask_llm(system_context, user_input)
            print(" " * 20, end="\r") # Clear the 'Thinking...' line

            # 2. Check for Tools (Only acts if in 'auto' mode)
            is_cmd, cmd_data = extract_json(raw_response)
            
            if is_cmd and mode == "auto":
                # Normalize to list so we can handle single OR multiple commands
                actions = cmd_data if isinstance(cmd_data, list) else [cmd_data]
                
                print(f"⚡ RECEIVED {len(actions)} ACTIONS:")
                
                for action in actions:
                    if not isinstance(action, dict):
                        continue
                    
                    tool = action.get("tool")
                    if not tool: continue
                    
                    print(f"   > EXECUTING: {str(tool).upper()}...", end=" ")
                    
                    result = "Unknown tool"
                    
                    # EXECUTION LOGIC
                    try:
                        if tool == "move":
                            # Default to current position if args missing
                            curr_x, curr_y = desktop.get_screen_info()['mouse_position']
                            x = action.get("x", curr_x)
                            y = action.get("y", curr_y)
                            result = desktop.move_mouse(x, y)
                            
                        elif tool == "click":
                            result = desktop.click()
                            
                        elif tool == "type":
                            text = action.get("text", "")
                            result = desktop.type_text(text)
                            
                        elif tool == "press":
                            key = action.get("key", "")
                            result = desktop.press_key(key)
                        
                        # --- NEW HANDLER ---
                        elif tool == "open":
                            app_name = action.get("name", "")
                            print(f"   > LAUNCHING: {app_name}...", end=" ")
                            result = desktop.open_app(app_name)
                        # -------------------
                        
                        elif tool == "wait":
                            sec = action.get("seconds", 1.0)
                            result = desktop.wait(sec)
                            
                        elif tool == "screenshot":
                            name = action.get("name", "scr.png")
                            result = desktop.take_screenshot(name)
                    
                    except Exception as exec_err:
                        result = f"Failed: {exec_err}"

                    print(f"✅ {result}")
                    time.sleep(0.2) # Small buffer between all actions
                
            else:
                # If not a command (or not in auto mode), just print the text
                print(f"SysChat: {raw_response}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()