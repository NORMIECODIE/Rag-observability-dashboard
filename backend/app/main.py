from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.observability.routes import router as observability_router
from app.llm import client

app = FastAPI(title="RAG Observability API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(observability_router)

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
        model="gemini-3.5-flash-lite",
        messages=[
            {"role":"user",
            "content":request.message
            }
        ]
    )

    return{
        "response":response.choices[0].message.content
    }