from fastapi import FastAPI
from app.llm.client import ask_llm
from app.config import settings
from app.api.routes_chat import router as chat_router

app = FastAPI(title="RAG Observability API")


@app.get("/")
def root():
    return {
        "message": "RAG Observability API",
        "qdrant_url": settings.qdrant_url
        }


@app.get("/ask")
def ask(question: str):
    answer = ask_llm(question)

    return {
        "question": question,
        "answer": answer
    }

@app.get("/")
def root():
    return{
        "message": "RAG Observability API"
    }

app.include_router(chat_router)