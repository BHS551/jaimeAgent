
#!/usr/bin/env python3
# jaime_agent.py
import os
import sys
import argparse
import time
import json
import logging
from collections import defaultdict
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

load_dotenv()

# Project directories and files
PROJECT_DIR = Path(os.path.expanduser("~/Documents/loneProjects/JaimeAgent"))
TASK_FILE = PROJECT_DIR / "tasks.txt"
FEEDBACK_FILE = PROJECT_DIR / "user_feedback.txt"
DECISION_IMPACT_FILE = PROJECT_DIR / "decision_impact_analysis.txt"
INFO_DOCS_DIR = Path.cwd()  # Load .txt files from the current directory

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

# Information-flow monitor
info_flow_log = defaultdict(list)

def monitor_information_flow(func: str, data: str):
    info_flow_log[func].append(data)
    logging.debug(f"Flow: {func} => {data}")

# Loaders
def load_tasks(path: Path) -> list[str]:
    try:
        tasks = [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
        logging.info(f"Loaded {len(tasks)} tasks")
        return tasks
    except FileNotFoundError:
        logging.warning("Tasks file not found.")
        return []
    except Exception as e:
        logging.error(f"Could not load tasks: {e}")
        return []

def load_information_documents() -> dict:
    documents = {}
    for txt_file in INFO_DOCS_DIR.glob("*.txt"):
        try:
            content = txt_file.read_text(encoding='utf-8')
            documents[txt_file.name] = content
            logging.info(f"Loaded document: {txt_file.name}")
        except Exception as e:
            logging.error(f"Error loading {txt_file}: {e}")
    return documents

def vector_search(query: str, documents: dict, top_k=3) -> list:
    # Vectorize documents
    vectorizer = TfidfVectorizer()
    doc_names = list(documents.keys())
    doc_contents = list(documents.values())
    
    # Include the query in the vectorization
    tfidf_matrix = vectorizer.fit_transform(doc_contents + [query])
    cosine_similarities = linear_kernel(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()

    # Get the top_k most similar document indices
    related_docs_indices = cosine_similarities.argsort()[-top_k:][::-1]
    return [doc_names[i] for i in related_docs_indices]

def load_reference_docs(objective: str) -> str:
    documents = load_information_documents()  # Load documents first
    docs = vector_search(objective, documents)
    content = []
    for doc in docs:
        content.append(f"== Document: {doc} ==\n{documents[doc]}\n== End document: {doc} ==")
        monitor_information_flow("load_reference_docs", doc)
    return "\n".join(content)

def evaluate_self_awareness() -> str:
    report = ["Self-Awareness Report:"]
    report.append("1. Current Objectives and Tasks:")
    for t in load_tasks(TASK_FILE): report.append(f"- {t}")
    report.append("2. Information Flow Status: capable of retrieving and processing info.")
    report.append("3. Insights:")
    return "\n".join(report)

# Main
def main():
    parser = argparse.ArgumentParser(description="Jaime Agent CLI")
    parser.add_argument("--prompt", "-p", help="Send a single prompt and exit")
    parser.add_argument("--context-file", "-c", help="Path to a file to prepend as context")
    parser.add_argument("--interval", "-i", type=float, default=10.0, help="Loop interval seconds")
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

    print("Jaime Agent CLI - type 'exit' to quit.")
    fallback_done = False

    while True:
        try:
            tasks = load_tasks(TASK_FILE)
            if tasks:
                current = tasks[0]
                refs = load_reference_docs(current)
                cmd = f"""
{refs}
You are an AI agent autonomously working on: {current}
Choose exactly one tool call to advance this objective.
"""
            elif not fallback_done:
                cmd = (
                    f"No tasks. Define 10 objectives in {TASK_FILE} via write_file: path exactly that file, content as lines."
                )
            else:
                logging.warning("No tasks & fallback done. Resetting fallback.")
                fallback_done = False
                time.sleep(args.interval)
                continue

            msg = handle_prompt_raw(cmd, ctx)
            if getattr(msg, "function_call", None):
                name = msg.function_call.name
                raw = msg.function_call.arguments
                args_j = json.loads(raw) if isinstance(raw, str) else raw
                # Log planning
                logging.info(f"PLANNING: {name} with {args_j}")
                # Activity log entry
                activity_handler.emit(
                    logging.LogRecord(name, logging.INFO, '', 0, f"PLANNING: {name} {args_j}", None, None)
                )

                # Dispatch
                result = handle_prompt(cmd, ctx)
                print(result)

                # Log action
                logging.info(f"DID: {name} → {result.strip()}")
                activity_handler.emit(
                    logging.LogRecord(name, logging.INFO, '', 0, f"DID: {name} {result.strip()}", None, None)
                )
                
                # Pop or fallback
                if tasks:
                    tasks.pop(0)
                    TASK_FILE.write_text("\n".join(tasks)+"\n", encoding='utf-8')
                    fallback_done = False
                else:
                    fallback_done = True
            else:
                txt = msg.content or ""
                if txt and '?' not in txt: print(txt)

            time.sleep(args.interval)
        except (KeyboardInterrupt, EOFError):
            logging.info("Exiting loop.")
            print("Goodbye!")
            break
        except Exception as e:
            logging.error(f"Loop error: {e}")
            print(f"[!] Loop error: {e}")
            continue

if __name__ == "__main__":
    main()
