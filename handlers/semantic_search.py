from vector_store import search_documents


def handle(query: str, top_k: int = 3):
    return search_documents(query, top_k)
