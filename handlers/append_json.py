# handlers/append_json.py
"""Persist conversation memory as a *flat list* of messages.

Each call stores **exactly one** message dict, so the on-disk file stays small
and easy to diff.  The file lives at project_root/session_memory.json.

Add your own locking/rotation if you later share this file across processes.
"""

import json
import os
from typing import Dict, Any

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.normpath(os.path.join(HERE, "../session_memory.json"))


def append_json(message: Any) -> None:
    """Append *one* message to session_memory.json."""
    if not isinstance(message, dict):
        raise TypeError("append_json expects a dict message")

    # Load (or initialise) the flat list
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
    except FileNotFoundError:
        data = []

    data.append(message)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
