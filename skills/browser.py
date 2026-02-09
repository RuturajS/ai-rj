
import webbrowser
from command_registry import registry, CommandRegistry

@registry.register(name="open_browser", description="Opens a URL in the default browser.", safe=True)
def open_browser(url: str):
    """Opens a website in the default browser."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url}"

@registry.register(name="google_search", description="Performs a Google search.", safe=True)
def google_search(query: str):
    """Searches Google for the given query."""
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searched Google for: {query}"
