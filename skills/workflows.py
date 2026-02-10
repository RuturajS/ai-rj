
import os
import json
from command_registry import registry

WORKFLOWS_DIR = "workflows"

if not os.path.exists(WORKFLOWS_DIR):
    os.makedirs(WORKFLOWS_DIR)

@registry.register(name="save_workflow", description="Saves a sequence of commands as a named workflow.", safe=False)
def save_workflow(name: str, commands: list):
    """
    Saves a workflow.
    Example commands: [{"command": "open_browser", "args": {"url": "google.com"}}, ...]
    """
    filepath = os.path.join(WORKFLOWS_DIR, f"{name.lower().replace(' ', '_')}.json")
    with open(filepath, 'w') as f:
        json.dump(commands, f, indent=4)
    return f"Workflow '{name}' has been saved to my memory, Sir."

@registry.register(name="list_workflows", description="Lists all saved workflows.", safe=True)
def list_workflows():
    """Lists available workflows."""
    files = [f.replace(".json", "").replace("_", " ") for f in os.listdir(WORKFLOWS_DIR) if f.endswith(".json")]
    if not files:
        return "You haven't taught me any workflows yet, Sir."
    return "I have the following procedures stored: " + ", ".join(files)

@registry.register(name="run_workflow", description="Executes a saved sequence of commands.", safe=False)
def run_workflow(name: str):
    """
    This is a special command. The main engine should probably handle the extraction
    and step-by-step execution to allow for speech in between.
    For now, we return the commands so main.py can iterate.
    """
    filepath = os.path.join(WORKFLOWS_DIR, f"{name.lower().replace(' ', '_')}.json")
    if not os.path.exists(filepath):
        return f"I'm sorry Sir, I don't have a procedure named '{name}' in my records."
    
    with open(filepath, 'r') as f:
        commands = json.load(f)
    
    return {"is_workflow": True, "steps": commands}
