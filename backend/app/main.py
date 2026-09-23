from fastapi import FastAPI
from pydantic import BaseModel
from app.config import settings

from app.llm import client

app = FastAPI(title="RAG Observability API")

class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "message": "RAG Observability API",
        "qdrant_url": settings.qdrant_url
        }

@app.post("/chat")
def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model="gemini-3.6-flash",
        messages=[
            {"role":"user",
            "content":request.message
            }
        ]
    )

    return{
        "response":response.choices[0].message.content
    }