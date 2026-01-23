import sys
import os

# Ensure Python can find the 'src' modules regardless of where script is run
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer import get_file_metadata, read_file_safe
from brain import ask_llm

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
    4. Keep answers concise, professional, and technical.
    """

def main():
    # 1. Argument Validation
    if len(sys.argv) < 2:
        print("\nUsage: python src/main.py <path_to_file>")
        print("Example: python src/main.py requirements.txt\n")
        return

    target_file = sys.argv[1]
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

if __name__ == "__main__":
    main()