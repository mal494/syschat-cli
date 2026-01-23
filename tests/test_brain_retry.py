import unittest
from unittest.mock import MagicMock
import sys
import os

# Adjust path to import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from brain import retry_api_call

class TestRetry(unittest.TestCase):
    
    def test_retry_success(self):
        mock_func = MagicMock(return_value="Success")
        decorated = retry_api_call(max_retries=3, delay=0.01)(mock_func)
        
        result = decorated()
        self.assertEqual(result, "Success")
        self.assertEqual(mock_func.call_count, 1)

    def test_retry_failure_then_success(self):
        # Fail twice, then succeed
        mock_func = MagicMock(side_effect=[Exception("Fail 1"), Exception("Fail 2"), "Success"])
        decorated = retry_api_call(max_retries=3, delay=0.01)(mock_func)
        
        result = decorated()
        self.assertEqual(result, "Success")
        self.assertEqual(mock_func.call_count, 3)

    def test_retry_failure_max(self):
        # Fail always
        mock_func = MagicMock(side_effect=Exception("Fail Always"))
        decorated = retry_api_call(max_retries=3, delay=0.01)(mock_func)
        
        result = decorated()
        self.assertTrue(result.startswith("API Error"))
        self.assertEqual(mock_func.call_count, 3)

if __name__ == '__main__':
    unittest.main()
