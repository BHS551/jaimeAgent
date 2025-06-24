# handlers/dispatch.py
"""
Dynamic dispatcher that loads a handler module matching the function name
and calls its `handle(**kwargs)`.

* Accepts either an OpenAI FunctionCall object **or** a plain dict
  { "name": str, "arguments": str|dict }.
* Produces crystal-clear error messages to aid debugging.
"""

from __future__ import annotations

import importlib
import json
import types
from typing import Any


def _parse_call(call: Any) -> tuple[str, dict]:
    """
    Normalise OpenAI FunctionCall or dict → (name, arguments_dict)
    """
    if hasattr(call, "name"):  # OpenAI FunctionCall
        name = call.name
        raw_args = call.arguments
    else:  # assume plain dict
        name = call["name"]
        raw_args = call["arguments"]

    if isinstance(raw_args, str):
        try:
            args = json.loads(raw_args) if raw_args else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in arguments: {e}") from None
    elif isinstance(raw_args, dict):
        args = raw_args
    else:
        raise TypeError(f"Unexpected type for arguments: {type(raw_args)}")

    return name, args


def dispatch_function(call: Any) -> str:
    """
    Import handlers.<function_name> and invoke its `handle(**args)`.

    Returns:
        str – the handler’s return value (should already be serialisable).
    """
    name, args = _parse_call(call)

    try:
        module: types.ModuleType = importlib.import_module(f"handlers.{name}")
    except ModuleNotFoundError as e:
        return f"❌ No handler module found for function '{name}'. " \
               f"Expected file: handlers/{name}.py – {e}"
    except Exception as e:
        return f"❌ Import error for handler '{name}': {e}"

    if not hasattr(module, "handle"):
        return f"❌ Handler module '{name}' exists but has no `handle()` function."

    try:
        result = module.handle(**args)
    except TypeError as e:
        return f"❌ Argument mismatch in handler '{name}': {e}"
    except Exception as e:
        return f"❌ Error inside handler '{name}': {e}"

    # Convert non-string returns to JSON strings so the LLM sees something usable
    return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
