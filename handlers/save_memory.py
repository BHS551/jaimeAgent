import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parents[1]
SESSION_MEMORY = PROJECT_DIR / 'session_memory.json'

def handle(key: str, value):
    entry = {'key': key, 'value': value}
    with open(SESSION_MEMORY, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return 'OK'