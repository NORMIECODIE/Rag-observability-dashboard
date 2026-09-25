from app.rag.embeddings import create_embedding
from app.rag.retriever import retrieve
from app.rag.prompt import build_prompt
from app.llm.client import generate_from_messages
from app.observability.tracing import span


def run_rag(question: str) -> dict:

    trace = []

    # It tells how long it take to create a query embedding
    with span("embedding", trace):

        query_vector = create_embedding(
            question
        )

    # It tells how long it takes for Qdrant retrieval and filtering
    with span("retrieval", trace):

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

    # It tells how long it takes to Gemini to generate an answer
    with span("generation", trace):

        # Send prompt to Gemini
        answer = generate_from_messages(
            messages

        )


    # Return answer + sources

    return {
        "answer": answer,
        "sources": chunks,
        "trace":trace
    }