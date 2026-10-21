from app.rag.retriever import retrieve

query = "What did Rutherford propose about the atom?"

results = retrieve(query, top_k=3)

print("\nQuery:")
print(query)

print("\nResults:")

for i, result in enumerate(results, start=1):
    print(f"\n--- Result {i} ---")
    print("Chunk ID:", result["chunk_id"])
    print("Score:", result["score"])
    print("Page:", result["page"])
    print("Text:", result["text"])
