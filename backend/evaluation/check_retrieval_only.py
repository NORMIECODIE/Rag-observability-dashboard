import json
from pathlib import Path
from app.rag.retriever import retrieve

cache_path = Path("evaluation/cache_results.json")
if not cache_path.exists():
    print("Embedding cache not found. Stopping without calling Gemini.")
    raise SystemExit(0)

with open(cache_path, "r", encoding="utf-8") as f:
    cache = json.load(f)

questions = [
    "What is text summarization?",
    "What types of automated language tasks are described in the document?",
    "A system reads a long piece of text and produces a shorter version containing its main information. What NLP application is this?",
]

for question in questions:
    print(f"\nQUESTION: {question}")

    vector = cache.get(question)
    if vector is None:
        print("No cached embedding; skipped to avoid an API call.")
        continue

    chunks = retrieve(question, top_k=5, query_vector=vector)
    print(f"Retrieved chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):
        print(
            f"\n  Chunk {i} | page={chunk['page']} "
            f"| score={chunk['score']:.4f}"
        )
        print(f"  {chunk['text']}")
