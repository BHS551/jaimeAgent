# client.py
import os
import json
import openai
import requests
import logging
from typing import List, Dict, Any, Optional

from config import OPENAI_API_KEY, MODEL_NAME, LLM_PROVIDER
from prevalidations import PREVALIDATIONS
from function_schema import FUNCTIONS
from handlers.dispatch import dispatch_function
from handlers.append_json import append_json

# --------------------------------------------------------------------------- #
#  LLM setup: choose provider based on config flag
# --------------------------------------------------------------------------- #
openai.api_key = OPENAI_API_KEY

# --------------------------------------------------------------------------- #
#  Session-memory helpers
# --------------------------------------------------------------------------- #
SESSION_PATH = os.path.join(os.path.dirname(__file__), "session_memory.json")

def _reset_session_file() -> None:
    """Overwrite session_memory.json with an empty list (clean start)."""
    with open(SESSION_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

# Clear memory *immediately at import time*
_reset_session_file()

def _ensure_session_file() -> None:
    """Create an empty list file if it does not yet exist."""
    if not os.path.exists(SESSION_PATH):
        with open(SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_session_messages() -> List[Dict[str, Any]]:
    """Return the flat list of memory messages (may be empty)."""
    _ensure_session_file()
    try:
        with open(SESSION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

# --------------------------------------------------------------------------- #
#  Helper to call the chosen LLM
# --------------------------------------------------------------------------- #
def _call_llm(payload: Dict[str, Any]) -> Any:
    """Route to DeepSeek locally—or on failure, log and fall back to OpenAI."""
    if LLM_PROVIDER == "deepseek":
        url = os.getenv("DEESEEK_URL", "http://localhost:8000/v1/chat/completions")
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"DeepSeek endpoint unreachable ({e}); falling back to OpenAI")
            # Prepare a clean payload for OpenAI
            payload_copy = payload.copy()
            payload_copy.pop("memory", None)
            return openai.chat.completions.create(**payload_copy)
    else:
        # OpenAI path also must not receive `memory` as a kwarg
        payload_copy = payload.copy()
        payload_copy.pop("memory", None)
        return openai.chat.completions.create(**payload_copy)

# --------------------------------------------------------------------------- #
#  Low-level call that adds memory but does **not** execute function calls
# --------------------------------------------------------------------------- #
def handle_prompt_raw(prompt: str, context: Optional[str] = None):
    """Send one prompt to the LLM, log the exchange in memory, return the reply."""
    memory: List[Dict[str, Any]] = load_session_messages()

    # ----- build per-turn messages ---------------------------------------- #
    messages: List[Dict[str, Any]] = []
    if PREVALIDATIONS:
        messages.append({
            "role": "system",
            "content": f"VALIDATION RULES:\n{json.dumps(PREVALIDATIONS)}",
        })
    if context:
        messages.append({"role": "system", "content": context})

    user_msg = {"role": "user", "content": prompt}
    messages.append(user_msg)

    # Persist ONLY the new user message
    append_json(user_msg)

    # ----- call the model ------------------------------------------------- #
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "functions": FUNCTIONS,
        "function_call": "auto"
    }
    # include memory only for OpenAI provider (DeepSeek may ignore)
    if LLM_PROVIDER != "deepseek":
        payload["memory"] = memory

    resp = _call_llm(payload)

    # Persist assistant reply (or tool call) in memory
    if isinstance(resp, dict):
        choice = resp["choices"][0]["message"]
        reply = choice
    else:
        reply = resp.choices[0].message

    try:
        # SDK ≥1.3
        append_json(reply.model_dump())
    except Exception:
        append_json({
            "role": getattr(reply, "role", None),
            "content": getattr(reply, "content", None),
            "name": getattr(reply, "name", None),
            "tool_calls": getattr(reply, "tool_calls", None),
            "function_call": getattr(reply, "function_call", None),
        })

    return reply

# --------------------------------------------------------------------------- #
#  High-level helper: validate, then execute any function calls
# --------------------------------------------------------------------------- #
def handle_prompt(prompt: str, context: Optional[str] = None) -> str:
    """Run a two-phase cycle: validation → execution (if any)."""
    # Phase 1 – validation
    val_msg = handle_prompt_raw(prompt, context)
    val_text = (val_msg.get("content") if isinstance(val_msg, dict)
                else val_msg.content or "")

    # Phase 2 – execution
    memory = load_session_messages()
    exec_messages: List[Dict[str, Any]] = [
        {"role": "system", "content": f"VALIDATION RESULTS:\n{val_text}"}
    ]
    if context:
        exec_messages.append({"role": "system", "content": context})

    user_msg = {"role": "user", "content": prompt}
    exec_messages.append(user_msg)
    append_json(user_msg)

    payload = {
        "model": MODEL_NAME,
        "messages": exec_messages,
        "functions": FUNCTIONS,
        "function_call": "auto"
    }
    if LLM_PROVIDER != "deepseek":
        payload["memory"] = memory

    exec_resp = _call_llm(payload)

    if isinstance(exec_resp, dict):
        msg = exec_resp["choices"][0]["message"]
    else:
        msg = exec_resp.choices[0].message

    append_json(
        msg.model_dump() if hasattr(msg, "model_dump") else {
            "role": getattr(msg, "role", None),
            "content": getattr(msg, "content", None),
            "name": getattr(msg, "name", None),
            "tool_calls": getattr(msg, "tool_calls", None),
            "function_call": getattr(msg, "function_call", None),
        }
    )

    # Dispatch any function call
    function_call = (msg.get("function_call") if isinstance(msg, dict)
                     else getattr(msg, "function_call", None))
    if function_call:
        result = dispatch_function(function_call)
        append_json({
            "role": "tool",
            "tool_call_id": (function_call.get("id") if isinstance(function_call, dict)
                             else getattr(function_call, "id", None)),
            "content": result,
        })
        return result

    return (msg.get("content") if isinstance(msg, dict)
            else msg.content or "No action taken")
import glob

knowledge_files = glob.glob('./knowledge/*.txt')
for file in knowledge_files:
    with open(file, 'r') as f:
        knowledge = f.read()
        # Process knowledge as needed
