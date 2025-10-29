from sqlmodel import SQLModel, create_engine
from sqlmodel import Session
from sqlalchemy.pool import StaticPool

# Database configuration
sqlite_file_name = "development.db"
sqlite_url = f"sqlite:///./{sqlite_file_name}"

# Create engine with echo=True for SQL logging
# StaticPool is needed for SQLite to work properly with SQLModel
engine = create_engine(
    sqlite_url, 
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


def create_db_and_tables():
    """Create all database tables based on the models."""
    # Import all models here to ensure they are registered
    from app.db.models import (
        Brand, Category, User, Product, Cart, CartItem,
        Order, OrderItem, Payment, PickupRequest, Evaluation, AuditLog
    )
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("Database and tables created successfully!")


def init_db():
    """Initialize the database by creating tables."""
    create_db_and_tables()


def get_session():
    """FastAPI dependency that yields a SQLModel Session bound to our engine."""
    with Session(engine) as session:
        yield session

