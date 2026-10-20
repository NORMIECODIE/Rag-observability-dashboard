
from app.rag.embeddings import create_embedding
import json
from pathlib import Path

from app.rag.retriever import retrieve

DATASET_PATH = Path("evaluation/test_questions.json")
CACHE_PATH = Path("evaluation/cache_results.json")

def load_embedding_cache():

    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r", encoding = "utf-8") as file:
            return json.load(file)

    return {}

def save_embedding_cache(cache):
    with open(CACHE_PATH, "w", encoding = "utf_8") as file:
        json.dump(cache, file)

def context_precision(retrieved_pages, expected_pages):
    if not retrieved_pages:
        return 0.0

    hits = [
        1 if page in expected_pages else 0
        for page in retrieved_pages
    ]

    return sum(hits) / len(hits)


def run_eval(configs, dataset_path=DATASET_PATH):
    with open(dataset_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Evaluate answerable questions only.
    answerable_data = [
        item for item in data
        if item["difficulty"] != "unanswerable"
    ]

    question_vectors = load_embedding_cache()

    for item in answerable_data:

        question = item["question"]

        if question not in question_vectors:
            print(f"Creating embeddings:{question}")

            question_vectors[question] = create_embedding(question)

            save_embedding_cache(question_vectors)


    print("\nRetrieval Evaluation")
    print("-" * 50)
    print(
        f"{'Chunk Size':<12}"
        f"{'Overlap':<10}"
        f"{'Top K':<10}"
        f"{'Precision':<12}"
    )
    print("-" * 50)

    for cfg in configs:
        scores = []

        for item in answerable_data:
            chunks = retrieve(
                item["question"],
                top_k=cfg["top_k"],
                query_vector=question_vectors[item["question"]],
            )

            if item == answerable_data[0]:
                continue


            retrieved_pages = [
                f"page {chunk['page']}"
                for chunk in chunks
            ]

            score = context_precision(
                retrieved_pages,
                item["expected_sources"]
            )

            scores.append(score)

        average = (
            sum(scores) / len(scores)
            if scores else 0.0
        )

        print(
            f"{cfg['chunk_size']:<12}"
            f"{cfg['overlap']:<10}"
            f"{cfg['top_k']:<10}"
            f"{average:.3f}"
        )


if __name__ == "__main__":
    configs = [
        {"chunk_size": 300, "overlap": 50, "top_k": 3},
        {"chunk_size": 300, "overlap": 50, "top_k": 5},
    ]

    run_eval(configs)
