import importlib
import json

# Dynamically dispatch to handler modules based on function name
# Each handler should be in its own module named handler_<function_name>.py
# and expose a `handle(**kwargs)` function.
def dispatch_function(call) -> str:
    args = json.loads(call.arguments)
    func_name = call.name
    module_pkg = f"handlers.{func_name}"
    try:
        module = importlib.import_module(module_pkg)
        return module.handle(**args)
    except ImportError:
        return f"No handler module for function '{func_name}'"
    except AttributeError:
        return f"Handler '{func_name}' missing a 'handle' function"
    except Exception as e:
        return f"Error in handler '{func_name}': {e}"