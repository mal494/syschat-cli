import unittest
from unittest.mock import patch
import sys
import os

# Adjust path to import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from desktop import normalize_coordinate, execute_action

class TestDesktop(unittest.TestCase):
    
    def test_normalize_coordinate(self):
        # 0 -> 0
        self.assertEqual(normalize_coordinate(0, 1920), 0)
        # 1000 -> max
        self.assertEqual(normalize_coordinate(1000, 1920), 1920)
        # 500 -> half
        self.assertEqual(normalize_coordinate(500, 1920), 960)
        
        # Out of bounds
        with self.assertRaises(ValueError):
            normalize_coordinate(-1, 1920)
        with self.assertRaises(ValueError):
            normalize_coordinate(1001, 1920)

    @patch('desktop.pyautogui')
    def test_execute_action_click(self, mock_pyautogui):
        # Mock screen size
        mock_pyautogui.size.return_value = (1000, 1000)
        
        action = {"action": "CLICK", "x": 500, "y": 500}
        success = execute_action(action)
        
        self.assertTrue(success)
        mock_pyautogui.moveTo.assert_called_with(500, 500, duration=0.5)
        mock_pyautogui.click.assert_called()

    @patch('desktop.pyautogui')
    def test_execute_action_validation(self, mock_pyautogui):
        # Missing coords
        action = {"action": "CLICK", "x": 500}
        with self.assertRaises(ValueError):
            execute_action(action)
            
        # Unknown action
        action = {"action": "DANCE"}
        with self.assertRaises(ValueError):
            execute_action(action)

if __name__ == '__main__':
    unittest.main()
