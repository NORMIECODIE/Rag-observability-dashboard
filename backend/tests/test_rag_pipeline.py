from app.rag.pipeline import run_rag


question = input("Enter your question: ")

result = run_rag(question)

print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)
print(result["answer"])

print("\n" + "=" * 60)
print("SOURCES")
print("=" * 60)


for i, source in enumerate(result["sources"], start = 1):


    print(f"\n Source {i}")
    print("Chunk ID:", source["chunk_id"])
    print("Source:", source["score"])
    print("Page:", source["page"])
    print("Text:", source["text"])

print("\n" + "=" * 60)
print("TRACE")
print("=" * 60)


for span_record in result["trace"]:

    print("\nStage:", span_record["name"])
    print("Status:", span_record["status"])
    print("Duration:", span_record["duration_ms"], "ms")