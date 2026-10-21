import time
import uuid

from app.rag.retriever import create_query_embedding, retrieve
from app.rag.prompt import build_prompt
from app.rag.generator import generate_answer_with_usage
from app.observability.tracing import span
from app.observability.mongodb import save_trace
from app.observability.cost import calculate_cost
from app.evaluation.evaluator import evaluate_rag


def ask_rag(query: str, top_k: int = 5):
    trace_id = str(uuid.uuid4())
    trace = []
    start_time = time.time()

    model_name = None

    usage = {
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
    }

    estimated_cost_usd = None

    try:
        with span("embedding", trace):
            query_vector = create_query_embedding(query)

        with span("retrieval", trace):
            contexts = retrieve(query_vector, top_k=top_k)

        with span("generation", trace):
            prompt = build_prompt(query, contexts)

            result = generate_answer_with_usage(prompt)

            answer = result["answer"]
            model_name = result["model"]
            usage = result["usage"]

            estimated_cost_usd = calculate_cost(
                usage["prompt_tokens"],
                usage["completion_tokens"],
            )

        with span("evaluation", trace):
            evaluation = evaluate_rag(
                answer=answer,
                contexts=contexts,
            )
            

        total_duration_ms = round(
            (time.time() - start_time) * 1000,
            1,
        )

        trace_data = {
            "trace_id": trace_id,
            "query": query,
            "status": "ok",
            "total_duration_ms": total_duration_ms,
            "model": model_name,
            "usage": usage,
            "estimated_cost_usd": estimated_cost_usd,
            "evaluation": evaluation,
            "spans": trace,
        }

        save_trace(trace_data)

        return {
            "trace_id": trace_id,
            "query": query,
            "answer": answer,
            "model": model_name,
            "usage": usage,
            "estimated_cost_usd": estimated_cost_usd,
            "evaluation": evaluation,
            "trace": trace,
        }

    except Exception:
        total_duration_ms = round(
            (time.time() - start_time) * 1000,
            1,
        )

        trace_data = {
            "trace_id": trace_id,
            "query": query,
            "status": "error",
            "total_duration_ms": total_duration_ms,
            "model": model_name,
            "usage": usage,
            "estimated_cost_usd": estimated_cost_usd,
            "spans": trace,
        }

        save_trace(trace_data)
        raise