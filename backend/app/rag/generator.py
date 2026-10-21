
from app.llm import client


MODEL_NAME = "gemini-3.5-flash-lite"


def generate_answer_with_usage(prompt: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    # Extract the generated answer.
    answer = response.choices[0].message.content or ""

    # Extract token usage when the API provides it.
    usage_data = getattr(response, "usage", None)

    if usage_data is not None:
        prompt_tokens = getattr(usage_data, "prompt_tokens", None)
        completion_tokens = getattr(
            usage_data, "completion_tokens", None
        )
        total_tokens = getattr(usage_data, "total_tokens", None)
    else:
        prompt_tokens = None
        completion_tokens = None
        total_tokens = None

    usage = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }

    return {
        "answer": answer,
        "model": MODEL_NAME,
        "usage": usage,
    }


def generate_answer(prompt: str) -> str:
    # Preserve compatibility with existing code and tests.
    result = generate_answer_with_usage(prompt)
    return result["answer"]
