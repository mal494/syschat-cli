import base64
import io
import time
import mss
import pyautogui
from PIL import Image

# Safety: Moving mouse to any corner will abort the script
pyautogui.FAILSAFE = True

# Constants for action execution
RETRY_COUNT = 1
RETRY_DELAY = 1.0  # seconds

def get_screen_size():
    """
    Returns the logical screen size (width, height) used by pyautogui.
    """
    return pyautogui.size()

def capture_screen(max_dimension=1024):
    """
    Captures the primary screen, resizes it to fit within max_dimension 
    (maintaining aspect ratio), and returns it as a base64 encoded string.
    
    Returns:
        str: Base64 encoded PNG image.
    """
    with mss.mss() as sct:
        # Capture the primary monitor (monitor 1)
        # monitor 0 is "all monitors combined", 1 is primary.
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # Resize if necessary to save tokens/bandwidth
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            scale = min(max_dimension / width, max_dimension / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Encode to base64
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        
        return base64_str

def normalize_coordinate(value, max_val):
    """
    Converts a 0-1000 normalized value to a pixel coordinate.
    """
    if not (0 <= value <= 1000):
        raise ValueError(f"Coordinate value {value} out of range (0-1000)")
    return int((value / 1000) * max_val)

def execute_action(action_dict):
    """
    Executes a desktop action based on a dictionary command.
    
    Expected format:
    {
        "action": "CLICK" | "TYPE" | "PRESS" | "SCROLL",
        "x": int (0-1000) [for CLICK],
        "y": int (0-1000) [for CLICK],
        "text": str [for TYPE],
        "key": str [for PRESS],
        "amount": int [for SCROLL]
    }
    """
    action_type = action_dict.get("action", "").upper()
    screen_width, screen_height = get_screen_size()
    
    last_exception = None
    
    for attempt in range(RETRY_COUNT + 1):
        try:
            if action_type == "CLICK":
                x_norm = action_dict.get("x")
                y_norm = action_dict.get("y")
                
                if x_norm is None or y_norm is None:
                    raise ValueError("CLICK action requires 'x' and 'y' coordinates.")
                
                target_x = normalize_coordinate(x_norm, screen_width)
                target_y = normalize_coordinate(y_norm, screen_height)
                
                # Move first (visual feedback) then click
                pyautogui.moveTo(target_x, target_y, duration=0.5)
                pyautogui.click()
                
            elif action_type == "TYPE":
                text = action_dict.get("text")
                if text is None:
                    raise ValueError("TYPE action requires 'text'.")
                pyautogui.write(text, interval=0.05)
                
            elif action_type == "PRESS":
                key = action_dict.get("key")
                if key is None:
                    raise ValueError("PRESS action requires 'key'.")
                pyautogui.press(key)
                
            elif action_type == "SCROLL":
                amount = action_dict.get("amount")
                if amount is None:
                    raise ValueError("SCROLL action requires 'amount'.")
                pyautogui.scroll(int(amount))
                
            else:
                raise ValueError(f"Unknown action type: {action_type}")
                
            # If we reach here, success
            return True
            
        except Exception as e:
            last_exception = e
            if attempt < RETRY_COUNT:
                time.sleep(RETRY_DELAY)
            else:
                print(f"Action failed after retries: {str(e)}")
                # Depending on strictness, we might want to re-raise or return False
                # For this agent, logging and returning False allows the loop to handle it
                return False
