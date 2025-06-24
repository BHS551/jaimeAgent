import os
import openai
from config import OPENAI_API_KEY, MODEL_NAME

openai.api_key = OPENAI_API_KEY

def handle(path: str, instructions: str) -> str:
    """
    Reads the file at `path`, asks the LLM to apply `instructions`
    to its contents, then writes back the updated file.
    """
    # Resolve and read
    expanded = os.path.expanduser(path)
    if not os.path.isfile(expanded):
        return f"Error: file not found: {expanded}"
    with open(expanded, "r", encoding="utf-8") as f:
        original = f.read()

    # Ask the model to produce the updated file
    prompt = (
        "Here is the original file content:\n"
        "```\n" + original + "\n```\n\n"
        "Apply the following instructions to transform the file:\n"
        + instructions +
        "\n\n"
        "Return the full, updated file content only."
    )
    resp = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role":"user","content":prompt}]
    )
    updated = resp.choices[0].message.content

    # Overwrite the file
    with open(expanded, "w", encoding="utf-8") as f:
        f.write(updated)

    return f"Smart‐modified {expanded}"
