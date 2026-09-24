from app.rag.retriever import retrieve
from app.rag.prompt import build_prompt
from app.llm.client import generate_from_messages



def run_rag(question: str) -> dict:

    # Retrieve relevant chunks
    chunks = retrieve(
        question,
        top_k=5
    )

    # Build grounded prompt
    messages = build_prompt(
        question,
        chunks
    )


    # Send prompt to Gemini
    answer = generate_from_messages(
        messages
    )


    # Return answer + sources

    return {
        "answer": answer,
        "sources": chunks
    }