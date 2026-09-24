from app.rag.embeddings import create_embedding
from app.rag.vector_store import search

def retrieve(query: str, top_k: int = 5) -> list[dict]:

    vector = create_embedding(query)

    results = search(
        vector,
        top_k= top_k
    )

    return [
        {
            "chunk_id": r.id,
            "text": r.payload["text"],
            "score": r.score,
            "page": r.payload["page"],
        }
        for r in results
    ]