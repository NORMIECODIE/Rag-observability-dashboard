
from fastapi import FastAPI

from app.llm.client import ask_llm
from app.config import settings
from app.api.routes_chat import router as chat_router
from app.api.routes_traces import router as traces_router
from app.api.routes_matrics import router as metrics_router
from app.api.routes_evaluation import router as evaluation_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG Observability API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "RAG Observability API",
        "qdrant_url": settings.qdrant_url,
    }


@app.get("/ask")
def ask(question: str):
    answer = ask_llm(question)

    return {
        "question": question,
        "answer": answer,
    }


app.include_router(chat_router)
app.include_router(traces_router)
app.include_router(metrics_router)
app.include_router(evaluation_router)