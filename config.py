
import os
from dotenv import load_dotenv

# Load all potential keys
load_dotenv()

# --- Voice ---
WAKE_WORD = os.getenv("WAKE_WORD", "RJ")
try:
    MICROPHONE_INDEX = int(os.getenv("MICROPHONE_INDEX", 1))
except ValueError:
    MICROPHONE_INDEX = 1

# --- Provider Config ---
# 'auto', 'openai', 'gemini', 'anthropic', 'groq', 'ollama'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").lower()

# --- API Keys ---
KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "gemini": os.getenv("GOOGLE_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "groq": os.getenv("GROQ_API_KEY"),
    "openrouter": os.getenv("OPENROUTER_API_KEY"),
}

# --- Remote Access ---
REMOTE_CONFIG = {
    "discord_token": os.getenv("DISCORD_BOT_TOKEN"),
    "discord_channel_id": int(os.getenv("DISCORD_ALLOWED_CHANNEL_ID", 0) or 0),
    "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN"),
    "telegram_user_id": int(os.getenv("TELEGRAM_ALLOWED_USER_ID", 0) or 0)
}

# --- Base URLs ---
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1")
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "local-model")

# --- Constraints ---
ALLOWED_PATHS = [
    os.path.abspath("workspace"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop")
]

REQUIRE_CONFIRMATION = [
    "delete_file",
    "shutdown_system",
    "send_email"
]
