from fastapi import FastAPI, Response, Request, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import create_db_and_tables, get_session
from app.db.models import User
from app.schemas.auth import UserLogin
from app.routers import auth, products, cart, orders, tradein, internal, categories, users, locations

# Initialize database
try:
    create_db_and_tables()
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")
    print("Tables may need to be created manually. The application will continue to start.")
    # Don't raise - allow the app to start even if table creation fails
    # Tables will be created on first use or can be created manually

# Initialize FastAPI app
app = FastAPI(
    title="Revo Backend API",
    description="Backend API for Revo C2B2C Electronics Trade-in Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Revo Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health_check():
    """Compatible health check endpoint at /api/health for frontend."""
    return {"status": "healthy"}

# Serve uploaded files
import os
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Prevent noisy 404s for favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# TODO: Include routers
# from app.routers import users, products, cart, orders, tradein, internal
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(tradein.router)
app.include_router(internal.router)
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(locations.router)

# Compatibility endpoints for frontend
@app.post("/api/login")
async def login_compat(user_login: UserLogin, session=Depends(get_session)):
    """Compatible login endpoint at /api/login.
    
    This endpoint is maintained for backward compatibility.
    New code should use /api/auth/login instead.
    
    Args:
        user_login: Login credentials (email and password)
        session: Database session
        
    Returns:
        Login response with success status, token, and user information
    """
    from app.routers.auth import _login_compatible_logic
    
    return _login_compatible_logic(user_login.email, user_login.password, session)


@app.post("/api/estimate")
async def estimate_compat(request: Request, session=Depends(get_session)):
    """Compatible trade-in estimate endpoint at /api/estimate."""
    from app.routers.tradein import get_tradein_estimate
    
    body = await request.json()
    return get_tradein_estimate(body, session=session)


@app.post("/api/pickup/request")
async def pickup_request_compat(
    request: Request,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session)
):
    """Compatible pickup request endpoint at /api/pickup/request."""
    from app.routers.tradein import request_pickup_compatible
    
    body = await request.json()
    return await request_pickup_compatible(body, current_user=current_user, session=session)
# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(products.router, prefix="/api/products", tags=["Products"])
# app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
# app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
# app.include_router(tradein.router, prefix="/api/tradein", tags=["Trade-in"])
# app.include_router(internal.router, prefix="/api/internal", tags=["Internal"])

