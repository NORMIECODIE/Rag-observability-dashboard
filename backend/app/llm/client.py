import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

from google.genai.errors import ServerError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

# Load the environment variables
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# It ask the LLM a direct question ( without any context )  to evaluate its raw accuracy
def ask_llm(
    question: str,
    model: str = "gemini-3.5-flash-lite"
) -> str:

    try:
        chat = client.chats.create(model=model)
        response = chat.send_message(question)
        return response.text

    except Exception as e:
        return f"Error calling Gemini LLM: {e}"

# Retry up to 3 times, waiting 2s, 4s, 8s between attempts when a ServerError occurs
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(ServerError),
    reraise=True,
)
def _call_gemini_api(client, model_name, messages):
    return client.models.generate_content(model=model_name, contents=messages)

# Generates grounded response with retrieved context
def generate_from_messages(
        messages: list[dict],
        model: str = "gemini-3.5-flash-lite"
)-> str:

    system_message = messages[0]["content"]
    user_message = messages[1]["content"]

    try:

        response = client.models.generate_content(
            model= model,
            contents= user_message,
            config= types.GenerateContentConfig( 
                system_instruction= system_message,
                automatic_function_calling= types.AutomaticFunctionCallingConfig(
                    disable = True
                )
            )
        )

        usage = response.usage_metadata

        usage_data = {
            "input_tokens": getattr(
                usage,
                "prompt_token_count",
                None
            ),
            "output_tokens": getattr(
                usage,
                "candidates_token_count",
                None
            ),
            "total_tokens": getattr(
                usage,
                "total_token_count",
                None
            )
        }

        return {
            "text": response.text,
            "usage": usage_data
        }

    except Exception as e:

        raise RuntimeError(f"Gemini LLM error: {e}")