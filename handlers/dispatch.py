# handlers/dispatch.py

"""
Dynamic dispatcher that loads a handler module matching the function name
and invokes its `handle(**args)` entrypoint.
"""

import importlib
import json
import os
import threading
import shlex
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
import types

load_dotenv()

PROJECT_DIR = Path(os.path.expanduser("~/Documents/loneProjects/JaimeAgent"))
TASK_FILE = PROJECT_DIR / "tasks.json"
FEEDBACK_FILE = PROJECT_DIR / "user_feedback.txt"


def _parse_call(call: str):
    """
    Given a JSON string `call`, parse out the function name and args.
    Returns tuple: (name: str, args: dict)
    """
    payload = json.loads(call)
    return payload["name"], payload.get("arguments", {})


def dispatch_function(call: any) -> str:
    """
    Import handlers.<function_name> and invoke its `handle(**args)`.

    Returns:
        str – the handler’s return value (should already be serialisable).
    """
    name, args = _parse_call(call)

    # Dynamically import the corresponding module
    try:
        module: types.ModuleType = importlib.import_module(f"handlers.{name}")
    except ImportError:
        raise RuntimeError(f"Handler module for '{name}' not found")

    if not hasattr(module, "handle"):
        raise RuntimeError(f"Handler '{name}' missing 'handle' entrypoint")

    # Execute the handler
    result = module.handle(**args)

    # 4) Memory persistence for save_memory
    if name == "save_memory":
        with open(PROJECT_DIR / "session_memory.json", "a", encoding="utf-8") as memf:
            memf.write(json.dumps(args, ensure_ascii=False) + "\n")

    # Return JSON string if needed
    return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
