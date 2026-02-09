
import pyautogui
import datetime
from command_registry import registry

# Fail-safe to abort scripts if mouse is moved to corner
pyautogui.FAILSAFE = True

@registry.register(name="type_text", description="Types text at the current cursor position.", safe=False)
def type_text(text: str):
    """Types the given text securely."""
    pyautogui.write(text, interval=0.05)
    return "Text typed."

@registry.register(name="press_key", description="Presses a specific keyboard key.", safe=False)
def press_key(key: str):
    """Presses a key (e.g., 'enter', 'esc')."""
    if key in pyautogui.KEY_NAMES:
        pyautogui.press(key)
        return f"Key '{key}' pressed."
    return f"Error: Key '{key}' not supported."

@registry.register(name="take_screenshot", description="Takes a screenshot of the screen.", safe=True)
def take_screenshot():
    """Captures the screen and saves it."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    pyautogui.screenshot(filename)
    return f"Screenshot saved as {filename}"
