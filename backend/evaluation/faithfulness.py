import instructor
import asyncio
import os

from dotenv import load_dotenv
from litellm import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import Faithfulness

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in your .env file.")

# LiteLLM provides an OpenAI-compatible client for Gemini.
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Add structured-output support to the async client.
client = instructor.from_openai(client)

llm = llm_factory(
    "gemini-3.5-flash-lite",
    provider="google",
    client=client,
    adapter="litellm",
)

faithfulness_scorer = Faithfulness(llm=llm)
# Workaround for async-client detection in Ragas 0.4.3
llm.is_async = True

async def score_faithfulness(
    question: str,
    answer: str,
    contexts: list[str],
) -> float:
    if not contexts:
        raise ValueError("At least one retrieved context is required.")

    result = await faithfulness_scorer.ascore(
        user_input=question,
        response=answer,
        retrieved_contexts=contexts,
    )

    return float(result.value)


if __name__ == "__main__":
    question = "What is NLP?"
    answer = "NLP enables computers to process human language."
    contexts = [
        "Natural Language Processing (NLP) is a field of AI "
        "that enables computers to understand and process human language."
    ]

    score = asyncio.run(
        score_faithfulness(question, answer, contexts)
    )

    print(f"Faithfulness score: {score:.3f}")
