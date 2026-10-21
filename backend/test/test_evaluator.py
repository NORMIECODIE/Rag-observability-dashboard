
from app.rag.rag_pipeline import ask_rag
from test.evaluation_cases import EVALUATION_CASES


for index, case in enumerate(EVALUATION_CASES, start=1):
    print(f"\n--- Evaluation Case {index} ---")
    print("Question:", case["question"])
    print("Expected answer:", case["expected_answer"])

    result = ask_rag(case["question"])
    answer = result["answer"]

    print("Generated answer:", answer)
    print("Evaluation:", result["evaluation"])

    # Simple baseline: check whether selected key facts
    # are present in the generated answer.
    expected_terms = case.get("expected_terms", [])
    normalized_answer = answer.lower()

    if expected_terms:
        matched = [
            term
            for term in expected_terms
            if term.lower() in normalized_answer
        ]
        score = len(matched) / len(expected_terms)

        print("Matched key facts:", matched)
        print(f"Key-fact coverage: {score:.2%}")
    else:
        print("Key-fact coverage: Not configured")
