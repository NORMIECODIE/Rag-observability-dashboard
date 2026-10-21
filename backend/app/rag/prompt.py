def build_prompt(query: str, contexts: list[dict]) -> str:
    context_text = "\n\n".join(
        f"[Page {context['page']}]\n{context['text']}"
        for context in contexts
    )

    prompt = f"""
You are a helpful assistant answering questions using the provided context.

Use only the information provided in the context to answer the question.
If the answer cannot be found in the context, say:
"I don't have enough information in the provided context."

Context:
{context_text}

Question:
{query}

Answer:
"""

    return prompt.strip()
