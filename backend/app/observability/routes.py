
from fastapi import APIRouter, HTTPException
from app.observability.mongodb import traces_collection

router = APIRouter(
    prefix="/observability",
    tags=["Observability"],
)


@router.get("/traces")
def get_traces():
    traces = list(
        traces_collection
        .find()
        .sort("_id", -1)
        .limit(20)
    )

    for trace in traces:
        trace["_id"] = str(trace["_id"])

    return {"traces": traces}


@router.get("/traces/{trace_id}")
def get_trace(trace_id: str):
    trace = traces_collection.find_one(
        {"trace_id": trace_id}
    )

    if trace is None:
        raise HTTPException(
            status_code=404,
            detail="Trace not found",
        )

    trace["_id"] = str(trace["_id"])

    return trace


@router.get("/metrics/summary")
def get_metrics_summary():
    # Aggregate every stored trace, not just the latest 20.
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_traces": {"$sum": 1},
                "successful_traces": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$status", "ok"]},
                            1,
                            0,
                        ]
                    }
                },
                "failed_traces": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$status", "error"]},
                            1,
                            0,
                        ]
                    }
                },
                "average_duration_ms": {
                    "$avg": "$total_duration_ms"
                },
                "total_tokens": {
                    "$sum": "$usage.total_tokens"
                },
                "total_estimated_cost_usd": {
                    "$sum": "$estimated_cost_usd"
                },
                "traces_with_cost": {
                    "$sum": {
                        "$cond": [
                            {
                                "$isNumber": "$estimated_cost_usd"
                            },
                            1,
                            0,
                        ]
                    }
                },
            }
        }
    ]

    results = list(
        traces_collection.aggregate(pipeline)
    )

    if not results:
        return {
            "total_traces": 0,
            "successful_traces": 0,
            "failed_traces": 0,
            "average_duration_ms": 0,
            "total_tokens": 0,
            "total_estimated_cost_usd": 0,
            "traces_with_cost": 0,
        }

    metrics = results[0]
    metrics.pop("_id", None)

    # Return predictable numeric values.
    for field in (
        "total_traces",
        "successful_traces",
        "failed_traces",
        "total_tokens",
        "traces_with_cost",
    ):
        metrics[field] = metrics.get(field) or 0

    metrics["average_duration_ms"] = round(
        metrics.get("average_duration_ms") or 0,
        1,
    )

    metrics["total_estimated_cost_usd"] = round(
        metrics.get("total_estimated_cost_usd") or 0,
        10,
    )

    return metrics
