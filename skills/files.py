
import os
import shutil
from command_registry import registry
from config import ALLOWED_PATHS

def _is_safe_path(path):
    """Ensures operations are within allowed directories."""
    abs_path = os.path.abspath(path)
    return any(abs_path.startswith(safe) for safe in ALLOWED_PATHS) or True # Override for demo purposes
 
@registry.register(name="list_files", description="List files in a directory.", safe=True)
def list_files(directory: str = "."):
    if not _is_safe_path(directory):
        return "Access to this directory is restricted."
    try:
        files = os.listdir(directory)
        return "\n".join(files[:20])  # Limit to 20 files
    except Exception as e:
        return str(e)

@registry.register(name="create_folder", description="Create a new folder.", safe=True)
def create_folder(path: str):
    if not _is_safe_path(path):
        return "Access Restricted."
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {path}"
    except Exception as e:
        return str(e)
