import inspect
from typing import Callable, Dict, Any, List
from src.interface.database import db

class ToolRegistry:
    """
    A central registry for all tools (functions) that agents can use.
    Maps string names (from YAML) to actual Python callables.
    """
    _registry: Dict[str, Callable] = {}

    @classmethod
    def register_tool(cls, name: str):
        """
        Decorator to register a function as a tool.
        Usage:
            @ToolRegistry.register_tool("my_tool")
            def my_function(...): ...
        """
        def decorator(func: Callable):
            cls._registry[name] = func
            return func
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Callable:
        """Retrieves a tool function by name."""
        if name not in cls._registry:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return cls._registry[name]

    @classmethod
    def list_tools(cls) -> List[str]:
        """Returns a list of all registered tool names."""
        return list(cls._registry.keys())

    @classmethod
    def execute(cls, tool_name: str, **kwargs) -> Any:
        """
        Safely executes a tool with the provided arguments.
        """
        try:
            func = cls.get_tool(tool_name)
            # You could add argument validation here if needed
            return func(**kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

# =============================================================================
#  DEFAULT TOOLS
#  (These are available to any agent immediately)
# =============================================================================

@ToolRegistry.register_tool("python")
def run_python_repl(code: str) -> str:
    """
    A simple (unsafe) Python REPL for demonstration.
    WARNING: specific sandbox implementation recommended for production.
    """
    try:
        # Capture stdout to return it
        import io
        import sys
        
        # Create a buffer to capture print statements
        buffer = io.StringIO()
        sys.stdout = buffer
        
        # Execute the code
        exec_globals = {}
        exec(code, exec_globals)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        result = buffer.getvalue()
        return result if result else "Code executed successfully (no output)."
        
    except Exception as e:
        sys.stdout = sys.__stdout__ # Ensure stdout is restored even on error
        return f"Python Execution Error: {e}"

@ToolRegistry.register_tool("file_read")
def read_file(filepath: str) -> str:
    """Reads a file from the local filesystem."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@ToolRegistry.register_tool("save_memory")
def save_knowledge(key: str, value: str) -> str:
    """
    Saves a fact to the database. 
    Example: save_memory("project_deadline", "Friday 5PM")
    """
    try:
        db.save_memory(key, value)
        return f"✅ Saved to database: {key} = {value}"
    except Exception as e:
        return f"❌ Database Error: {e}"

@ToolRegistry.register_tool("read_memory")
def read_knowledge(key: str) -> str:
    """Retrieves a fact from the database."""
    val = db.get_memory(key)
    if val:
        return f"📖 Found: {val}"
    return f"🤷‍♂️ Nothing found for '{key}'"

@ToolRegistry.register_tool("recall_everything")
def read_all_knowledge() -> str:
    """Reads all stored memories. Use sparingly."""
    all_mem = db.get_all_memory()
    if not all_mem:
        return "Memory is empty."
    return str(all_mem)


# Simple test block
if __name__ == "__main__":
    print("Registered Tools:", ToolRegistry.list_tools())
    
    # Test execution
    print("\n--- Testing Python Tool ---")
    code_to_run = "print(5 + 5)"
    result = ToolRegistry.execute("python", code=code_to_run)
    print(f"Result: {result}")