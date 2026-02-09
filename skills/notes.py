
import os
import datetime
from command_registry import registry
from config import ALLOWED_PATHS

LOGS_DIR = os.path.join(os.getcwd(), "logs")
NOTES_FILE = os.path.join(LOGS_DIR, "notes.txt")

@registry.register(name="take_note", description="Saves a text note to the log file.", safe=True)
def take_note(content: str):
    """Appends a timestamped note to logs/notes.txt"""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {content}\n"
    
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
        
    return f"Note saved: {content}"

@registry.register(name="read_notes", description="Reads the last 5 notes.", safe=True)
def read_notes():
    """Reads the most recent notes."""
    if not os.path.exists(NOTES_FILE):
        return "No notes found."
        
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    last_notes = lines[-5:] # Get last 5
    return "Here are your recent notes:\n" + "".join(last_notes)
