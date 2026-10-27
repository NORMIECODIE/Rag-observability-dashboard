
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.observability.mongodb import traces_collection


router = APIRouter(tags=["Traces"])


def serialize_trace(trace: dict) -> dict:
    """Convert MongoDB values into JSON-compatible values."""
    trace["_id"] = str(trace["_id"])

    created_at = trace.get("created_at")
    if isinstance(created_at, datetime):
        trace["created_at"] = created_at.isoformat()

    return trace


@router.get("/traces")
def get_traces(
    limit: int = Query(default=10, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
):
    """Retrieve saved RAG traces, newest first."""

    total = traces_collection.count_documents({})

    cursor = (
        traces_collection.find({})
        .sort([("created_at", -1), ("_id", -1)])
        .skip(skip)
        .limit(limit)
    )

    traces = [
        serialize_trace(trace)
        for trace in cursor
    ]

    return {
        "total": total,
        "count": len(traces),
        "limit": limit,
        "skip": skip,
        "traces": traces,
    }


@router.get("/traces/{trace_id}/details")
def get_trace_details(trace_id: str):
    """Return dashboard-friendly details for one RAG trace."""

    trace = traces_collection.find_one({"trace_id": trace_id})

    if trace is None:
        raise HTTPException(
            status_code=404,
            detail=f"Trace '{trace_id}' not found",
        )

    spans = trace.get("spans", [])

    latency_breakdown = {
        "embedding_ms": 0,
        "retrieval_ms": 0,
        "generation_ms": 0,
    }

    token_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }

    estimated_cost_usd = 0.0
    retrieval_chunks = []
    retrieval_top_k = None
    generation_metadata = {}

    for span in spans:
        name = span.get("name")
        duration = span.get("duration_ms", 0) or 0

        if name in ("embedding", "retrieval", "generation"):
            latency_breakdown[f"{name}_ms"] = duration

        if name == "retrieval":
            # Your saved trace stores retrieved chunks in "result".
            retrieval_chunks = span.get("result", []) or []
            retrieval_top_k = span.get("top_k")

        elif name == "generation":
            token_usage["input_tokens"] = (
                span.get("input_tokens", 0) or 0
            )
            token_usage["output_tokens"] = (
                span.get("output_tokens", 0) or 0
            )
            token_usage["total_tokens"] = (
                span.get("total_tokens", 0) or 0
            )
            estimated_cost_usd = (
                span.get("estimated_cost_usd", 0) or 0
            )

            generation_metadata = {
                "provider": span.get("provider"),
                "model": span.get("model"),
            }

    created_at = trace.get("created_at")
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()

    return {
        "trace_id": trace.get("trace_id"),
        "question": trace.get("question"),
        "answer": trace.get("answer"),
        "status": trace.get("status"),
        "created_at": created_at,
        "total_latency_ms": trace.get("total_latency_ms", 0),
        "latency_breakdown": latency_breakdown,
        "generation": generation_metadata,
        "token_usage": token_usage,
        "estimated_cost_usd": estimated_cost_usd,
        "retrieval": {
            "top_k": retrieval_top_k,
            "chunk_count": len(retrieval_chunks),
            "chunks": retrieval_chunks,
        },
        "evaluation": trace.get("evaluation"),
    }


@router.get("/traces/{trace_id}")
def get_trace(trace_id: str):
    """Retrieve one complete saved trace by its trace ID."""

    trace = traces_collection.find_one(
        {"trace_id": trace_id}
    )

    if trace is None:
        raise HTTPException(
            status_code=404,
            detail=f"Trace '{trace_id}' not found",
        )

    return serialize_trace(trace)
