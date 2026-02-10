
import webbrowser
import pyautogui
import time
import requests
from bs4 import BeautifulSoup
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

@registry.register(name="get_page_text", description="Retrieves text content from a URL to answer questions.", safe=True)
def get_page_text(url: str):
    """Fetches text content from a URI."""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text[:3000]
    except Exception as e:
        return f"Error retrieving page info: {str(e)}"

@registry.register(name="search_and_summarize", description="Searches the web and provides a spoken summary of the information.", safe=True)
def search_and_summarize(query: str):
    """Marker command for the engine to handle a deeper search."""
    search_url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the first search result link
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if "url?q=" in href and "webcache" not in href:
                actual_link = href.split("url?q=")[1].split("&")[0]
                if actual_link.startswith("http"):
                    links.append(actual_link)
        
        if links:
            return {"is_info_retrieval": True, "query": query, "first_link": links[0]}
        return {"is_info_retrieval": True, "query": query, "first_link": None}
    except:
        return {"is_info_retrieval": True, "query": query, "first_link": None}
