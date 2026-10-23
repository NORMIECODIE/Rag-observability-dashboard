
from app.rag.embeddings import create_embedding
from app.rag.vector_store import search


def retrieve(
    query: str,
    top_k: int = 3,
    score_threshold: float = 0.65,
    query_vector: list[float] | None = None,
) -> list[dict]:

    if query_vector is None:
        query_vector = create_embedding(query)

    results = search(query_vector, top_k=top_k)

    print(f"\n[RETRIEVAL DEBUG] Query: {query}")
    print(f"[RETRIEVAL DEBUG] Results returned by search: {len(results)}")

    for result in results:
        print(
            f"[RETRIEVAL DEBUG] score={result.score:.4f}, "
            f"page={result.payload.get('page')}, "
            f"text={result.payload.get('text', '')[:100]!r}"
        )

    filtered_results = [
        {
            "chunk_id": r.id,
            "document": r.payload.get("document_id"),
            "text": r.payload["text"],
            "score": r.score,
            "page": r.payload["page"],
        }
        for r in results
        if r.score >= score_threshold
        and isinstance(r.payload.get("text"), str)
        and r.payload["text"].strip()
    ]

    print(
        f"[RETRIEVAL DEBUG] Results retained at threshold "
        f"{score_threshold}: {len(filtered_results)}"
    )

    return filtered_results
