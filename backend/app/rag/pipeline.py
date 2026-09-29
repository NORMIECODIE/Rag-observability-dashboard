from pydantic._internal import _schema_generation_shared
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

    # Generate a unique trace ID
    trace_id = str(uuid.uuid4())

    start_time = time.time()

    trace = []

    # It tells how long it take to create a query embedding
    with span("embedding", trace):

        query_vector = create_embedding(
            question
        )

    # It tells how long it takes for Qdrant retrieval and filtering
    with span("retrieval", trace) as retrieval_span:
        
        # Retrieve relevant chunks
         chunks = retrieve(
            question,
            top_k=5,
            query_vector = query_vector
        )

         retrieval_span["top_k"]= 5
         retrieval_span["result"]= chunks

    # Build grounded prompt
    messages = build_prompt(
        question,
        chunks
    )

    # It tells how long it takes to Gemini to generate an answer
    try:
        with span("generation",trace) as generation_span:
            llm_result = generate_from_messages(messages)

            answer = llm_result["text"]
            usage = llm_result["usage"]

            generation_span["provider"] = "google"
            generation_span["model"] = "gemini-3.5-flash-lite"

            generation_span["input_tokens"] = usage.get(
                "input_tokens"
            )
            
            generation_span["output_tokens"] = usage.get(
                "output_tokens"
            )

            # Total tokens used in the generation
            generation_span["total_tokens"] = usage.get(
                "total_tokens"
            )

            # Calculate estimated cost
            generation_span["estimated_cost_usd"] = calculate_generation_cost(
            provider="google",
            model="gemini-3.5-flash-lite",
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            )
        
        status = "success"

    except Exception as e:
        answer = str(e)
        status = "error"

    # Calculate total RAG request latency
    total_latency_ms = round(
        (time.time() - start_time) * 1000,
        1
    )

    # Save the complete trace to MongoDB
    save_trace(
        trace_id=trace_id,
        question=question,
        answer=answer,
        spans=trace,
        status=status,
        total_latency_ms=total_latency_ms
    )

    # Return answer + sources

    return {
        "trace_id": trace_id,
        "answer": answer,
        "sources": chunks,
        "trace":trace
    }