

INPUT_PRICE_PER_MILLION = 0.30
OUTPUT_PRICE_PER_MILLION = 2.50


def calculate_cost(prompt_tokens, completion_tokens):
    """
    Calculate estimated LLM cost in USD.

    Returns None when token usage is unavailable.
    """

    if prompt_tokens is None or completion_tokens is None:
        return None

    input_cost = (
        prompt_tokens * INPUT_PRICE_PER_MILLION / 1_000_000
    )

    output_cost = (
        completion_tokens * OUTPUT_PRICE_PER_MILLION / 1_000_000
    )

    return round(input_cost + output_cost, 10)