from app.rag.retriever import retrieve
from app.rag.prompt import build_prompt
from app.llm.client import generate_from_messages


question = input("Enter your question: ")


print("Retrieving relevant chunks....")

chunks = retrieve(
    question,
    top_k=3
)


print("Building prompt....")

messages = build_prompt(
    question,
    chunks
)

print("Sending prompt to Gemini...\n")

answer = generate_from_messages(
    messages
)


print("=" * 60)
print("QUESTION")
print("=" * 60)

print(question)


print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)


print(answer)