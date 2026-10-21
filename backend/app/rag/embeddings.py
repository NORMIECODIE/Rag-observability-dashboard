from google import genai
from app.config import settings


client = genai.Client(api_key=settings.gemini_api_key)


def create_embedding(text: str):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )

    return result.embeddings[0].values