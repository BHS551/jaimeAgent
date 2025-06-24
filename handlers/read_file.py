# handlers/read_file.py
"""
Read a file OR return the recursive listing of a directory.

Parameters
----------
path : str
    Absolute or relative path.  If a directory, we list its children
    (depth-first) and return a JSON dump of file paths.
"""

import json
import os
import pathlib


def handle(path: str) -> str:
    abs_path = os.path.abspath(os.path.expanduser(path))

    if not os.path.exists(abs_path):
        return f"❌ Error: file or directory not found: {abs_path}"

    p = pathlib.Path(abs_path)

    if p.is_file():
        try:
            return p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "⚠️ Binary file – not displayed."
    else:  # directory: list recursively
        files = [str(fp.relative_to(p)) for fp in p.rglob("*") if fp.is_file()]
        return json.dumps(files, indent=2, ensure_ascii=False)
