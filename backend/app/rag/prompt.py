SYSTEM_PROMPT = """You are a document-grounded assistant.
Answer the user's question using only the provided context.
If the answer cannot be found in the context, say that the
information is not available. Do not invent facts."""


def build_prompt(
        question: str,
        chunks: list[dict]
) -> list[dict]:

    context = "\n\n".join(
        f"[p.{c['page']}] {c['text']}"
        for c in chunks
    )


    user_msg = f"Context: \n{context}\n\n Question: {question}"

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_msg
        }
    ]