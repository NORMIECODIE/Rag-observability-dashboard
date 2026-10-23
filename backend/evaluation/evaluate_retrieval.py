
import asyncio
import json
from pathlib import Path

from app.rag.embeddings import create_embedding
from app.rag.retriever import retrieve
from app.llm.client import generate_from_messages
from evaluation.faithfulness import score_faithfulness

DATASET_PATH = Path("evaluation/test_questions.json")
CACHE_PATH = Path("evaluation/cache_results.json")
RESULTS_PATH = Path("evaluation/faithfulness_batch3_results.json")


def load_embedding_cache():
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_embedding_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as file:
        json.dump(cache, file)


def context_precision(retrieved_pages, expected_pages):
    if not retrieved_pages:
        return 0.0

    hits = [
        1 if page in expected_pages else 0
        for page in retrieved_pages
    ]

    return sum(hits) / len(hits)


async def run_eval(configs, dataset_path=DATASET_PATH):
    with open(dataset_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    answerable_data = [
        item for item in data
        if item["difficulty"] != "unanswerable"
    ]

    answerable_data = answerable_data[3:5]
    
    question_vectors = load_embedding_cache()

    for item in answerable_data:
        question = item["question"]

        if question not in question_vectors:
            print(f"Creating embedding: {question}")
            question_vectors[question] = create_embedding(question)
            save_embedding_cache(question_vectors)

    all_results = []

    print("\nRAG Evaluation")
    print("-" * 75)
    print(
        f"{'Chunk Size':<12}"
        f"{'Overlap':<10}"
        f"{'Top K':<8}"
        f"{'Precision':<12}"
        f"{'Faithfulness':<14}"
    )
    print("-" * 75)

    for cfg in configs:
        precision_scores = []
        faithfulness_scores = []

        for item in answerable_data:
            question = item["question"]

            chunks = retrieve(
                question,
                top_k=cfg["top_k"],
                query_vector=question_vectors[question],
            )

            retrieved_pages = [
                f"page {chunk['page']}"
                for chunk in chunks
            ]

            precision = context_precision(
                retrieved_pages,
                item["expected_sources"],
            )
            precision_scores.append(precision)

            contexts = [
                chunk["text"]
                for chunk in chunks
                if chunk.get("text")
            ]

            if not contexts:
                print(f"Skipping faithfulness: no chunks for {question}")
                faithfulness = None
            else:
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "Answer the user's question using only the "
                            "provided context. If the context is insufficient, "
                            "say so. Do not add unsupported facts."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Context:\n{' '.join(contexts)}\n\n"
                            f"Question: {question}"
                        ),
                    },
                ]

                generated = generate_from_messages(messages)
                answer = generated["text"]

                faithfulness = await score_faithfulness(
                    question=question,
                    answer=answer,
                    contexts=contexts,
                )

                faithfulness_scores.append(faithfulness)

            all_results.append({
                "question": question,
                "chunk_size": cfg["chunk_size"],
                "overlap": cfg["overlap"],
                "top_k": cfg["top_k"],
                "retrieved_pages": retrieved_pages,
                "context_precision": precision,
                "answer": answer if contexts else None,
                "faithfulness": faithfulness,
            })

        avg_precision = (
            sum(precision_scores) / len(precision_scores)
            if precision_scores else 0.0
        )

        avg_faithfulness = (
            sum(faithfulness_scores) / len(faithfulness_scores)
            if faithfulness_scores else 0.0
        )

        print(
            f"{cfg['chunk_size']:<12}"
            f"{cfg['overlap']:<10}"
            f"{cfg['top_k']:<8}"
            f"{avg_precision:<12.3f}"
            f"{avg_faithfulness:<14.3f}"
        )

    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(all_results, file, indent=2, ensure_ascii=False)

    print(f"\nDetailed results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    configs = [
        {"chunk_size": 300, "overlap": 50, "top_k": 3},
        {"chunk_size": 300, "overlap": 50, "top_k": 5},
    ]

    asyncio.run(run_eval(configs))
