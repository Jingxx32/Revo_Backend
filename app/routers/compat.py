"""
Compatibility router for frontend API endpoints.
Maps frontend API calls to backend endpoints.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Compatibility"])

# Note: Compatibility endpoints have been removed.
# Please use the standard OAuth2 endpoints instead:
# - POST /api/auth/token for authentication

