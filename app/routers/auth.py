from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.db.database import get_session
from app.db.models import User
from app.schemas.auth import UserCreate, Token
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, session=Depends(get_session)):
    """Register a new user (compatible with frontend format)."""
    # Check if user exists
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        return {
            "success": False,
            "error": "Email already registered"
        }

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role or "customer",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    return {
        "success": True,
        "token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    }


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    # OAuth2PasswordRequestForm provides username and password fields
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)


def _login_compatible_logic(email: str, password: str, session):
    """Shared login logic for compatible endpoints."""
    if not email or not password:
        return {
            "success": False,
            "error": "Email and password are required"
        }
    
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        return {
            "success": False,
            "error": "Incorrect email or password"
        }
    
    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    return {
        "success": True,
        "token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    }


@router.post("/login")
def login_compatible(payload: dict, session=Depends(get_session)):
    """Compatible login endpoint for frontend (expects {email, password})."""
    email = payload.get("email")
    password = payload.get("password")
    return _login_compatible_logic(email, password, session)


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }


