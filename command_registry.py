
from typing import Callable, Dict, Any, Optional
import inspect
import config

class CommandRegistry:
    """
    Central registry for all allowed AI commands.
    Enforces strict function mapping and permissions.
    """
    
    def __init__(self):
        self._commands: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, safe: bool = False):
        """
        Decorator to register a function as an executable command.
        
        Args:
            name: The command name used by the LLM (e.g., 'open_browser').
            description: Description of what the command does.
            safe: If True, bypasses confirmation (e.g., read-only ops).
        """
        def decorator(func: Callable):
            if name in self._commands:
                raise ValueError(f"Command '{name}' is already registered.")
            
            # Store function and metadata
            self._commands[name] = func
            self._metadata[name] = {
                "description": description,
                "safe": safe,
                "params": str(inspect.signature(func))
            }
            return func
        return decorator

    def get_command(self, name: str) -> Optional[Callable]:
        return self._commands.get(name)

    def is_safe(self, name: str) -> bool:
        if name not in self._commands:
            return False
        # Check explicit registry safety check AND config override
        return self._metadata[name]["safe"] and name not in config.REQUIRE_CONFIRMATION

    def list_commands(self):
        """Returns a string list of all available commands for the LLM system prompt."""
        cmd_list = []
        for name, meta in self._metadata.items():
            cmd_list.append(f"- {name}: {meta['description']} (Params: {meta['params']})")
        return "\n".join(cmd_list)

    def execute(self, command_name: str, **kwargs) -> Any:
        """
        Safely executes a registered command.
        """
        if command_name not in self._commands:
            return f"Error: Command '{command_name}' is not supported."

        func = self._commands[command_name]
        
        # Security Check
        if not self.is_safe(command_name):
            print(f"\n[SECURITY] Command '{command_name}' requires confirmation.")
            confirm = input(f"Execute {command_name} with {kwargs}? (y/n): ").lower()
            if confirm != 'y':
                return "Action cancelled by user."

        try:
            return func(**kwargs)
        except Exception as e:
            return f"Execution Error: {str(e)}"

# Global Registry Instance
registry = CommandRegistry()
