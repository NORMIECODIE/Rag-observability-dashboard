
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.observability.mongodb import traces_collection

router = APIRouter(tags=["Traces"])


def parse_date(value: str | None, parameter_name: str):
    """Parse an ISO 8601 date and normalize it to UTC."""
    if value is None:
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid {parameter_name}. Use ISO 8601 format, "
                "for example 2026-10-23T00:00:00Z"
            ),
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    # MongoDB trace timestamps are stored in UTC.
    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


@router.get("/traces")
def get_traces(
    limit: int = Query(default=10, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    created_after: str | None = Query(default=None),
    created_before: str | None = Query(default=None),
):
    """Retrieve traces with optional filters and pagination."""

    # Validate status if provided.
    if status is not None and status not in ("success", "error"):
        raise HTTPException(
            status_code=400,
            detail="status must be 'success' or 'error'",
        )

    start_date = parse_date(created_after, "created_after")
    end_date = parse_date(created_before, "created_before")

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="created_after must be before created_before",
        )

    # Build MongoDB filters.
    filters = {}

    if status is not None:
        filters["status"] = status

    date_filter = {}

    if start_date is not None:
        date_filter["$gte"] = start_date

    if end_date is not None:
        date_filter["$lte"] = end_date

    if date_filter:
        filters["created_at"] = date_filter

    total = traces_collection.count_documents(filters)

    cursor = (
        traces_collection.find(filters)
        .sort([
            ("created_at", -1),
            ("_id", -1),
        ])
        .skip(skip)
        .limit(limit)
    )

    traces = []

    for trace in cursor:
        trace["_id"] = str(trace["_id"])

        created_at = trace.get("created_at")
        if created_at is not None:
            trace["created_at"] = created_at.isoformat()

        traces.append(trace)

    return {
        "total": total,
        "count": len(traces),
        "limit": limit,
        "skip": skip,
        "filters": {
            "status": status,
            "created_after": created_after,
            "created_before": created_before,
        },
        "traces": traces,
    }


@router.get("/traces/{trace_id}")
def get_trace(trace_id: str):
    """Retrieve one saved trace using its trace ID."""

    trace = traces_collection.find_one(
        {"trace_id": trace_id}
    )

    if trace is None:
        raise HTTPException(
            status_code=404,
            detail=f"Trace '{trace_id}' not found",
        )

    trace["_id"] = str(trace["_id"])

    created_at = trace.get("created_at")
    if created_at is not None:
        trace["created_at"] = created_at.isoformat()

    return trace
