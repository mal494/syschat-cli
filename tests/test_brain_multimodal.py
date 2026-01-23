import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust path to import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from brain import ask_llm

class TestBrainMultimodal(unittest.TestCase):
    
    @patch('brain.requests.post')
    @patch.dict(os.environ, {"LLM_API_KEY": "fake-key", "LLM_MODEL": "gpt-4o"})
    def test_openai_payload_construction(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Action Plan"}}]
        }
        mock_post.return_value = mock_response

        # Call function
        ask_llm("System", "User Query", image_data="base64img")

        # Verify payload
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        
        # Check if image_url is present in the user message
        user_msg = payload['messages'][1]
        self.assertEqual(user_msg['role'], 'user')
        self.assertTrue(isinstance(user_msg['content'], list))
        self.assertEqual(user_msg['content'][1]['type'], 'image_url')
        self.assertIn("base64img", user_msg['content'][1]['image_url']['url'])

    @patch('brain.requests.post')
    @patch.dict(os.environ, {"LLM_API_KEY": "", "LLM_MODEL": "llava"})
    def test_ollama_payload_construction(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Ollama Action"}
        }
        mock_post.return_value = mock_response

        # Call function
        ask_llm("System", "User Query", image_data="base64img")

        # Verify payload
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        
        # Check if images list is present in the user message
        user_msg = payload['messages'][1]
        self.assertEqual(user_msg['role'], 'user')
        self.assertIn("images", user_msg)
        self.assertEqual(user_msg['images'][0], "base64img")

if __name__ == '__main__':
    unittest.main()
