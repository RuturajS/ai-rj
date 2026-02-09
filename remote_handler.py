
from command_registry import registry
from llm_engine import LLMEngine
import skills.browser
import skills.system
import skills.files
import skills.media
import skills.input

# Shared engine instance
llm = LLMEngine()

def handle_remote_command(text: str) -> str:
    """
    Processes a text command from Discord/Telegram and returns the output.
    """
    if not text:
        return "Empty command."

    # 1. Parse Intent
    intent = llm.parse_intent(text)
    cmd_name = intent.get("command")
    args = intent.get("args", {})

    if not cmd_name or cmd_name == "unknown":
        return f"I didn't understand: '{text}'"

    # 2. Execute
    try:
        result = registry.execute(cmd_name, **args)
        return str(result)
    except Exception as e:
        return f"Error executing '{cmd_name}': {e}"
