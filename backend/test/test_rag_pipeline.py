from app.rag.rag_pipeline import ask_rag


query = "What did Rutherford propose about the atom?"

result = ask_rag(query, top_k=3)

print("\nQuestion:")
print(result["query"])

print("\nAnswer:")
print(result["answer"])

print("\nEvaluation:")
print(result["evaluation"])

print("\nTrace:")

for span in result["trace"]:
    print(span)