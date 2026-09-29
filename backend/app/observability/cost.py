PRICING = {
    "google": {
        "gemini-3.5-flash-lite": {
            "input_per_1m": 0.30,
            "output_per_1m": 2.50,
        }
    }
}


def calculate_generation_cost(
    provider: str,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:

    if input_tokens is None or output_tokens is None:
        return None

    pricing = PRICING.get(provider, {}).get(model)

    if pricing is None:
        return None

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input_per_1m"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output_per_1m"]

    return round(input_cost + output_cost, 10)