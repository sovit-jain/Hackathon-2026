import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Profile
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, Token, UserOut
from app.utils.jwt_handler import create_access_token, verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/register", response_model=Token)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> Token:
    logger.info("Register request received for email=%s", payload.email)
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        logger.warning("Register failed: email already registered=%s", payload.email)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(name=payload.name, email=payload.email.lower(), password=get_password_hash(payload.password))
    db.add(user)
    db.flush()

    profile = Profile(user_id=user.id, target_role="db-technology", weekly_hours=5, current_level="beginner")
    db.add(profile)
    db.commit()
    db.refresh(user)

    logger.info("User registered successfully user_id=%s email=%s", user.id, user.email)
    token = create_access_token(user.id)
    return Token(access_token=token, user=UserOut(id=user.id, name=user.name, email=user.email, is_active=user.is_active))


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    logger.info("Login request received for email=%s", payload.email)
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password):
        logger.warning("Login failed for email=%s", payload.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    user.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token(user.id)
    logger.info("User logged in successfully user_id=%s email=%s", user.id, user.email)
    return Token(access_token=token, user=UserOut(id=user.id, name=user.name, email=user.email, is_active=user.is_active))


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    db: Session = Depends(get_db),
) -> User:
    auth_header_present = "authorization" in request.headers
    logger.debug("get_current_user auth_header_present=%s", auth_header_present)
    if not credentials or not credentials.credentials:
        logger.warning("Authentication failed: missing bearer token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = verify_token(credentials.credentials)
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        logger.warning("Authentication failed: user not found for sub=%s", payload.get("sub"))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    logger.debug("Authenticated user_id=%s", user.id)
    return user


@router.get("/me", response_model=UserOut)
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserOut:
    current_user.last_login = datetime.utcnow()
    db.commit()
    return UserOut(id=current_user.id, name=current_user.name, email=current_user.email, is_active=current_user.is_active)
