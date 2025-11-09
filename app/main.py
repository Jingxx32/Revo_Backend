from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.database import create_db_and_tables
from app.routers import auth, products, cart, orders, tradein, internal, categories, users, locations

# Initialize database
create_db_and_tables()

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
async def login_compat(request: Request):
    """Compatible login endpoint at /api/login."""
    from app.routers.auth import _login_compatible_logic
    from app.db.database import get_session
    
    body = await request.json()
    session = next(get_session())
    email = body.get("email")
    password = body.get("password")
    return _login_compatible_logic(email, password, session)


@app.post("/api/estimate")
async def estimate_compat(request: Request):
    """Compatible trade-in estimate endpoint at /api/estimate."""
    from app.db.database import get_session
    from app.routers.tradein import get_tradein_estimate
    
    body = await request.json()
    session = next(get_session())
    return get_tradein_estimate(body, session=session)


@app.post("/api/pickup/request")
async def pickup_request_compat(request: Request):
    """Compatible pickup request endpoint at /api/pickup/request."""
    from app.routers.tradein import request_pickup_compatible
    from app.core.security import get_current_user
    from app.db.database import get_session
    from fastapi import Depends, Header, HTTPException, status
    from app.db.models import User
    
    body = await request.json()
    session = next(get_session())
    
    # Get user from token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    token = auth_header.replace("Bearer ", "")
    from app.core.security import jwt, SECRET_KEY, ALGORITHM
    from jose import JWTError
    from sqlmodel import select
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    return await request_pickup_compatible(body, current_user=user, session=session)
# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(products.router, prefix="/api/products", tags=["Products"])
# app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
# app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
# app.include_router(tradein.router, prefix="/api/tradein", tags=["Trade-in"])
# app.include_router(internal.router, prefix="/api/internal", tags=["Internal"])

