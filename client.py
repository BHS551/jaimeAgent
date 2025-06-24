# client.py
import os
import json
import openai
from typing import List, Dict, Any, Optional

from config import OPENAI_API_KEY, MODEL_NAME
from prevalidations import PREVALIDATIONS
from function_schema import FUNCTIONS
from handlers.dispatch import dispatch_function
from handlers.append_json import append_json

# --------------------------------------------------------------------------- #
#  OpenAI setup
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
#  Low-level call that adds memory but does **not** execute function calls
# --------------------------------------------------------------------------- #
def handle_prompt_raw(prompt: str, context: Optional[str] = None):
    """Send one prompt to the LLM, log the exchange in memory, return the reply."""
    memory: List[Dict[str, Any]] = load_session_messages()

    # ----- build per-turn messages ---------------------------------------- #
    messages: List[Dict[str, Any]] = []
    if PREVALIDATIONS:
        messages.append(
            {
                "role": "system",
                "content": f"VALIDATION RULES:\n{json.dumps(PREVALIDATIONS)}",
            }
        )
    if context:
        messages.append({"role": "system", "content": context})

    user_msg = {"role": "user", "content": prompt}
    messages.append(user_msg)

    # Persist ONLY the new user message
    append_json(user_msg)

    # ----- call the model ------------------------------------------------- #
    try:
        # Preferred path: regions where `memory=` is already available
        resp = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            memory=memory,
            functions=FUNCTIONS,
            function_call="auto",
        )
    except TypeError:
        # Fallback: inject memory in a hidden system message
        hidden_memory = {"role": "system", "content": "<MEMORY>\n" + json.dumps(memory)}
        resp = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[hidden_memory] + messages,
            functions=FUNCTIONS,
            function_call="auto",
        )

    # Persist assistant reply (or tool call) in memory
    reply = resp.choices[0].message
    try:
        append_json(reply.model_dump())  # SDK ≥ 1.3
    except AttributeError:
        append_json(
            {
                "role": reply.role,
                "content": reply.content,
                "name": getattr(reply, "name", None),
                "tool_calls": getattr(reply, "tool_calls", None),
                "function_call": getattr(reply, "function_call", None),
            }
        )

    return reply


# --------------------------------------------------------------------------- #
#  High-level helper: validate, then execute any function calls
# --------------------------------------------------------------------------- #
def handle_prompt(prompt: str, context: Optional[str] = None) -> str:
    """Run a two-phase cycle: validation → execution (if any)."""
    # Phase 1 – validation
    val_msg = handle_prompt_raw(prompt, context)
    val_text = val_msg.content or ""

    # Phase 2 – execution
    memory = load_session_messages()
    exec_messages: List[Dict[str, Any]] = [
        {"role": "system", "content": f"VALIDATION RESULTS:\n{val_text}"}
    ]
    if context:
        exec_messages.append({"role": "system", "content": context})

    user_msg = {"role": "user", "content": prompt}
    exec_messages.append(user_msg)
    append_json(user_msg)  # store only the new message

    try:
        exec_resp = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=exec_messages,
            memory=memory,
            functions=FUNCTIONS,
            function_call="auto",
        )
    except TypeError:
        hidden_memory = {"role": "system", "content": "<MEMORY>\n" + json.dumps(memory)}
        exec_resp = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[hidden_memory] + exec_messages,
            functions=FUNCTIONS,
            function_call="auto",
        )

    msg = exec_resp.choices[0].message
    append_json(msg.model_dump() if hasattr(msg, "model_dump") else {
        "role": msg.role,
        "content": msg.content,
        "name": getattr(msg, "name", None),
        "tool_calls": getattr(msg, "tool_calls", None),
        "function_call": getattr(msg, "function_call", None),
    })

    # Dispatch any function call
    if getattr(msg, "function_call", None):
        result = dispatch_function(msg.function_call)
        append_json(
            {
                "role": "tool",
                "tool_call_id": msg.function_call.id
                if hasattr(msg.function_call, "id")
                else None,
                "content": result,
            }
        )
        return result

    return msg.content or "No action taken"
