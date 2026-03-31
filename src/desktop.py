import time
import os
import base64
import io

# pyautogui requires a running display (X11/Windows).  We import it lazily so
# that the module can be loaded in headless test environments and patched via
# unittest.mock.patch.
try:
    import pyautogui
    pyautogui.FAILSAFE = True   # Slam mouse to corner to ABORT script
    pyautogui.PAUSE = 1.0       # Visible delay between actions
except ImportError:             # pragma: no cover
    pyautogui = None  # type: ignore


# ---------------------------------------------------------------------------
# Standalone helpers used by agent.py
# ---------------------------------------------------------------------------

def normalize_coordinate(coord, max_val):
    """
    Maps a coordinate in the 0–1000 range to an actual screen pixel value.

    Args:
        coord:   Integer in [0, 1000].
        max_val: Actual screen dimension in pixels (width or height).

    Returns:
        Integer pixel value.

    Raises:
        ValueError: If coord is outside [0, 1000].
    """
    if coord < 0 or coord > 1000:
        raise ValueError(f"Coordinate {coord} is out of range [0, 1000]")
    return int(coord * max_val / 1000)


def capture_screen():
    """Captures the screen and returns a base64-encoded PNG string."""
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def execute_action(action_plan):
    """
    Executes a single action dict produced by the OODA agent loop.

    Supported actions:
        CLICK  — requires x, y (0–1000 coords mapped to screen pixels)
        DONE   — signals task completion (no-op)
        FAIL   — signals task failure (no-op)

    Args:
        action_plan: dict with at least an "action" key.

    Returns:
        True on success.

    Raises:
        ValueError: For missing required fields or unknown actions.
    """
    action = action_plan.get("action")
    if not action:
        raise ValueError("Action plan missing 'action' field")

    if action == "CLICK":
        x = action_plan.get("x")
        y = action_plan.get("y")
        if x is None or y is None:
            raise ValueError("CLICK action requires both 'x' and 'y' fields")

        screen_width, screen_height = pyautogui.size()
        actual_x = normalize_coordinate(x, screen_width)
        actual_y = normalize_coordinate(y, screen_height)
        pyautogui.moveTo(actual_x, actual_y, duration=0.5)
        pyautogui.click()
        return True

    elif action in ("DONE", "FAIL"):
        return True

    else:
        raise ValueError(f"Unknown action: {action}")


# ---------------------------------------------------------------------------
# DesktopController class — used by main.py interactive mode
# ---------------------------------------------------------------------------

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
        path = os.path.abspath(filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return f"Screenshot saved to {path}"

    def move_mouse(self, x, y):
        """Moves mouse safely within screen bounds."""
        if not (0 <= x <= self.screen_width and 0 <= y <= self.screen_height):
            return "Error: Coordinates out of bounds."
        pyautogui.moveTo(x, y, duration=0.5)
        return f"Moved to {x}, {y}"

    def click(self):
        """Clicks current position."""
        pyautogui.click()
        return "Clicked."

    def type_text(self, text):
        """Types text like a human."""
        pyautogui.write(text, interval=0.1)
        return f"Typed: {text}"

    def press_key(self, key):
        """Presses a specific key (enter, esc, etc)."""
        valid_keys = pyautogui.KEY_NAMES
        if key not in valid_keys:
            return f"Error: Invalid key '{key}'"
        pyautogui.press(key)
        return f"Pressed {key}"

    def wait(self, seconds):
        """Pauses execution for a set time."""
        time.sleep(float(seconds))
        return f"Waited {seconds}s"

    def open_app(self, app_name):
        """
        Opens an app by simulating: Win Key -> Type Name -> Enter.
        Works for almost any installed program.
        """
        pyautogui.press('win')
        time.sleep(1.0)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(1.0)
        pyautogui.press('enter')
        time.sleep(2.0)
        return f"Opened application: {app_name}"


# Simple test if run directly
if __name__ == "__main__":
    ctrl = DesktopController()
    print(f"Screen: {ctrl.get_screen_info()}")
    print("TEST MODE: I will move the mouse in 3 seconds. Slam corner to abort!")
    time.sleep(3)
    ctrl.move_mouse(100, 100)
    print("Done.")
