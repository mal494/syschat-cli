import pyautogui
import time
import os
from datetime import datetime

# --- SAFETY FIRST ---
# Slam mouse to corner to ABORT script
pyautogui.FAILSAFE = True 
# Add a delay between actions so you can see what's happening
pyautogui.PAUSE = 1.0 

class DesktopController:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        
    def get_screen_info(self):
        """Returns resolution and current mouse position."""
        x, y = pyautogui.position()
        return {
            "resolution": f"{self.screen_width}x{self.screen_height}",
            "mouse_position": (x, y)
        }

    def take_screenshot(self, filename="screenshot.png"):
        """Gives the AI 'eyes' to see what is on screen."""
        # Save to a temp folder or project root
        path = os.path.abspath(filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return f"Screenshot saved to {path}"

    def move_mouse(self, x, y):
        """Moves mouse safely."""
        # Sanity check coordinates
        if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
            return "Error: Coordinates out of bounds."
        
        pyautogui.moveTo(x, y, duration=0.5) # Smooth movement
        return f"Moved to {x}, {y}"

    def click(self):
        """Clicks current position."""
        pyautogui.click()
        return "Clicked."

    def type_text(self, text):
        """Types text like a keyboard."""
        pyautogui.write(text, interval=0.1) # Type like a human
        return f"Typed: {text}"

    def press_key(self, key):
        """Presses a specific key (enter, esc, etc)."""
        valid_keys = pyautogui.KEY_NAMES
        if key not in valid_keys:
            return f"Error: Invalid key '{key}'"
            
        pyautogui.press(key)
        return f"Pressed {key}"

# Simple test if run directly
if __name__ == "__main__":
    ctrl = DesktopController()
    print(f"Screen: {ctrl.get_screen_info()}")
    print("⚠️ TEST MODE: I will move the mouse in 3 seconds. Slam corner to abort!")
    time.sleep(3)
    ctrl.move_mouse(100, 100)
    print("Done.")