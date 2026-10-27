
import json
from pathlib import Path
from numbers import Real

report_path = Path(__file__).with_name("evaluation_report.json")

with report_path.open("r", encoding="utf-8") as file:
    report = json.load(file)

results = report.get("results", [])

valid_costs = []
missing_costs = 0

for index, result in enumerate(results, start=1):
    cost = result.get("cost_usd")

    if (
        isinstance(cost, Real)
        and not isinstance(cost, bool)
        and cost >= 0
    ):
        valid_costs.append(float(cost))
    else:
        missing_costs += 1
        print(
            f"Missing cost in result {index}: "
            f"{result.get('question', 'Unknown question')}"
        )

print("\n--- Evaluation Cost Report ---")
print(f"Total results: {len(results)}")
print(f"Results with valid costs: {len(valid_costs)}")
print(f"Results missing valid costs: {missing_costs}")

if valid_costs:
    print(f"Sum of available costs: ${sum(valid_costs):.8f} USD")
    if missing_costs:
        print("WARNING: This is a partial total, not the full evaluation cost.")
    else:
        print("All results have valid costs.")
else:
    print("No valid per-result cost values were found.")
