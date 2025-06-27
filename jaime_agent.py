#!/usr/bin/env python3
# jaime_agent.py
import os
import sys
import argparse
import time
import json
import logging
import subprocess
from collections import defaultdict
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project directories and files
PROJECT_DIR = Path(os.path.expanduser("~/Documents/loneProjects/JaimeAgent"))
TASK_FILE = PROJECT_DIR / "tasks.json"
FEEDBACK_FILE = PROJECT_DIR / "user_feedback.txt"
DECISION_IMPACT_FILE = PROJECT_DIR / "decision_impact_analysis.txt"
FLOWS_FILE = PROJECT_DIR / "git_flows.json"

# Ensure project directories exist
PROJECT_DIR.mkdir(parents=True, exist_ok=True)

# Ensure import path when run from Startup folder
MODULE_DIR = os.path.expanduser("~/Documents/loneProjects/JaimeAgent/scripts")
if os.path.isdir(MODULE_DIR) and MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

# Core imports for function-calling
from client import handle_prompt_raw, handle_prompt
from handlers.dispatch import dispatch_function

# Configure core logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_DIR / "jaime_agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
# Human-readable activity log
ACTIVITY_LOG = PROJECT_DIR / "activity_log.txt"
activity_handler = logging.FileHandler(ACTIVITY_LOG, encoding="utf-8")
activity_handler.setLevel(logging.INFO)
activity_handler.setFormatter(
    logging.Formatter("%(asctime)s → %(message)s", "%Y-%m-%d %H:%M:%S")
)
logging.getLogger().addHandler(activity_handler)

# Optional vector store client (stub)
try:
    from vector_store import search_documents
except ImportError:
    def search_documents(query, top_k=3):
        return []

# Information-flow monitor
info_flow_log = defaultdict(list)

def monitor_information_flow(func: str, data: str):
    info_flow_log[func].append(data)
    logging.debug(f"Flow: {func} => {data}")

# Load and save tasks in JSON with steps

def load_tasks() -> list[dict]:
    try:
        return json.loads(TASK_FILE.read_text(encoding='utf-8'))
    except FileNotFoundError:
        logging.info("No tasks file found, starting with empty task list.")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing tasks.json: {e}")
        return []


def save_tasks(tasks: list[dict]):
    try:
        TASK_FILE.write_text(json.dumps(tasks, indent=2), encoding='utf-8')
        logging.info(f"Saved {len(tasks)} tasks to tasks.json")
    except Exception as e:
        logging.error(f"Error saving tasks.json: {e}")

# Load reference docs

def load_reference_docs(objective: str) -> str:
    docs = []
    try:
        docs = search_documents(objective)
    except Exception:
        logging.debug("Vector search failed")
    content = []
    loaded = set()
    for doc in docs:
        full = PROJECT_DIR / Path(os.path.expanduser(doc)).name
        if full.exists() and full.suffix == '.txt':
            try:
                text = full.read_text(encoding='utf-8')
                content.append(f"== {full.name} ==\n{text}")
                monitor_information_flow("load_reference_docs", full.name)
                loaded.add(full.name)
            except Exception as e:
                logging.error(f"Error loading {full}: {e}")
    for txt in PROJECT_DIR.glob("*.txt"):
        if txt.name in loaded or txt.name in {FEEDBACK_FILE.name, DECISION_IMPACT_FILE.name, ACTIVITY_LOG.name, 'jaime_agent.log'}:
            continue
        try:
            text = txt.read_text(encoding='utf-8')
            content.append(f"== {txt.name} ==\n{text}")
            monitor_information_flow("load_reference_docs", txt.name)
        except Exception as e:
            logging.error(f"Error loading {txt}: {e}")
    return "\n\n".join(content)

# Self-awareness

def evaluate_self_awareness() -> str:
    report = ["Self-Awareness Report:"]
    report.append("1. Current Tasks and Steps:")
    tasks = load_tasks()
    for t in tasks:
        cs = t.get('current_step', 0)
        steps = t.get('steps', [])
        report.append(f"- {t.get('id')} → step {cs}/{len(steps)}")
    report.append("2. Information Flow Status: OK")
    report.append("3. Insights loaded from docs.")
    return "\n".join(report)

# Git flow persistence

def load_flows() -> dict:
    if FLOWS_FILE.exists():
        try:
            return json.loads(FLOWS_FILE.read_text(encoding='utf-8'))
        except Exception as e:
            logging.error(f"Error loading flows: {e}")
    return {}


def save_flows(flows: dict):
    try:
        FLOWS_FILE.write_text(json.dumps(flows, indent=2), encoding='utf-8')
        logging.info("Git flows saved.")
    except Exception as e:
        logging.error(f"Error saving flows: {e}")

# Main loop

def main():
    parser = argparse.ArgumentParser(description="Jaime Agent CLI")
    parser.add_argument("--prompt", "-p", help="Send a single prompt and exit")
    parser.add_argument("--context-file", "-c", help="Path to prepend as context")
    parser.add_argument("--interval", "-i", type=float, default=10.0, help="Loop interval seconds")
    parser.add_argument("--define-flow", nargs=2, metavar=("NAME","CMDS"), help="Define a named git flow; CMDS is semicolon-separated commands")
    parser.add_argument("--run-flow", help="Run a named git flow")
    parser.add_argument("--self-awareness", "-sa", action="store_true", help="Generate self-awareness report")
    parser.add_argument("--feedback", "-f", help="Provide feedback to the agent")
    args = parser.parse_args()

    # Load optional context
    ctx = None
    if args.context_file:
        try:
            ctx = Path(os.path.expanduser(args.context_file)).read_text(encoding='utf-8')
            logging.info(f"Context loaded from {args.context_file}")
        except Exception as e:
            logging.error(f"Error loading context: {e}")
            sys.exit(1)

    # Define a git flow
    if args.define_flow:
        name, cmds = args.define_flow
        flows = load_flows()
        flows[name] = [c.strip() for c in cmds.split(";") if c.strip()]
        save_flows(flows)
        print(f"Defined flow '{name}' with {len(flows[name])} commands.")
        sys.exit(0)

    # Run a git flow
    if args.run_flow:
        flows = load_flows()
        if args.run_flow not in flows:
            print(f"[!] Flow '{args.run_flow}' not found.")
            sys.exit(1)
        print(f"Running flow '{args.run_flow}':")
        for cmd in flows[args.run_flow]:
            logging.info(f"GIT FLOW '{args.run_flow}': executing: {cmd}")
            activity_handler.emit(logging.LogRecord("git_flow", logging.INFO, '', 0, f"FLOW {args.run_flow}: {cmd}", None, None))
            try:
                res = subprocess.run(cmd, cwd=PROJECT_DIR, shell=True, check=True, capture_output=True, text=True)
                print(res.stdout)
                logging.info(f"GIT FLOW '{args.run_flow}': succeeded")
                activity_handler.emit(logging.LogRecord("git_flow", logging.INFO, '', 0, f"DONE {cmd}", None, None))
            except subprocess.CalledProcessError as e:
                print(e.stderr)
                logging.error(f"GIT FLOW '{args.run_flow}': failed {e}")
                sys.exit(1)
        sys.exit(0)

    # Feedback mode
    if args.feedback:
        FEEDBACK_FILE.write_text(args.feedback + "\n", encoding='utf-8')
        logging.info("User feedback appended.")
        print("[INFO] Feedback received.")
        sys.exit(0)

    # Self-awareness mode
    if args.self_awareness:
        print(evaluate_self_awareness())
        sys.exit(0)

    # One-shot prompt mode
    if args.prompt:
        msg = handle_prompt_raw(args.prompt, ctx)
        if getattr(msg, "function_call", None): print("⚠️ Function call skipped.")
        else: print(msg.content or "")
        sys.exit(0)

    # Automatic loop
    print("Jaime Agent CLI - type 'exit' to quit.")
    fallback_done = False
    while True:
        try:
            tasks = load_tasks()
            if tasks:
                task = tasks[0]
                step_idx = task.get("current_step", 0)
                steps = task.get("steps", [])
                if step_idx < len(steps):
                    step_desc = steps[step_idx]
                    cmd = f"""
{load_reference_docs(task.get('id', ''))}
You are working on task '{task['id']}', step {step_idx+1}/{len(steps)}:
{step_desc}

Choose one tool call to advance this step.
"""
                    msg = handle_prompt_raw(cmd, ctx)
                    if getattr(msg, "function_call", None):
                        name = msg.function_call.name
                        raw = msg.function_call.arguments
                        args_j = json.loads(raw) if isinstance(raw, str) else raw
                        logging.info(f"PLANNING: {name} {args_j}")
                        result = dispatch_function(msg.function_call)
                        print(result)
                        logging.info(f"DID: {name} → {result.strip()}")
                        # mark step done
                        task['current_step'] = step_idx + 1
                        if task['current_step'] >= len(steps):
                            tasks.pop(0)
                        save_tasks(tasks)
                        fallback_done = False
                    else:
                        txt = msg.content or ""
                        if txt and '?' not in txt:
                            print(txt)
                else:
                    # no steps left, drop task
                    tasks.pop(0)
                    save_tasks(tasks)
            elif not fallback_done:
                print(f"No tasks. Define tasks in {TASK_FILE} as JSON list of {{id,steps,current_step}}.")
                fallback_done = True
            else:
                logging.warning("No tasks & fallback done. Resetting.")
                fallback_done = False
            time.sleep(args.interval)
        except (KeyboardInterrupt, EOFError):
            logging.info("Exiting.")
            print("Goodbye!")
            break
        except Exception as e:
            logging.error(f"Loop error: {e}")
            print(f"[!] Loop error: {e}")
            continue

if __name__ == "__main__":
    main()
