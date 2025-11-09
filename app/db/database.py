from sqlmodel import SQLModel, create_engine
from sqlmodel import Session
from app.core.config import settings
import os

# Database configuration
# Get PostgreSQL connection URL from environment variable or settings
database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# Replace postgresql:// with postgresql+psycopg2:// for SQLAlchemy compatibility
# Render and other platforms often provide postgresql:// URLs
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create PostgreSQL engine
engine = create_engine(
    database_url,
    echo=True,  # Set to False in production for better performance
    pool_pre_ping=True,  # Verify connections before using them (helps with connection recovery)
    pool_size=5,  # Number of connections to maintain in the pool
    max_overflow=10  # Maximum number of connections to create beyond pool_size
)


def create_db_and_tables():
    """Create all database tables based on the models."""
    try:
        # Import all models here to ensure they are registered
        from app.db.models import (
            Brand, Category, User, Product, Cart, CartItem,
            Order, OrderItem, Payment, PickupRequest, Evaluation, AuditLog
        )
        
        # Create all tables (if not exists)
        SQLModel.metadata.create_all(engine)
        print("Database and tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        import traceback
        traceback.print_exc()
        raise


def init_db():
    """Initialize the database by creating tables."""
    create_db_and_tables()


def get_session():
    """FastAPI dependency that yields a SQLModel Session bound to our engine."""
    with Session(engine) as session:
        yield session

