import sys
import os

# Adjust path to import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import generate_system_prompt
from brain import ask_llm

def run_test():
    print("--- Manual Prompt Test ---")
    
    metadata = {
        "filename": "backup.sh",
        "size_bytes": 150,
        "size_readable": "0.15 KB",
        "is_log_file": False
    }
    content = """#!/bin/bash
tar -czf backup.tar.gz /var/www/html
"""
    
    prompt = generate_system_prompt(metadata, content)
    
    print("\n[GENERATED PROMPT]")
    print(prompt)
    
    question = "Can you write a python version of this script?"
    print(f"\n[USER QUESTION]: {question}")
    
    print("\nSysChat is thinking (if LLM is configured)...")
    answer = ask_llm(prompt, question)
    print(f"\n[LLM ANSWER]:\n{answer}")

if __name__ == "__main__":
    run_test()

