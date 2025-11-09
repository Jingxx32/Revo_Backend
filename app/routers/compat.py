"""
Compatibility router for frontend API endpoints.
Maps frontend API calls to backend endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.routers import auth

router = APIRouter(prefix="/api", tags=["Compatibility"])

# Re-export auth endpoints at root level for compatibility
@router.post("/login")
async def login_compatible_root(payload: dict):
    """Compatible login endpoint at /api/login (redirects to /api/auth/login)."""
    # Import here to avoid circular dependency
    from app.routers.auth import login_compatible
    from app.db.database import get_session
    
    session = next(get_session())
    try:
        return await login_compatible(payload, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

