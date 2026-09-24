from app.rag.retriever import retrieve


query = "What are common NLP tasks?"


results = retrieve(
    query,
    top_k=3
)


print("\nQuery:")

print(query)

print("\nRetrieved Results:")


for i, result in enumerate(results, start=1):

    print("\n" + "=" * 60)


    print("Result:", i)
    print("Chunk ID:", result["chunk_id"])
    print("Score:", result["score"])
    print("Page:", result["page"])

    print("\nText:")
    print(result["text"])