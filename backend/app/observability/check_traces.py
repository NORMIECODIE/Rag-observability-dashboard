
from app.observability.mongodb import traces_collection


def main():
    print("Database:", traces_collection.database.name)
    print("Collection:", traces_collection.name)

    print("\nSearching for the latest trace...")

    trace = traces_collection.find_one(
        sort=[("_id", -1)]
    )

    if not trace:
        print("\nNo traces found.")
        return

    # Find the individual spans by name.
    spans = trace.get("spans", [])

    embedding = next(
        (s for s in spans if s.get("name") == "embedding"), {}
    )
    retrieval = next(
        (s for s in spans if s.get("name") == "retrieval"), {}
    )
    generation = next(
        (s for s in spans if s.get("name") == "generation"), {}
    )

    print("\n" + "=" * 50)
    print("RAG TRACE DETAILS")
    print("=" * 50)

    print("Trace ID:", trace.get("trace_id"))
    print("Question:", trace.get("question"))
    print("Status:", trace.get("status"))
    print("Created at:", trace.get("created_at"))
    print("Total latency:", trace.get("total_latency_ms"), "ms")

    print("\nANSWER")
    print("-" * 50)
    print(trace.get("answer", "No answer saved"))

    print("\nLATENCY BREAKDOWN")
    print("-" * 50)

    for name, span in [
        ("Embedding", embedding),
        ("Retrieval", retrieval),
        ("Generation", generation),
    ]:
        print(
            f"{name}: {span.get('duration_ms', 'N/A')} ms"
            f" | Status: {span.get('status', 'N/A')}"
        )

    print("\nTOKEN USAGE")
    print("-" * 50)
    print("Provider:", generation.get("provider", "N/A"))
    print("Model:", generation.get("model", "N/A"))
    print("Input tokens:", generation.get("input_tokens", "N/A"))
    print("Output tokens:", generation.get("output_tokens", "N/A"))
    print("Total tokens:", generation.get("total_tokens", "N/A"))

    cost = generation.get("estimated_cost_usd")

    print("\nESTIMATED COST")
    print("-" * 50)

    if cost is not None:
        print(f"${cost:.7f} USD")
    else:
        print("Cost data not available for this trace.")

    retrieved_chunks = retrieval.get("result", [])

    print("\nRETRIEVAL DETAILS")
    print("-" * 50)
    print("Top K:", retrieval.get("top_k", "N/A"))
    print("Chunks retrieved:", len(retrieved_chunks))

    for index, chunk in enumerate(retrieved_chunks, start=1):
        print(
            f"{index}. Score: {chunk.get('score', 'N/A')} "
            f"| Page: {chunk.get('page', 'N/A')} "
            f"| Document: {chunk.get('document', 'N/A')}"
        )

    print("\n" + "=" * 50)

    print("\nRAW RETRIEVAL SPAN")
    print(retrieval)


if __name__ == "__main__":
    main()