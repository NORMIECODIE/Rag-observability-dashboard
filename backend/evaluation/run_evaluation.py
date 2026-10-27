
import json
import statistics
import time
from pathlib import Path

from app.rag.pipeline import run_rag
from evaluation.llm_judge import judge


DATASET_PATH = Path("evaluation/test_questions.json")
REPORT_PATH = Path("evaluation/evaluation_report.json")


def save_report(rows, dataset_size):
    """Save evaluation results and aggregate metrics safely."""

    scored_rows = [
        row
        for row in rows
        if all(
            isinstance(row.get(key), (int, float))
            and not isinstance(row.get(key), bool)
            for key in ("faithfulness", "relevance", "completeness")
        )
    ]

    known_costs = [
        row["cost_usd"]
        for row in rows
        if isinstance(row.get("cost_usd"), (int, float))
        and not isinstance(row.get("cost_usd"), bool)
    ]

    def average(key, source_rows):
        values = [
            row[key]
            for row in source_rows
            if isinstance(row.get(key), (int, float))
            and not isinstance(row.get(key), bool)
        ]
        return round(statistics.mean(values), 4) if values else None

    all_costs_available = bool(rows) and len(known_costs) == len(rows)

    report = {
        "dataset_size": dataset_size,
        "completed_queries": len({
            row["dataset_index"]
            for row in rows
            if "dataset_index" in row
        }),
        "scored_queries": len(scored_rows),
        "queries_without_scores": len(rows) - len(scored_rows),
        "avg_faithfulness": average("faithfulness", scored_rows),
        "avg_relevance": average("relevance", scored_rows),
        "avg_completeness": average("completeness", scored_rows),
        "avg_rag_latency_seconds": average("rag_latency_seconds", rows),
        "avg_judge_latency_seconds": average("judge_latency_seconds", rows),
        "total_cost_usd": (
            round(sum(known_costs), 6)
            if all_costs_available
            else None
        ),
        "cost_status": (
            "Available"
            if all_costs_available
            else (
                "Unavailable: verified cost data is not available "
                "for every query"
            )
        ),
        "results": rows,
    }

    temp_path = REPORT_PATH.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    temp_path.replace(REPORT_PATH)

    return report


def run_full_eval():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list) or not data:
        raise ValueError(
            "The evaluation dataset must be a non-empty JSON list."
        )

    if not all(isinstance(item, dict) for item in data):
        raise ValueError(
            "Every evaluation dataset item must be a JSON object."
        )

    rows = []

    # Load existing results so completed questions are not rerun.
    if REPORT_PATH.exists():
        try:
            with REPORT_PATH.open("r", encoding="utf-8") as file:
                previous_report = json.load(file)

            if isinstance(previous_report, dict):
                saved_rows = previous_report.get("results", [])

                if isinstance(saved_rows, list):
                    rows = [
                        row
                        for row in saved_rows
                        if isinstance(row, dict)
                        and isinstance(row.get("dataset_index"), int)
                        and not isinstance(row.get("dataset_index"), bool)
                        and 1 <= row["dataset_index"] <= len(data)
                    ]
                else:
                    print(
                        "Warning: Existing report results are invalid. "
                        "No saved results could be loaded."
                    )
            else:
                print(
                    "Warning: Existing report is invalid. "
                    "No saved results could be loaded."
                )

        except (json.JSONDecodeError, OSError) as error:
            print(f"Warning: Could not read previous report: {error}")
            print("No saved results could be loaded.")

    # Keep the latest saved result for each question index.
    rows_by_index = {
        row["dataset_index"]: row
        for row in rows
    }

    rows = list(rows_by_index.values())
    completed_indexes = set(rows_by_index.keys())

    print(f"Dataset questions: {len(data)}")
    print(f"Previously saved results retained: {len(rows)}")
    print(f"Questions remaining: {len(data) - len(completed_indexes)}")

    processed_this_run = 0

    for index, item in enumerate(data, start=1):
        # Skip questions already present in the report.
        if index in completed_indexes:
            continue

        question = item.get("question", "")

        if not isinstance(question, str) or not question.strip():
            print(f"Skipping question {index}: question is empty.")

            rows.append({
                "dataset_index": index,
                "question": "",
                "faithfulness": None,
                "relevance": None,
                "completeness": None,
                "reason": "Question text is empty.",
                "rag_latency_seconds": 0,
                "judge_latency_seconds": 0,
                "cost_usd": None,
            })

            save_report(rows, len(data))
            processed_this_run += 1
            continue

        question = question.strip()

        print(f"\nEvaluating question {index}/{len(data)}...")

        try:
            # Step 1: Run the RAG pipeline.
            start = time.perf_counter()
            result = run_rag(question)
            rag_latency = time.perf_counter() - start

            if not isinstance(result, dict):
                raise ValueError(
                    "run_rag() did not return a dictionary."
                )

            print("RAG result keys:", list(result.keys()))
            print("RAG generation cost:", result.get("cost_usd"))

            sources = result.get("sources") or []

            context = "\n".join(
                source.get("text", "")
                for source in sources
                if isinstance(source, dict)
                and isinstance(source.get("text"), str)
                and source["text"].strip()
            )

            # Accept only numeric, non-boolean costs.
            cost_usd = result.get("cost_usd")

            if (
                not isinstance(cost_usd, (int, float))
                or isinstance(cost_usd, bool)
            ):
                cost_usd = None

            # Step 2: Handle missing retrieved context.
            if not context.strip():
                print("Warning: No context retrieved.")

                row = {
                    "dataset_index": index,
                    "question": question,
                    "faithfulness": None,
                    "relevance": None,
                    "completeness": None,
                    "reason": (
                        "No retrieved context available for evaluation."
                    ),
                    "rag_latency_seconds": round(rag_latency, 4),
                    "judge_latency_seconds": 0,
                    "cost_usd": cost_usd,
                }

            else:
                # Step 3: Validate the generated answer.
                answer = result.get("answer")

                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError(
                        "RAG pipeline returned an empty answer."
                    )

                # Step 4: Evaluate the answer using the LLM judge.
                start = time.perf_counter()
                scores = judge(question, context, answer)
                judge_latency = time.perf_counter() - start

                print("Judge scores:", scores)

                row = {
                    "dataset_index": index,
                    "question": question,
                    "faithfulness": scores["faithfulness"],
                    "relevance": scores["relevance"],
                    "completeness": scores["completeness"],
                    "reason": scores.get("reason", ""),
                    "rag_latency_seconds": round(rag_latency, 4),
                    "judge_latency_seconds": round(judge_latency, 4),
                    "cost_usd": cost_usd,
                }

            # Replace any previous row for this question, if present.
            rows = [
                saved
                for saved in rows
                if saved.get("dataset_index") != index
            ]
            rows.append(row)

            report = save_report(rows, len(data))
            processed_this_run += 1

            print(f"Saved question {index}.")
            print(f"Cost for this RAG request: {cost_usd}")
            print(f"Report total cost: {report['total_cost_usd']}")
            print(f"Cost status: {report['cost_status']}")

        except Exception as error:
            # Save completed results before stopping.
            save_report(rows, len(data))
            print(f"\nEvaluation stopped at question {index}.")
            print(f"Reason: {error}")
            print("Previously saved results were preserved.")
            return

    report = save_report(rows, len(data))

    print("\nEvaluation finished.")
    print(f"Questions processed this run: {processed_this_run}")
    print(f"Scored questions in report: {report['scored_queries']}")
    print(f"Total evaluation cost: {report['total_cost_usd']}")
    print(f"Cost status: {report['cost_status']}")
    print(f"Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    run_full_eval()
