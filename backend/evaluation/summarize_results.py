
import json
from pathlib import Path
from collections import defaultdict

RESULT_FILES = [
    Path("evaluation/faithfulness_results.json"),
    Path("evaluation/faithfulness_batch2_results.json"),
    Path("evaluation/faithfulness_batch3_results.json"),
]

results = []

for path in RESULT_FILES:
    if not path.exists():
        print(f"Missing file: {path}")
        continue

    with open(path, "r", encoding="utf-8") as file:
        results.extend(json.load(file))

groups = defaultdict(list)

for item in results:
    key = (
        item["chunk_size"],
        item["overlap"],
        item["top_k"],
    )
    groups[key].append(item)

print("\nCombined RAG Evaluation")
print("-" * 65)
print(
    f"{'Chunk':<10}{'Overlap':<10}{'Top K':<10}"
    f"{'Questions':<12}{'Precision':<12}{'Faithfulness':<12}"
)
print("-" * 65)

for (chunk, overlap, top_k), items in sorted(groups.items()):
    precision = [
        item["context_precision"]
        for item in items
        if item.get("context_precision") is not None
    ]
    faithfulness = [
        item["faithfulness"]
        for item in items
        if item.get("faithfulness") is not None
    ]

    avg_precision = sum(precision) / len(precision) if precision else 0
    avg_faithfulness = (
        sum(faithfulness) / len(faithfulness)
        if faithfulness else 0
    )

    print(
        f"{chunk:<10}{overlap:<10}{top_k:<10}"
        f"{len(items):<12}{avg_precision:<12.3f}"
        f"{avg_faithfulness:<12.3f}"
    )

print(f"\nTotal evaluation records: {len(results)}")
