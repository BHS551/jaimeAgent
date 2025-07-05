import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parents[1]
SESSION_MEMORY = PROJECT_DIR / 'session_memory.json'

def handle(key: str):
    try:
        for line in SESSION_MEMORY.read_text(encoding='utf-8').splitlines():
            entry = json.loads(line)
            if entry.get('key') == key:
                return entry.get('value')
    except FileNotFoundError:
        pass
    return None