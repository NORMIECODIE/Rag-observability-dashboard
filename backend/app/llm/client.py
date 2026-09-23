import os

from google import genai
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