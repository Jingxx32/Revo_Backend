import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.database import create_db_and_tables
from app.routers import auth, products, cart, orders, tradein, internal, categories, users, locations, address

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
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve static images for testing
if os.path.exists("static/images"):
    app.mount("/static/images", StaticFiles(directory="static/images"), name="static_images")

# Prevent noisy 404s for favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

#  Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(tradein.router)
app.include_router(internal.router)
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(address.router)

# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(products.router, prefix="/api/products", tags=["Products"])
# app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
# app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
# app.include_router(tradein.router, prefix="/api/tradein", tags=["Trade-in"])
# app.include_router(internal.router, prefix="/api/internal", tags=["Internal"])