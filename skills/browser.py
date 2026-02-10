
import webbrowser
import pyautogui
import time
from command_registry import registry, CommandRegistry

@registry.register(name="open_browser", description="Opens a URL in the default browser.", safe=True)
def open_browser(url: str):
    """Opens a website in the default browser."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url} for you, sir."

@registry.register(name="close_browser", description="Closes the current browser window.", safe=False)
def close_browser():
    """Closes the active window (Alt+F4)."""
    pyautogui.hotkey('alt', 'f4')
    return "Browser closed."

@registry.register(name="close_tab", description="Closes the current browser tab.", safe=True)
def close_tab():
    """Closes the active tab (Ctrl+W)."""
    pyautogui.hotkey('ctrl', 'w')
    return "Tab closed."

@registry.register(name="google_search", description="Performs a Google search.", safe=True)
def google_search(query: str):
    """Searches Google for the given query."""
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searched Google for: {query}"
