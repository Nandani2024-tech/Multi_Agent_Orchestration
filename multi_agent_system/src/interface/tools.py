import inspect
from typing import Callable, Dict, Any, List
from src.interface.database import db
import os

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
def read_file(file_path: str = None, filename: str = None) -> str:
    """
    Reads a file from the filesystem.
    Accepts either 'file_path' or 'filename' as arguments to be AI-friendly.
    """
    # 1. Figure out which argument the AI used
    target_file = file_path or filename
    
    if not target_file:
        return "❌ Error: You must provide a 'file_path' or 'filename'."

    # 2. Security Check (Prevent hacking parent directories)
    if ".." in target_file or target_file.startswith("/"):
        return "❌ Error: Access denied. You can only read files in the current directory."

    # 3. Read the file
    try:
        if not os.path.exists(target_file):
            return f"❌ Error: File '{target_file}' not found."
            
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[:2000]  # Limit length to prevent crashing the AI
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"

@ToolRegistry.register_tool("read_memory")
def read_knowledge(key: str) -> str:
    """Retrieves a fact from the database."""
    val = db.get_memory(key)
    if val:
        return f"📖 Found: {val}"
    return f"🤷‍♂️ Nothing found for '{key}'"

# In src/interface/tools.py

@ToolRegistry.register_tool("recall_everything")
def read_all_knowledge(key: str = None, query: str = None) -> str:
    """
    Retrieves memories from the database. 
    Can filter by 'key' or 'query' if provided.
    """
    # 1. Fetch all raw data
    memories = db.get_all_memory() # Returns list of (id, key, value, timestamp)
    
    if not memories:
        return "No memories found in database."

    # 2. Format and Filter
    results = []
    search_term = key or query  # Agent might call it 'key' or 'query'
    
    for mem in memories:
        # mem structure: (id, key, value, timestamp)
        m_key = mem[1]
        m_val = mem[2]
        
        # If agent asked for a specific key, filter for it
        if search_term:
            if search_term.lower() not in m_key.lower() and search_term.lower() not in m_val.lower():
                continue # Skip this memory if it doesn't match
        
        results.append(f"{m_key}: {m_val}")

    if not results:
        return f"No memories found matching '{search_term}'."
        
    return "\n".join(results)


# Simple test block
if __name__ == "__main__":
    print("Registered Tools:", ToolRegistry.list_tools())
    
    # Test execution
    print("\n--- Testing Python Tool ---")
    code_to_run = "print(5 + 5)"
    result = ToolRegistry.execute("python", code=code_to_run)
    print(f"Result: {result}")