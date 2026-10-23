from datetime import datetime, timedelta, timezone
from fastapi import APIRouter

from app.observability.mongodb import traces_collection

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)


@router.get("/overview")
def get_metrics_overview():
    """Return summary metrics for saved RAG traces."""

    total_requests = traces_collection.count_documents({})

    successful_requests = traces_collection.count_documents(
        {"status": "success"}
    )

    failed_requests = traces_collection.count_documents(
        {"status": "error"}
    )

    # Calculate average end-to-end latency.
    latency_pipeline = [
        {
            "$group": {
                "_id": None,
                "average_latency_ms": {
                    "$avg": "$total_latency_ms"
                },
            }
        }
    ]

    latency_result = list(
        traces_collection.aggregate(latency_pipeline)
    )

    average_latency_ms = (
        latency_result[0].get("average_latency_ms") or 0
        if latency_result
        else 0
    )

    # Collect token usage and estimated cost from generation spans.
    token_pipeline = [
        {"$unwind": "$spans"},
        {"$match": {"spans.name": "generation"}},
        {
            "$group": {
                "_id": None,
                "total_input_tokens": {
                    "$sum": "$spans.input_tokens"
                },
                "total_output_tokens": {
                    "$sum": "$spans.output_tokens"
                },
                "total_tokens": {
                    "$sum": "$spans.total_tokens"
                },
                "estimated_cost_usd": {
                    "$sum": "$spans.estimated_cost_usd"
                },
            }
        },
    ]

    token_result = list(
        traces_collection.aggregate(token_pipeline)
    )

    usage = token_result[0] if token_result else {}

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_latency_ms": round(average_latency_ms, 2),
        "total_input_tokens": usage.get("total_input_tokens", 0),
        "total_output_tokens": usage.get("total_output_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "estimated_cost_usd": round(
            usage.get("estimated_cost_usd", 0), 8
        ),
    }


@router.get("/latency")
def get_latency_metrics():
    """Return latency statistics for each RAG pipeline stage."""

    # Ignore zero and negative end-to-end latency values.
    overall_pipeline = [
        {
            "$match": {
                "total_latency_ms": {"$gt": 0}
            }
        },
        {
            "$group": {
                "_id": None,
                "average_ms": {"$avg": "$total_latency_ms"},
                "minimum_ms": {"$min": "$total_latency_ms"},
                "maximum_ms": {"$max": "$total_latency_ms"},
                "count": {"$sum": 1},
            }
        },
    ]

    overall_result = list(
        traces_collection.aggregate(overall_pipeline)
    )

    overall = overall_result[0] if overall_result else {}

    # Calculate statistics for individual pipeline stages.
    stage_pipeline = [
        {"$unwind": "$spans"},
        {
            "$match": {
                "spans.name": {
                    "$in": ["embedding", "retrieval", "generation"]
                },
                "spans.duration_ms": {"$gt": 0},
            }
        },
        {
            "$group": {
                "_id": "$spans.name",
                "average_ms": {"$avg": "$spans.duration_ms"},
                "minimum_ms": {"$min": "$spans.duration_ms"},
                "maximum_ms": {"$max": "$spans.duration_ms"},
                "count": {"$sum": 1},
            }
        },
    ]

    stage_results = list(
        traces_collection.aggregate(stage_pipeline)
    )

    stages = {}

    for item in stage_results:
        stages[item["_id"]] = {
            "average_ms": round(item["average_ms"], 2),
            "minimum_ms": round(item["minimum_ms"], 2),
            "maximum_ms": round(item["maximum_ms"], 2),
            "count": item["count"],
        }

    empty_stage = {
        "average_ms": 0,
        "minimum_ms": 0,
        "maximum_ms": 0,
        "count": 0,
    }

    return {
        "end_to_end": {
            "average_ms": round(overall.get("average_ms") or 0, 2),
            "minimum_ms": round(overall.get("minimum_ms") or 0, 2),
            "maximum_ms": round(overall.get("maximum_ms") or 0, 2),
            "count": overall.get("count", 0),
        },
        "stages": {
            "embedding": stages.get("embedding", empty_stage.copy()),
            "retrieval": stages.get("retrieval", empty_stage.copy()),
            "generation": stages.get("generation", empty_stage.copy()),
        },
    }

@router.get("/requests")
def get_request_volume(
    period: str = "day",
    days: int = 7,
):
    """Return request counts grouped by hour or day."""

    if period not in ("hour", "day"):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="period must be 'hour' or 'day'",
        )

    if days < 1 or days > 90:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="days must be between 1 and 90",
        )

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=days)

    date_format = (
        "%Y-%m-%dT%H:00:00Z"
        if period == "hour"
        else "%Y-%m-%d"
    )

    pipeline = [
        {
            "$match": {
                "created_at": {
                    "$gte": start_time,
                    "$lte": now,
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": date_format,
                        "date": "$created_at",
                        "timezone": "UTC",
                    }
                },
                "request_count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    results = list(traces_collection.aggregate(pipeline))

    return {
        "period": period,
        "days": days,
        "timezone": "UTC",
        "total_requests": sum(
            item["request_count"] for item in results
        ),
        "data": [
            {
                "time": item["_id"],
                "request_count": item["request_count"],
            }
            for item in results
        ],
    }
