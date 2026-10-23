
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
        row for row in rows
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
        "avg_rag_latency_seconds": average(
            "rag_latency_seconds", rows
        ),
        "avg_judge_latency_seconds": average(
            "judge_latency_seconds", rows
        ),
        "total_cost_usd": (
            round(sum(known_costs), 6)
            if rows and len(known_costs) == len(rows)
            else None
        ),
        "cost_status": (
            "Available"
            if rows and len(known_costs) == len(rows)
            else "Unavailable: verified cost data is not available for every query"
        ),
        "results": rows,
    }

    # Write to a temporary file first, then replace the report.
    # This reduces the risk of leaving a partially written JSON file.
    temp_path = REPORT_PATH.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    temp_path.replace(REPORT_PATH)

    return report


def run_full_eval():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list) or not data:
        raise ValueError("The evaluation dataset must be a non-empty JSON list.")

    rows = []

    # Load previously saved results.
    if REPORT_PATH.exists():
        try:
            with REPORT_PATH.open("r", encoding="utf-8") as file:
                previous_report = json.load(file)

            if isinstance(previous_report, dict):
                saved_rows = previous_report.get("results", [])
                if isinstance(saved_rows, list):
                    rows = [
                        row for row in saved_rows
                        if isinstance(row, dict)
                        and isinstance(row.get("dataset_index"), int)
                        and 1 <= row["dataset_index"] <= len(data)
                    ]

            if not isinstance(previous_report, dict):
                print(
                    "Warning: The existing report is null or invalid. "
                    "No saved results could be loaded."
                )

        except (json.JSONDecodeError, OSError) as error:
            print(f"Warning: Could not read the previous report: {error}")
            print("No saved results could be loaded.")

    # Keep only the latest saved row for each dataset index.
    rows_by_index = {
        row["dataset_index"]: row
        for row in rows
    }
    rows = list(rows_by_index.values())

    completed_indexes = set(rows_by_index.keys())

    print(f"Dataset questions: {len(data)}")
    print(f"Already completed: {len(completed_indexes)}")

    for index, item in enumerate(data, start=1):
        if index in completed_indexes:
            continue

        question = item.get("question", "").strip()

        if not question:
            print(f"Skipping question {index}: question text is empty.")

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
            completed_indexes.add(index)
            continue

        print(f"\nEvaluating question {index}/{len(data)}...")

        try:
            # Step 1: Run retrieval and answer generation.
            start = time.perf_counter()
            result = run_rag(question)
            rag_latency = time.perf_counter() - start

            if not isinstance(result, dict):
                raise ValueError("run_rag() did not return a dictionary.")

            sources = result.get("sources") or []

            context = "\n".join(
                source.get("text", "")
                for source in sources
                if isinstance(source, dict)
                and isinstance(source.get("text"), str)
                and source["text"].strip()
            )

            # Step 2: Handle missing retrieved context.
            if not context.strip():
                print("Warning: No context retrieved for this question.")
                print(f"Question: {question}")
                print("Skipping LLM judge for this question.")

                rows.append({
                    "dataset_index": index,
                    "question": question,
                    "faithfulness": None,
                    "relevance": None,
                    "completeness": None,
                    "reason": "No retrieved context available for evaluation.",
                    "rag_latency_seconds": round(rag_latency, 4),
                    "judge_latency_seconds": 0,
                    "cost_usd": result.get("cost_usd"),
                })

                save_report(rows, len(data))
                completed_indexes.add(index)
                print(f"Progress saved: {len(completed_indexes)} questions")
                continue

            # Step 3: Validate the generated answer.
            answer = result.get("answer")

            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("RAG pipeline returned an empty answer.")

            # Step 4: Run the LLM judge.
            start = time.perf_counter()
            scores = judge(question, context, answer)
            judge_latency = time.perf_counter() - start

            # Step 5: Save this question's result.
            row = {
                "dataset_index": index,
                "question": question,
                "faithfulness": scores["faithfulness"],
                "relevance": scores["relevance"],
                "completeness": scores["completeness"],
                "reason": scores.get("reason", ""),
                "rag_latency_seconds": round(rag_latency, 4),
                "judge_latency_seconds": round(judge_latency, 4),
                "cost_usd": result.get("cost_usd"),
            }

            rows.append(row)
            completed_indexes.add(index)

            report = save_report(rows, len(data))

            print(
                f"Completed {index}/{len(data)} | "
                f"Faithfulness: {scores['faithfulness']:.2f} | "
                f"Relevance: {scores['relevance']:.2f}"
            )
            print(
                f"Progress saved: {report['completed_queries']} questions"
            )

        except Exception as error:
            # Preserve completed results and stop on an unexpected error.
            save_report(rows, len(data))

            print(f"\nEvaluation stopped at question {index}.")
            print(f"Reason: {error}")
            print("Completed results have been saved.")
            print("Fix the error, then rerun to resume.")
            return

    # This is outside the loop, so the evaluation processes all questions.
    report = save_report(rows, len(data))

    print("\nEvaluation finished.")
    print(
        f"Scored questions: {report['scored_queries']}/{len(data)}"
    )
    print(f"Average faithfulness: {report['avg_faithfulness']}")
    print(f"Average relevance: {report['avg_relevance']}")
    print(f"Average completeness: {report['avg_completeness']}")
    print(f"Average RAG latency: {report['avg_rag_latency_seconds']} seconds")
    print(f"Average judge latency: {report['avg_judge_latency_seconds']} seconds")
    print(f"Total cost: {report['total_cost_usd']}")
    print(f"Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    run_full_eval()
