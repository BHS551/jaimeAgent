
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

load_dotenv()

# Project directories and files
PROJECT_DIR = Path(os.path.expanduser("~/Documents/loneProjects/JaimeAgent"))
TASK_FILE = PROJECT_DIR / "tasks.json"
FEEDBACK_FILE = PROJECT_DIR / "user_feedback.txt"
DECISION_IMPACT_FILE = PROJECT_DIR / "decision_impact_analysis.txt"
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

# Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_DIR / "jaime_agent.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
activity_handler = logging.FileHandler(PROJECT_DIR / "activity_log.txt", encoding="utf-8")
activity_handler.setLevel(logging.INFO)
activity_handler.setFormatter(
    logging.Formatter("%(asctime)s -> %(message)s", "%Y-%m-%d %H:%M:%S")
)
logging.getLogger().addHandler(activity_handler)

# Stub for vector search
try:
    from vector_store import search_documents
except ImportError:
    def search_documents(query, top_k=3):
        return []

info_flow_log = defaultdict(list)
def monitor_information_flow(func: str, data: str):
    info_flow_log[func].append(data)
    logging.debug(f"Flow: {func} -> {data}")

# Task I/O

def load_tasks() -> list[dict]:
    try:
        return json.loads(TASK_FILE.read_text(encoding='utf-8'))
    except FileNotFoundError:
        logging.info("No tasks.json found, starting empty")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Failed parsing tasks.json: {e}")
        return []


def save_tasks(tasks: list[dict]):
    try:
        TASK_FILE.write_text(json.dumps(tasks, indent=2), encoding='utf-8')
        logging.info(f"Tasks saved ({len(tasks)} remaining)")
    except Exception as e:
        logging.error(f"Failed writing tasks.json: {e}")

# Document cache

@lru_cache(maxsize=1)
def load_reference_docs(objective: str) -> str:
    parts = []
    for doc in search_documents(objective):
        full = PROJECT_DIR / Path(doc).name
        if full.exists():
            try:
                text = full.read_text(encoding='utf-8')
                parts.append(f"== {full.name} ==\n{text}")
                monitor_information_flow("load_reference_docs", full.name)
            except Exception:
                logging.error(f"Error reading {full}")
    
    # Load all .txt files from the knowledge directory
    for txt_file in KNOWLEDGE_DIR.glob("*.txt"):
        try:
            text = txt_file.read_text(encoding='utf-8')
            parts.append(f"== {txt_file.name} ==\n{text}")
            monitor_information_flow("load_reference_docs", txt_file.name)
        except Exception:
            logging.error(f"Error reading {txt_file}")

    return "\n\n".join(parts)

# Git flows

def load_flows() -> dict:
    if FLOWS_FILE.exists():
        try:
            return json.loads(FLOWS_FILE.read_text(encoding='utf-8'))
        except Exception:
            logging.error("Failed loading git_flows.json")
    return {}


def save_flows(flows: dict):
    try:
        FLOWS_FILE.write_text(json.dumps(flows, indent=2), encoding='utf-8')
        logging.info("Git flows saved")
    except Exception:
        logging.error("Failed writing git_flows.json")

# Handlers for CLI modes

def handle_define_flow(args):
    flows = load_flows()
    flows[args.define_flow[0]] = [c.strip() for c in args.define_flow[1].split(';')]
    save_flows(flows)
    print(f"Defined flow '{args.define_flow[0]}' with {len(flows[args.define_flow[0]])} cmds")


def handle_run_flow(args):
    flows = load_flows()
    name = args.run_flow
    if name not in flows:
        print(f"[!] Flow '{name}' not found.")
        sys.exit(1)
    for cmd in flows[name]:
        logging.info(f"GIT FLOW {name}: {cmd}")
        parts = shlex.split(cmd)
        try:
            out = subprocess.run(parts, cwd=PROJECT_DIR, check=True, capture_output=True, text=True)
            print(out.stdout)
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            sys.exit(1)
    sys.exit(0)


def handle_feedback(args):
    FEEDBACK_FILE.write_text(args.feedback + '\n', encoding='utf-8')
    print("[INFO] Feedback saved.")
    sys.exit(0)


def handle_self_awareness():
    print(evaluate_self_awareness())
    sys.exit(0)


def handle_one_shot(args, ctx):
    msg = handle_prompt_raw(args.prompt, ctx)
    if getattr(msg, 'function_call', None):
        print("⚠️ Function call skipped.")
    else:
        print(msg.content or '')
    sys.exit(0)

# Self-awareness logic

def evaluate_self_awareness() -> str:
    report = ['Self-Awareness Report:','1. Tasks:']
    for t in load_tasks():
        cs = t.get('current_step',0)
        ls = len(t.get('steps',[]))
        report.append(f"- {t['id']} -> {cs}/{ls}")
    report.append('Status: OK')
    return "\n".join(report)

# Main auto-loop

def run_auto_loop(ctx, interval):
    tasks = load_tasks()
    stop_event = threading.Event()
    while not stop_event.wait(interval):
        if not tasks:
            print("No tasks. Add to tasks.json.")
            break
        task = tasks[0]
        idx = task.get('current_step',0)
        steps = task.get('steps',[])
        if idx >= len(steps):
            tasks.pop(0)
            save_tasks(tasks)
            continue
        prompt = f"{load_reference_docs(task['id'])}\nTask {task['id']} step {idx+1}/{len(steps)}: {steps[idx]}"
        resp = handle_prompt_raw(prompt, ctx)
        if getattr(resp,'function_call',None):
            result = dispatch_function(resp.function_call)
            print(result)
            if isinstance(result,str) and result.startswith('❌'):
                logging.error(f"{task['id']} failed at step {idx+1}")
                break
            task['current_step'] = idx+1
            save_tasks(tasks)
        else:
            print(resp.content or '')

# Entry point

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prompt','-p')
    p.add_argument('--context-file','-c')
    p.add_argument('--interval','-i',type=float,default=10.0)
    p.add_argument('--define-flow',nargs=2)
    p.add_argument('--run-flow')
    p.add_argument('--self-awareness','-sa',action='store_true')
    p.add_argument('--feedback','-f')
    args = p.parse_args()
    ctx = None
    if args.context_file:
        ctx = Path(args.context_file).read_text(encoding='utf-8')
    if args.define_flow: handle_define_flow(args)
    if args.run_flow:   handle_run_flow(args)
    if args.feedback:   handle_feedback(args)
    if args.self_awareness: handle_self_awareness()
    if args.prompt:     handle_one_shot(args,ctx)
    print("Jaime Agent CLI - type 'exit' to quit.")
    run_auto_loop(ctx, args.interval)

if __name__=='__main__':
    main()