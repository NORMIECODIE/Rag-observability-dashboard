from fastapi import FastAPI
from app.config import settings

app = FastAPI(title="RAG Observability API")


@app.get("/")
def root():
    return {
        "message": "RAG Observability API",
        "qdrant_url": settings.qdrant_url
        }