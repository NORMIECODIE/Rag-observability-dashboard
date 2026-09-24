from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.pipeline import run_rag

router = APIRouter()


class ChatRequest(BaseModel):
    question: str



@router.post("/chat")
def chat(req: ChatRequest):
    return run_rag(req.question)