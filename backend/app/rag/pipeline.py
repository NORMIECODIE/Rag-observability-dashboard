
import uuid
import time

from app.rag.embeddings import create_embedding
from app.rag.retriever import retrieve
from app.rag.prompt import build_prompt
from app.llm.client import generate_from_messages
from app.observability.cost import calculate_generation_cost
from app.observability.tracing import span
from app.observability.trace_store import save_trace


# Runs the RAG pipeline
def run_rag(question: str) -> dict:

    trace_id = str(uuid.uuid4())
    start_time = time.time()
    trace = []

    # Default cost in case generation fails or cost is unavailable
    cost_usd = None

    # Create query embedding
    with span("embedding", trace):
        query_vector = create_embedding(question)

    # Retrieve relevant chunks
    with span("retrieval", trace) as retrieval_span:
        chunks = retrieve(
            question,
            top_k=5,
            query_vector=query_vector
        )

        retrieval_span["top_k"] = 5
        retrieval_span["result"] = chunks

    # Build grounded prompt
    messages = build_prompt(question, chunks)

    try:
        # Generate the answer
        with span("generation", trace) as generation_span:
            llm_result = generate_from_messages(messages)

            answer = llm_result["text"]
            usage = llm_result["usage"]

            input_tokens = usage.get("input_tokens")
            output_tokens = usage.get("output_tokens")

            generation_span["provider"] = "google"
            generation_span["model"] = "gemini-3.5-flash-lite"
            generation_span["input_tokens"] = input_tokens
            generation_span["output_tokens"] = output_tokens
            generation_span["total_tokens"] = usage.get("total_tokens")

            # Calculate estimated generation cost
            if (
                isinstance(input_tokens, (int, float))
                and isinstance(output_tokens, (int, float))
            ):
                cost_usd = calculate_generation_cost(
                    provider="google",
                    model="gemini-3.5-flash-lite",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )

            generation_span["estimated_cost_usd"] = cost_usd

        status = "success"

    except Exception as e:
        answer = str(e)
        status = "error"

    # Calculate total request latency
    total_latency_ms = round(
        (time.time() - start_time) * 1000,
        1
    )

    # Save trace to MongoDB
    save_trace(
        trace_id=trace_id,
        question=question,
        answer=answer,
        spans=trace,
        status=status,
        total_latency_ms=total_latency_ms
    )

    # Return cost as well as answer and sources
    return {
        "trace_id": trace_id,
        "answer": answer,
        "sources": chunks,
        "trace": trace,
        "cost_usd": cost_usd,
    }
