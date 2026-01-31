from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User
from app.utils.dependencies import get_current_user
from app.services.ai_assistant_service import AIAssistantService
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import MovieResponse

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    content: str
    movies: List[MovieResponse]

@router.post("/", response_model=ChatResponse)
def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle user chat messages and return AI responses with optional movie recommendations.
    """
    try:
        response = AIAssistantService.process_query(current_user.id, request.message, db)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
