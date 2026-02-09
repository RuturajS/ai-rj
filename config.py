
import os

# --- AI Configuration ---
# Use 'openai', 'gemini', 'ollama' (local), or 'openrouter'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")

# --- Voice Settings ---
WAKE_WORD = "RJ"
VOICE_ID = 0  # Index of the TTS voice

# --- path Constraints ---
# ONLY operations within these paths are allowed for file manipulation
ALLOWED_PATHS = [
    os.path.abspath("workspace"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop")
]

# --- Safety ---
# Commands that require explicit user confirmation (y/n)
REQUIRE_CONFIRMATION = [
    "delete_file",
    "shutdown_system",
    "send_email",
    "upload_file"
]
