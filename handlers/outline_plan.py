from client import handle_prompt_raw
import json

def handle(context: str, task_description: str):
    prompt = f"You are Jaime, a code assistant.\n\nContext:\n{context}\n\nYour task:\n{task_description}\n\nPlease output a numbered, step-by-step plan."
    resp = handle_prompt_raw(prompt, None)
    return resp.content or ''