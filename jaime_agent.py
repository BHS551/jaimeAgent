#!/usr/bin/env python3
# jaime_agent.py
import os
import sys
import argparse

from dotenv import load_dotenv
load_dotenv()

# Ensure import path when run from Startup folder
MODULE_DIR = os.path.expanduser("~/Documents/loneProjects/JaimeAgent/scripts")
if os.path.isdir(MODULE_DIR) and MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from client import handle_prompt_raw, handle_prompt
from handlers.dispatch import dispatch_function

def main():
    parser = argparse.ArgumentParser(description="Jaime Agent CLI")
    parser.add_argument("--prompt", "-p", help="Send a single prompt and exit")
    parser.add_argument("--context-file", "-c",
                        help="Optional path to a file whose contents get prepended as context")
    args = parser.parse_args()

    # Load context file if provided
    ctx = None
    if args.context_file:
        try:
            with open(os.path.expanduser(args.context_file), 'r', encoding='utf-8') as f:
                ctx = f.read()
        except Exception as e:
            print(f"[!] Could not load context file: {e}", file=sys.stderr)

    # One-shot mode: show plain-text or preview function_call but do not execute
    if args.prompt:
        msg = handle_prompt_raw(args.prompt, ctx)
        if hasattr(msg, "function_call") and msg.function_call:
            print("⚠️ Function call skipped in one-shot mode.")
        else:
            print(msg.content or "")
        sys.exit(0)

    # Interactive REPL with preview → confirm → execute
    print("Jaime Agent CLI - type 'exit' or Ctrl+C to quit")
    while True:
        try:
            cmd = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not cmd or cmd.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        # Phase 1: ask what Jaime plans to do
        msg = handle_prompt_raw(cmd, ctx)

        if hasattr(msg, "function_call") and msg.function_call:
            name = msg.function_call.name
            args_json = msg.function_call.arguments
            print(f"\n⚠️ Jaime will execute `{name}` with arguments:\n{args_json}\n")
            yn = input("Proceed? (y/N) ").strip().lower()
            if yn.startswith("y"):
                # Phase 2: actually run it (includes validations)
                result = handle_prompt(cmd, ctx)
                print(result)
            else:
                print("🚫 Operation cancelled.")
        else:
            # No function: show assistant reply (already includes validations)
            print(msg.content or "")

if __name__ == "__main__":
    main()
