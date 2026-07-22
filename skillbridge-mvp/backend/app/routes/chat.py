import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Profile
from app.models.user import User
from app.routes.auth import get_current_user
from app.utils.llm import generate_chat_reply

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("")
async def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    logger.info("Chat request received user_id=%s message=%s", current_user.id, payload.message)
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    role = profile.target_role if profile else "data-analyst"
    reply = await generate_chat_reply(payload.message, role)
    logger.info("Chat response generated user_id=%s role=%s", current_user.id, role)
    return {"reply": reply}
