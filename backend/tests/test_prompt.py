from app.rag.retriever import retrieve
from app.rag.prompt import build_prompt


question = "What are common NLP tasks?"


chunks = retrieve(
    question,
    top_k=3
)


messages = build_prompt(
    question,
    chunks
)


print("\nSYSTEM MESSAGE:")
print(messages[0]["content"])


print("\nUSER MESSAGE:")
print(messages[1]["content"])