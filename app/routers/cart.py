from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app.db.database import get_session
from app.db.models import Cart, CartItem, Product, User
from app.core.security import get_current_user


router = APIRouter(prefix="/api/cart", tags=["Cart"])


class CartItemCreate(BaseModel):
    product_id: int
    qty: int = 1


class CartItemUpdate(BaseModel):
    qty: int


def _get_or_create_cart(user_id: int, session):
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart


def _serialize_cart(cart: Cart, session):
    # Fetch items
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    result_items = []
    subtotal = 0.0
    for item in items:
        product = session.get(Product, item.product_id)
        unit_price = product.list_price or product.base_price or 0.0 if product else 0.0
        line_total = unit_price * item.qty
        subtotal += line_total
        result_items.append({
            "product_id": item.product_id,
            "title": product.title if product else None,
            "qty": item.qty,
            "unit_price": unit_price,
            "line_total": line_total,
        })
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": result_items,
        "subtotal": subtotal,
    }


@router.get("/")
def get_cart(current_user: User = Depends(get_current_user), session=Depends(get_session)):
    cart = _get_or_create_cart(current_user.id, session)
    return _serialize_cart(cart, session)


@router.get("/count")
def get_cart_count(current_user: User = Depends(get_current_user), session=Depends(get_session)):
    """Get cart item count and total items quantity."""
    cart = _get_or_create_cart(current_user.id, session)
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    
    count = len(items)  # Number of unique products
    total_items = sum(item.qty for item in items)  # Total quantity of all items
    
    return {
        "count": count,
        "total_items": total_items,
    }


@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(payload: CartItemCreate, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    # Validate product
    product = session.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    cart = _get_or_create_cart(current_user.id, session)

    existing = session.exec(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == payload.product_id
        )
    ).first()

    if existing:
        existing.qty += max(1, payload.qty)
    else:
        session.add(CartItem(cart_id=cart.id, product_id=payload.product_id, qty=max(1, payload.qty)))

    session.commit()
    return _serialize_cart(cart, session)


@router.put("/items/{product_id}")
def update_item(product_id: int, payload: CartItemUpdate, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    cart = _get_or_create_cart(current_user.id, session)
    item = session.exec(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart")

    if payload.qty <= 0:
        session.delete(item)
    else:
        item.qty = payload.qty
    session.commit()
    return _serialize_cart(cart, session)


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(product_id: int, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    cart = _get_or_create_cart(current_user.id, session)
    item = session.exec(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
    ).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart")

    session.delete(item)
    session.commit()
    return None


