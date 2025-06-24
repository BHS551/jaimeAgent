# handlers/handler_read_file.py
import os

def handle(path: str) -> str:
    """Read and return the contents of the given text file."""
    expanded = os.path.expanduser(path)
    abs_path = expanded if os.path.isabs(expanded) else os.path.join(os.getcwd(), os.path.normpath(expanded))
    if not os.path.isfile(abs_path):
        return f"Error: file not found: {abs_path}"
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {abs_path}: {e}"