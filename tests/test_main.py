import unittest
import sys
import os

# Adjust path to import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import generate_system_prompt

class TestMain(unittest.TestCase):
    def test_generate_system_prompt_script_instructions(self):
        metadata = {"filename": "test.py"}
        content = "print('hello')"
        prompt = generate_system_prompt(metadata, content)
        
        self.assertIn("If the user asks for a script", prompt)
        self.assertIn("safe Bash or Python script block", prompt)

    def test_generate_system_prompt_log_instructions(self):
        metadata = {"filename": "test.log", "is_log_file": True}
        content = "ERROR: Fail"
        prompt = generate_system_prompt(metadata, content)
        
        self.assertIn("LOG SUMMARIZATION", prompt)
        self.assertIn("summarize the errors found", prompt)

    def test_interaction_prompt_inclusion(self):
        # This is a bit more of an integration test but it verifies prompt logic
        metadata = {"filename": "service.log", "is_log_file": True}
        content = "ERROR: 500 Internal Server Error"
        prompt = generate_system_prompt(metadata, content)
        
        # Verify that the prompt given to LLM would contain the log data
        self.assertIn("service.log", prompt)
        self.assertIn("ERROR: 500 Internal Server Error", prompt)


if __name__ == '__main__':
    unittest.main()
