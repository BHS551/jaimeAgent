# vector_store.py
from pathlib import Path


def search_documents(query: str, top_k: int = 3) -> list[str]:
    """
    Naive semantic search: scan all .py files under the project root,
    return up to top_k snippets containing the query (case-insensitive).
    """
    results: list[str] = []
    # Normalize search term
    term = query.lower()

    # Search through all Python files
    for path in Path(".").rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        lower_text = text.lower()
        idx = lower_text.find(term)
        if idx != -1:
            # Extract a snippet around the match
            start = max(0, idx - 50)
            end = min(len(text), idx + len(term) + 50)
            snippet = text[start:end].replace("\n", " ").strip()
            results.append(f"{path}:{snippet}")

        if len(results) >= top_k:
            break

    return results
