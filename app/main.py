from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import create_db_and_tables
from app.routers import auth, products, cart, orders, tradein, internal

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

# TODO: Include routers
# from app.routers import users, products, cart, orders, tradein, internal
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(tradein.router)
app.include_router(internal.router)
# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(products.router, prefix="/api/products", tags=["Products"])
# app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
# app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
# app.include_router(tradein.router, prefix="/api/tradein", tags=["Trade-in"])
# app.include_router(internal.router, prefix="/api/internal", tags=["Internal"])

