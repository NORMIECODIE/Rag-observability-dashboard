
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(
    prefix="/metrics",
    tags=["Evaluation Metrics"],
)

# backend/evaluation/evaluation_report.json
PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "evaluation" / "evaluation_report.json"


def load_evaluation_report():
    """Load the saved evaluation report without rerunning evaluation."""

    if not REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation report not found at: {REPORT_PATH}",
        )

    try:
        with REPORT_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read evaluation report: {exc}",
        ) from exc


@router.get("/evaluation")
def get_evaluation_metrics():
    """Return summary metrics from the saved evaluation report."""

    report = load_evaluation_report()

    return {
        "dataset_size": report.get("dataset_size", 0),
        "completed_queries": report.get("completed_queries", 0),
        "scored_queries": report.get("scored_queries", 0),
        "queries_without_scores": report.get("queries_without_scores", 0),
        "average_scores": {
            "faithfulness": report.get("avg_faithfulness"),
            "relevance": report.get("avg_relevance"),
            "completeness": report.get("avg_completeness"),
        },
        "average_latency_seconds": {
            "rag": report.get("avg_rag_latency_seconds"),
            "judge": report.get("avg_judge_latency_seconds"),
        },
        "total_cost_usd": report.get("total_cost_usd"),
        "cost_status": report.get("cost_status"),
    }


@router.get("/evaluation/results")
def get_evaluation_results(
    limit: int = Query(default=10, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
):
    """Return paginated individual evaluation results."""

    report = load_evaluation_report()

    results = report.get("results", [])
    total = len(results)
    page = results[skip : skip + limit]

    return {
        "total": total,
        "count": len(page),
        "limit": limit,
        "skip": skip,
        "results": [
            {
                "dataset_index": item.get("dataset_index"),
                "question": item.get("question"),
                "faithfulness": item.get("faithfulness"),
                "relevance": item.get("relevance"),
                "completeness": item.get("completeness"),
                "reason": item.get("reason"),
                "rag_latency_seconds": item.get("rag_latency_seconds"),
                "judge_latency_seconds": item.get("judge_latency_seconds"),
                "cost_usd": item.get("cost_usd"),
            }
            for item in page
        ],
    }
