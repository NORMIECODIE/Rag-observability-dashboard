
def evaluate_retrieval(contexts: list[dict]) -> dict:
    """
    Summarize retrieval results using the similarity scores
    returned by the vector database.

    Similarity is a signal, not proof of relevance.
    """
    scores = [
        float(context["score"])
        for context in contexts
        if context.get("score") is not None
    ]

    return {
        "retrieved_chunks": len(contexts),
        "average_similarity": (
            round(sum(scores) / len(scores), 4)
            if scores
            else None
        ),
        "highest_similarity": (
            round(max(scores), 4)
            if scores
            else None
        ),
    }


def evaluate_answer_coverage(
    answer: str,
    contexts: list[dict],
) -> dict:
    """
    A simple lexical-overlap heuristic.

    This is NOT a definitive measure of answer faithfulness.
    It checks how many distinct answer words also occur in
    the retrieved context.
    """
    import re

    def meaningful_words(text: str) -> set[str]:
        return {
            word.lower()
            for word in re.findall(r"\b[a-zA-Z0-9]+\b", text)
            if len(word) > 2
        }

    context_text = " ".join(
        context.get("text", "")
        for context in contexts
    )

    answer_words = meaningful_words(answer)
    context_words = meaningful_words(context_text)

    overlap = answer_words & context_words

    return {
        "answer_word_count": len(answer_words),
        "overlapping_word_count": len(overlap),
        "lexical_coverage": (
            round(len(overlap) / len(answer_words), 4)
            if answer_words
            else None
        ),
        "method": "lexical_overlap_heuristic",
    }


def evaluate_rag(
    answer: str,
    contexts: list[dict],
) -> dict:
    """Run the initial retrieval and answer-coverage checks."""
    return {
        "retrieval": evaluate_retrieval(contexts),
        "answer_coverage": evaluate_answer_coverage(
            answer,
            contexts,
        ),
    }
