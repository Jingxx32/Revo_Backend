from sqlmodel import SQLModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from sqlalchemy import Column, JSON, TIMESTAMP
from sqlalchemy.sql import func


# Core reference tables
class Brand(SQLModel, table=True):
    __tablename__ = "brands"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={"unique": True})


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={"unique": True})


# Users
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column_kwargs={"unique": True})
    password_hash: str
    role: str = Field(default="customer")  # CHECK: customer, admin, evaluator
    created_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now())
    )


# Products
class Product(SQLModel, table=True):
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(sa_column_kwargs={"unique": True})
    title: str
    model: Optional[str] = Field(default=None)  # Product model name (e.g., "iPhone 14", "MacBook Air M2")
    brand_id: Optional[int] = Field(default=None, foreign_key="brands.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    condition: Optional[str] = Field(default=None)  # CHECK: A, B, C
    verified: int = Field(default=0)
    description: Optional[str] = Field(default=None)
    images_json: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    cost_components_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    base_price: Optional[float] = Field(default=None)
    list_price: Optional[float] = Field(default=None)
    resale_price: Optional[float] = Field(default=None)
    qty: int = Field(default=0)
    rating: Optional[float] = Field(default=None)  # Product rating (e.g., 4.8)
    reviews: Optional[int] = Field(default=0)  # Number of reviews
    location: Optional[str] = Field(default=None)  # Location (e.g., "Vancouver Hub", "Ottawa Lab")
    highlights_json: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))  # JSON array of highlights
    city_availability_json: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))  # JSON array of available cities
    created_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now())
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    )


# Carts
class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", sa_column_kwargs={"unique": True})
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    )


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    
    cart_id: int = Field(foreign_key="carts.id", primary_key=True)
    product_id: int = Field(foreign_key="products.id", primary_key=True)
    qty: int


# Orders
class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    status: str = Field(default="pending")  # CHECK: pending, paid, shipped, completed, refunded
    subtotal: float
    tax: float
    shipping_fee: float = Field(default=0)
    total: float
    created_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now())
    )


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    
    order_id: int = Field(foreign_key="orders.id", primary_key=True)
    product_id: int = Field(foreign_key="products.id", primary_key=True)
    title_snapshot: str
    unit_price: float
    qty: int
    line_total: float


# Payments
class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    stripe_pi: str
    amount: float
    currency: str
    status: str
    created_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now())
    )


# Pickup / evaluation
class PickupRequest(SQLModel, table=True):
    __tablename__ = "pickup_requests"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    brand_id: Optional[int] = Field(default=None, foreign_key="brands.id")
    model_text: Optional[str] = Field(default=None)
    storage: Optional[str] = Field(default=None)  # Storage capacity (e.g., "128GB", "256GB", "512GB")
    condition: Optional[str] = Field(default=None)
    additional_info: Optional[str] = Field(default=None)  # Additional information/notes
    photos_json: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))  # JSON array of photo URLs
    address_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    scheduled_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True))
    )
    deposit_amount: Optional[float] = Field(default=None)
    status: Optional[str] = Field(default=None)  # CHECK: requested, collected, evaluating, offered, accepted, rejected


class Evaluation(SQLModel, table=True):
    __tablename__ = "evaluations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pickup_id: int = Field(foreign_key="pickup_requests.id")
    tester_id: Optional[int] = Field(default=None, foreign_key="users.id")
    diagnostics_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    parts_replaced_json: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    evaluation_cost: Optional[float] = Field(default=None)
    final_offer: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    created_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now())
    )


# Audit logs
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: str
    entity: str
    entity_id: Optional[int] = Field(default=None)
    payload_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime | None = Field(
        default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now())
    )

