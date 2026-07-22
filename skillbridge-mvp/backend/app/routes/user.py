from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.auth import UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserOut:
    return UserOut(id=current_user.id, name=current_user.name, email=current_user.email, is_active=current_user.is_active)
