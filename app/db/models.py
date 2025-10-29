from sqlmodel import SQLModel, Field
from typing import Optional


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
    created_at: Optional[str] = Field(default=None)


# Products
class Product(SQLModel, table=True):
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(sa_column_kwargs={"unique": True})
    title: str
    brand_id: Optional[int] = Field(default=None, foreign_key="brands.id")
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    condition: Optional[str] = Field(default=None)  # CHECK: A, B, C
    verified: int = Field(default=0)
    description: Optional[str] = Field(default=None)
    images_json: Optional[str] = Field(default=None)
    cost_components_json: Optional[str] = Field(default=None)
    base_price: Optional[float] = Field(default=None)
    list_price: Optional[float] = Field(default=None)
    resale_price: Optional[float] = Field(default=None)
    qty: int = Field(default=0)
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)


# Carts
class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", sa_column_kwargs={"unique": True})
    updated_at: Optional[str] = Field(default=None)


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
    created_at: Optional[str] = Field(default=None)


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
    created_at: Optional[str] = Field(default=None)


# Pickup / evaluation
class PickupRequest(SQLModel, table=True):
    __tablename__ = "pickup_requests"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    brand_id: Optional[int] = Field(default=None, foreign_key="brands.id")
    model_text: Optional[str] = Field(default=None)
    condition: Optional[str] = Field(default=None)
    address_json: Optional[str] = Field(default=None)
    scheduled_at: Optional[str] = Field(default=None)
    deposit_amount: Optional[float] = Field(default=None)
    status: Optional[str] = Field(default=None)  # CHECK: requested, collected, evaluating, offered, accepted, rejected


class Evaluation(SQLModel, table=True):
    __tablename__ = "evaluations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pickup_id: int = Field(foreign_key="pickup_requests.id")
    tester_id: Optional[int] = Field(default=None, foreign_key="users.id")
    diagnostics_json: Optional[str] = Field(default=None)
    parts_replaced_json: Optional[str] = Field(default=None)
    evaluation_cost: Optional[float] = Field(default=None)
    final_offer: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    created_at: Optional[str] = Field(default=None)


# Audit logs
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: str
    entity: str
    entity_id: Optional[int] = Field(default=None)
    payload_json: Optional[str] = Field(default=None)
    created_at: Optional[str] = Field(default=None)

