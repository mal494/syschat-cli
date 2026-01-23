import sys
import os
import argparse

# Ensure Python can find the 'src' modules regardless of where script is run
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer import get_file_metadata, read_file_safe
from brain import ask_llm
from agent import run_agent_loop

# Configure LLM access
from dotenv import load_dotenv
load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "darkidol")  # Default model


def generate_system_prompt(metadata, content):
    """
    Constructs the prompt engineering that gives the AI its persona.
    """
    return f"""
    ROLE: You are 'SysChat', an expert System Administrator Assistant.
    TASK: Answer questions about the specific file below based on its metadata and content.

    [FILE METADATA]
    {metadata}

    [FILE CONTENT PREVIEW]
    {content}

    GUIDELINES:
    1. If the User asks about file size, dates, or permissions, use the METADATA.
    2. If the User asks about what the code/text does, use the CONTENT PREVIEW.
    3. If the content is omitted, explain that you cannot see inside this file type.
    4. SCRIPT GENERATION: If the user asks for a script, provide a complete, safe Bash or Python script block based on the file's context.
    5. LOG SUMMARIZATION: If the file is a log file (check metadata), summarize the errors found in the content preview.
    6. Keep answers concise, professional, and technical.
    """

def file_chat_mode(target_file):
    print(f"--- SysChat: Analyzing {target_file} ---")

    # 2. Harvest Metadata
    meta = get_file_metadata(target_file)
    if "error" in meta:
        print(f"Error: {meta['error']}")
        return

    # 3. Harvest Content (Safety First)
    is_readable, content = read_file_safe(target_file, meta.get('size_bytes', 0))

    # 4. Build the Brain
    system_context = generate_system_prompt(meta, content)
    
    print(f"Target: {meta['filename']} | Size: {meta['size_readable']}")
    print(f"Content Status: {'Loaded' if is_readable else 'Skipped (See logs)'}")
    print("--------------------------------------------------")
    print("Type 'exit' or 'quit' to stop.")

    # 5. Interaction Loop
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye.")
                break
            
            if not user_input.strip():
                continue

            print("SysChat is thinking...", end="\r")
            answer = ask_llm(system_context, user_input)
            
            # Clear the "thinking" line and print answer
            print(" " * 20, end="\r") 
            print(f"SysChat: {answer}")

        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

def main():
    parser = argparse.ArgumentParser(description="SysChat: AI-powered system assistant")
    parser.add_argument("target", nargs="?", help="File to analyze (File Chat Mode)")
    parser.add_argument("--agent", action="store_true", help="Start the Autonomous Desktop Agent")
    parser.add_argument("--goal", type=str, help="Goal for the Desktop Agent (optional, enables non-interactive start)")
    
    args = parser.parse_args()

    if args.agent:
        goal = args.goal
        if not goal:
            goal = input("Enter the goal for the Desktop Agent: ")
        run_agent_loop(goal)
    elif args.target:
        file_chat_mode(args.target)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
