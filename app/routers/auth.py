from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session

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
def register(user_in: UserCreate, db: Session = Depends(get_session)):
    """Register a new user (compatible with frontend format).
    
    Security: All new users are created with 'customer' role.
    The role field is not accepted from the client and is hard-coded server-side
    to prevent privilege escalation attacks.
    """
    # Check if user exists
    existing = db.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        return {
            "success": False,
            "error": "Email already registered"
        }
    
    # Hash password
    hashed_password = hash_password(user_in.password)
    
    # Create new user with role="customer" (hard-coded for security)
    new_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        role="customer",  # <--- 这就是真正的修复！强制设置为 customer
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token for immediate authentication
    access_token = create_access_token(
        {"sub": str(new_user.id), "email": new_user.email, "id": new_user.id, "role": new_user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    # Return frontend-compatible response
    return {
        "success": True,
        "token": access_token,
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role,
        }
    }


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    # OAuth2PasswordRequestForm provides username and password fields
    user = db.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(
        {"sub": str(user.id), "email": user.email, "id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)


@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }


