import sys
import os
import json
import time
from pathlib import Path

# Add src to path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer import get_file_metadata, read_file_safe, scan_directory
from brain import ask_llm, extract_json

try:
    from prompts import AUTO_SYSTEM_PROMPT
except ImportError:
    AUTO_SYSTEM_PROMPT = "You are a Desktop Automation Agent. Use the available tools."


def generate_system_prompt(metadata, content):
    """
    Builds a system prompt string from file metadata and content.

    Includes log-specific instructions for .log files, and script generation
    instructions for all other files.
    """
    filename = metadata.get("filename", "unknown")
    is_log = metadata.get("is_log_file", False)

    if is_log:
        role_instructions = (
            "ROLE: SysAdmin Log Analyst.\n"
            "LOG SUMMARIZATION MODE: summarize the errors found, group by severity, "
            "and suggest remediation steps."
        )
    else:
        role_instructions = (
            "ROLE: SysAdmin.\n"
            "If the user asks for a script, generate a safe Bash or Python script block."
        )

    return (
        f"{role_instructions}\n"
        f"[FILE: {filename}]\n"
        f"[METADATA]\n{metadata}\n"
        f"[CONTENT]\n{content}"
    )


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python src/main.py <mode> [path]")
        print("Modes:")
        print("  auto         -> Control the mouse/keyboard (Agent Mode)")
        print("  dir <path>   -> Audit a folder")
        print("  file <path>  -> Analyze a file")
        print("  <path>       -> Analyze a file (shorthand)")
        return

    mode = sys.argv[1]
    system_context = ""

    # --- MODE 1: AUTOMATION (AGENT) ---
    if mode == "auto":
        from desktop import DesktopController
        desktop = DesktopController()

        print("--- SysChat: Desktop Automation Mode ---")
        screen_info = desktop.get_screen_info()
        system_context = f"{AUTO_SYSTEM_PROMPT}\nCURRENT SCREEN RESOLUTION: {screen_info['resolution']}"
        print(f"Agent Ready. Screen: {screen_info['resolution']}")
        print("SAFETY: Slam mouse to any corner to abort script.")

    # --- MODE 2: DIRECTORY AUDIT ---
    elif mode == "dir":
        if len(sys.argv) < 3:
            print("Error: Missing path. Usage: python src/main.py dir <path>")
            return
        path = sys.argv[2]
        print(f"Scanning {path}...")
        tree, content = scan_directory(path)
        system_context = (
            "ROLE: Lead Developer.\n"
            f"[PROJECT TREE]\n{tree}\n"
            f"[CODE CONTENT]\n{content}\n"
            "INSTRUCTIONS: Analyze the architecture based strictly on the files above."
        )
        print(f"Context Loaded ({len(content)} chars).")

    # --- MODE 3: SINGLE FILE ANALYSIS ---
    else:
        # Accept both `file <path>` and `<path>` directly
        target_path = sys.argv[2] if mode == "file" and len(sys.argv) > 2 else sys.argv[1]

        print(f"Scanning {target_path}...")
        meta = get_file_metadata(target_path)
        if "error" in meta:
            print(f"Error: {meta['error']}")
            return

        _, content = read_file_safe(target_path)
        system_context = generate_system_prompt(meta, content)
        print("File Loaded.")

    # --- MAIN INTERACTION LOOP ---
    print("--------------------------------------------------")
    print("Type 'exit' to quit.")

    # Only create DesktopController when in auto mode (already done above).
    # For non-auto modes we still need the object for the tool dispatcher below.
    desktop = locals().get("desktop")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            print("Thinking...", end="\r")
            raw_response = ask_llm(system_context, user_input)
            print(" " * 20, end="\r")

            is_cmd, cmd_data = extract_json(raw_response)

            if is_cmd and mode == "auto":
                actions = cmd_data if isinstance(cmd_data, list) else [cmd_data]
                print(f"RECEIVED {len(actions)} ACTIONS:")

                for action in actions:
                    if not isinstance(action, dict):
                        continue

                    tool = action.get("tool")
                    if not tool:
                        continue

                    print(f"   > EXECUTING: {str(tool).upper()}...", end=" ")
                    result = "Unknown tool"

                    try:
                        if tool == "move":
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

                        elif tool == "open":
                            app_name = action.get("name", "")
                            result = desktop.open_app(app_name)

                        elif tool == "wait":
                            sec = action.get("seconds", 1.0)
                            result = desktop.wait(sec)

                        elif tool == "screenshot":
                            name = action.get("name", "scr.png")
                            result = desktop.take_screenshot(name)

                    except Exception as exec_err:
                        result = f"Failed: {exec_err}"

                    print(f"OK: {result}")
                    time.sleep(0.2)

            else:
                print(f"SysChat: {raw_response}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
