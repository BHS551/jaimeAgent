#!/usr/bin/env python3
# jaime_agent.py

import os
import sys
import argparse
import time
import json
import logging
import subprocess
import threading
import shlex
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project directories and files
PROJECT_DIR = Path(os.path.expanduser("~/Documents/loneProjects/JaimeAgent"))
TASK_FILE = PROJECT_DIR / "tasks.json"
SESSION_MEMORY = PROJECT_DIR / "session_memory.json"
FEEDBACK_FILE = PROJECT_DIR / "user_feedback.txt"
FLOWS_FILE = PROJECT_DIR / "git_flows.json"
KNOWLEDGE_DIR = PROJECT_DIR / "knowledge"

# Ensure project directories exist
PROJECT_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

# Ensure import path when run from Startup folder
MODULE_DIR = os.path.expanduser("~/Documents/loneProjects/JaimeAgent/scripts")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

# Core imports for function-calling
from client import handle_prompt_raw, handle_prompt
from handlers.dispatch import dispatch_function

# Logging configuration
tlogger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(PROJECT_DIR / "jaime_agent.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
activity_handler = logging.FileHandler(
    PROJECT_DIR / "activity_log.txt", encoding="utf-8"
)
activity_handler.setLevel(logging.INFO)
activity_handler.setFormatter(
    logging.Formatter("%(asctime)s -> %(message)s", "%Y-%m-%d %H:%M:%S")
)
tlogger.addHandler(activity_handler)

# Stub for vector search (semantic_search enhancement)
try:
    from vector_store import search_documents
except ImportError:

    def search_documents(query, top_k=3):
        return []


# In-memory information flow log
info_flow_log = defaultdict(list)


def monitor_information_flow(func: str, data: str):
    info_flow_log[func].append(data)
    logging.debug(f"Flow: {func} -> {data}")


# Task and memory I/O
def load_tasks() -> list[dict]:
    try:
        return json.loads(TASK_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_tasks(tasks: list[dict]):
    TASK_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def load_session_memory() -> dict:
    try:
        entries = [
            json.loads(line)
            for line in SESSION_MEMORY.read_text(encoding="utf-8").splitlines()
        ]
        return {e["key"]: e["value"] for e in entries}
    except FileNotFoundError:
        return {}


# Generate context by combining snippets, memory, and reference docs
def build_context(user_input: str) -> str:
    parts = []
    # 1) semantic search snippets
    search_call = json.dumps(
        {"name": "semantic_search", "arguments": {"query": user_input, "top_k": 5}}
    )
    snippets = dispatch_function(search_call)
    try:
        snippets = json.loads(snippets)
    except json.JSONDecodeError:
        snippets = [snippets]
    parts.append("# Relevant Code Snippets:\n" + "\n".join(snippets))

    # 2) session memory
    memory = load_session_memory()
    if memory:
        mem_text = json.dumps(memory, indent=2)
        parts.append("# Remembered Facts:\n" + mem_text)

    # 3) reference knowledge files
    # optional: implement similar to load_reference_docs if needed

    return "\n\n".join(parts)


class JaimeAgent:
    def __init__(self):
        self.pending_plan = None

    def handle_prompt(self, user_input: str):
        """
        Entry point for user messages:
        - Build a rich context (snippets + memory)
        - Outline a plan
        - Ask user to confirm
        """
        context = build_context(user_input)

        # Outline plan
        plan_call = json.dumps(
            {
                "name": "outline_plan",
                "arguments": {"context": context, "task_description": user_input},
            }
        )
        outline = dispatch_function(plan_call)
        self.pending_plan = outline

        # Send plan for confirmation
        handle_prompt(
            text=outline,
            function_call={
                "name": "confirm_plan",
                "arguments": json.dumps({"plan": outline}),
            },
        )

    def handle_function_response(self, name: str, arguments: dict):
        """
        After plan confirmation or any function call.
        """
        if name == "confirm_plan":
            plan = arguments.get("plan", "")
            steps = plan.splitlines()
            # Execute steps
            for idx, step in enumerate(steps):
                # Save each step
                dispatch_function(
                    json.dumps(
                        {
                            "name": "save_memory",
                            "arguments": {"key": f"step_{idx}", "value": step},
                        }
                    )
                )
                # TODO: route step to specific handlers

            # Post-change validation
            test_res = dispatch_function(
                json.dumps(
                    {"name": "run_tests", "arguments": {"folder_path": str(Path.cwd())}}
                )
            )
            lint_res = dispatch_function(
                json.dumps(
                    {
                        "name": "run_linter",
                        "arguments": {"folder_path": str(Path.cwd())},
                    }
                )
            )
            summary = f"Test Results:\n{test_res}\n\nLint Warnings:\n{lint_res}"
            handle_prompt(text=summary)
        else:
            # Pass-through for other calls
            result = dispatch_function(
                json.dumps({"name": name, "arguments": arguments})
            )
            handle_prompt(text=str(result))


# Auto-loop for tasks.json


def run_auto_loop(ctx, interval):
    tasks = load_tasks()
    while tasks:
        task = tasks[0]
        steps = task.get("steps", [])
        idx = task.get("current_step", 0)
        if idx < len(steps):
            step = steps[idx]
            print(f"Executing {task['id']} step {idx+1}: {step}")
            # Process each step using handle_prompt_raw and enriched context
            resp = handle_prompt_raw(step, build_context(step))
            if getattr(resp, "function_call", None):
                # Always convert FunctionCall to JSON string for dispatch
                call_payload = json.dumps(
                    {
                        "name": resp.function_call.name,
                        "arguments": resp.function_call.arguments,
                    }
                )
                out = dispatch_function(call_payload)
                print(out)
                # Save memory for this step
                mem_payload = json.dumps(
                    {
                        "name": "save_memory",
                        "arguments": {"key": f"{task['id']}_step_{idx}", "value": step},
                    }
                )
                dispatch_function(mem_payload)
                # Post-change validation
                test_payload = json.dumps(
                    {"name": "run_tests", "arguments": {"folder_path": str(Path.cwd())}}
                )
                lint_payload = json.dumps(
                    {
                        "name": "run_linter",
                        "arguments": {"folder_path": str(Path.cwd())},
                    }
                )
                dispatch_function(test_payload)
                dispatch_function(lint_payload)
                task["current_step"] += 1
                save_tasks(tasks)
            else:
                print(resp.content or "")
        else:
            tasks.pop(0)
            save_tasks(tasks)
        time.sleep(interval)


# CLI entry point


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", "-p")
    p.add_argument("--interval", "-i", type=float, default=10.0)
    p.add_argument("--define-flow", nargs=2)
    p.add_argument("--run-flow")
    p.add_argument("--self-awareness", "-sa", action="store_true")
    p.add_argument("--feedback", "-f")
    args = p.parse_args()
    if args.run_flow:
        handle_run_flow(args)
    if args.define_flow:
        handle_define_flow(args)
    if args.feedback:
        handle_feedback(args)
    if args.self_awareness:
        print(evaluate_self_awareness())
        return
    if args.prompt:
        JaimeAgent().handle_prompt(args.prompt)
        return
    print("Starting auto-loop. Press Ctrl+C to exit.")
    run_auto_loop(None, args.interval)


if __name__ == "__main__":
    main()
