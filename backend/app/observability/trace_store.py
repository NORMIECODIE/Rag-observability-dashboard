from datetime import datetime, timezone

from app.observability.mongodb import traces_collection


def save_trace(
    trace_id: str,
    question: str,
    answer: str,
    spans: list[dict],
    status: str = "success",
    total_latency_ms: float = 0.0
):
    document = {
        "trace_id": trace_id,
        "question": question,
        "answer": answer,
        "status": status,
        "total_latency_ms": total_latency_ms,
        "created_at": datetime.now(timezone.utc),
        "spans": spans
    }

    traces_collection.insert_one(document)

    print("Trace saved successfully")
