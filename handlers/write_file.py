import os

"""
Handler module for write_file function.
Must define a `handle(path, content)` function.
"""

def handle(path: str, content: str) -> str:
    """Append content to a file if it exists, or create it with the content (supports ~ expansion)."""
    expanded = os.path.expanduser(path)
    abs_path = expanded if os.path.isabs(expanded) else os.path.join(os.getcwd(), os.path.normpath(expanded))
    parent = os.path.dirname(abs_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    # Open in append mode, create if not exists
    with open(abs_path, "a+", encoding="utf-8") as f:
        f.write(content)
    return f"Appended content to {abs_path}"