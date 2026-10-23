from fastapi import APIRouter
from pydantic import BaseModel

from ai.assistant import ask_assistant


router = APIRouter(
    prefix="/assistant",
    tags=["RAG Assistant"]
)


class AssistantRequest(BaseModel):
    question: str


@router.post("/ask")
def assistant(request: AssistantRequest):
    return ask_assistant(request.question)