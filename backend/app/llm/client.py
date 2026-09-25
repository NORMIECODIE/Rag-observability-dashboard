import os

from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_llm(
    question: str,
    model: str = "gemini-3.6-flash"
) -> str:

    try:
        chat = client.chats.create(model=model)
        response = chat.send_message(question)
        return response.text

    except Exception as e:
        return f"Error calling Gemini LLM: {e}"



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


        return response.text

    except Exception as e:

        return f"Error calling Gemini LLM: {e}"