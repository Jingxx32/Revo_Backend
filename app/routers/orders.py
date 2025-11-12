import json
import os
from typing import Optional

import stripe
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from sqlmodel import select

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import Cart, CartItem, Order, OrderItem, Payment, Product, User


router = APIRouter(prefix="/api/orders", tags=["Orders"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


def _get_product_image(product: Product) -> Optional[str]:
    """Extract first image URL from product's images_json."""
    if not product or not product.images_json:
        return None
    
    images = product.images_json
    
    # 如果数据库返回的是字符串(SQLite遗留)，尝试解析
    if isinstance(images, str):
        try:
            images = json.loads(images)
        except:
            return None
            
    # 如果已经是列表(PostgreSQL)，直接使用
    if isinstance(images, list) and len(images) > 0:
        # 确保取出的第一项也是字符串
        return images[0] if isinstance(images[0], str) else None
        
    return None


def _compute_cart_totals(user_id: int, session) -> dict:
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        return {"cart": None, "items": [], "subtotal": 0.0}
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    subtotal = 0.0
    expanded_items = []
    for item in items:
        product = session.get(Product, item.product_id)
        if not product:
            # skip missing products
            continue
        unit_price = product.list_price or product.base_price or 0.0
        line_total = unit_price * item.qty
        subtotal += line_total
        expanded_items.append((item, product, unit_price, line_total))
    return {"cart": cart, "items": expanded_items, "subtotal": subtotal}


@router.post("/")
def create_order(current_user: User = Depends(get_current_user), session=Depends(get_session)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe secret key is not configured")

    totals = _compute_cart_totals(current_user.id, session)
    if not totals["items"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    subtotal = totals["subtotal"]
    tax = 0.0
    shipping_fee = 0.0
    total = subtotal + tax + shipping_fee

    # Create order in pending state
    order = Order(
        user_id=current_user.id,
        status="pending",
        subtotal=subtotal,
        tax=tax,
        shipping_fee=shipping_fee,
        total=total,
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    # Create order items snapshot
    for (item, product, unit_price, line_total) in totals["items"]:
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                title_snapshot=product.title,
                unit_price=unit_price,
                qty=item.qty,
                line_total=line_total,
            )
        )
    session.commit()

    # Create Stripe PaymentIntent
    amount_cents = int(round(total * 100))
    payment_intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        metadata={
            "order_id": str(order.id),
            "user_id": str(current_user.id),
        },
        description=f"Order #{order.id}",
        automatic_payment_methods={"enabled": True},
    )

    # Record payment row (initial state)
    session.add(
        Payment(
            order_id=order.id,
            stripe_pi=payment_intent.id,
            amount=total,
            currency="usd",
            status=payment_intent.status,
        )
    )
    session.commit()

    return {"order_id": order.id, "client_secret": payment_intent.client_secret}


@router.post("/checkout")
def checkout_compatible(
    orderData: dict = Body(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Compatible checkout endpoint for frontend (expects {items, total, paymentMethod})."""
    if not stripe.api_key:
        return {
            "success": False,
            "error": "Stripe secret key is not configured"
        }
    
    # Extract items from orderData
    items = orderData.get("items", [])
    if not items:
        return {
            "success": False,
            "error": "Cart is empty"
        }
    
    # Calculate totals
    subtotal = sum(item.get("price", 0) * item.get("quantity", 0) for item in items)
    tax = 0.0  # Frontend calculates tax
    shipping_fee = 0.0
    total = orderData.get("total", subtotal + tax + shipping_fee)
    
    # Create order
    order = Order(
        user_id=current_user.id,
        status="pending",
        subtotal=subtotal,
        tax=tax,
        shipping_fee=shipping_fee,
        total=total,
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Create order items
    for item in items:
        product = session.get(Product, item.get("id"))
        if product:
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    title_snapshot=item.get("name", product.title),
                    unit_price=item.get("price", 0),
                    qty=item.get("quantity", 1),
                    line_total=item.get("price", 0) * item.get("quantity", 1),
                )
            )
    session.commit()
    
    # Create Stripe PaymentIntent if using credit card
    payment_method = orderData.get("paymentMethod", "card")
    if payment_method == "card" or payment_method == "credit":
        try:
            amount_cents = int(round(total * 100))
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                metadata={
                    "order_id": str(order.id),
                    "user_id": str(current_user.id),
                },
                description=f"Order #{order.id}",
                automatic_payment_methods={"enabled": True},
            )
            
            session.add(
                Payment(
                    order_id=order.id,
                    stripe_pi=payment_intent.id,
                    amount=total,
                    currency="usd",
                    status=payment_intent.status,
                )
            )
            session.commit()
            
            return {
                "success": True,
                "orderId": f"ORD{order.id}",
                "order_id": order.id,
                "client_secret": payment_intent.client_secret,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Payment processing failed: {str(e)}"
            }
    else:
        # For wallet or COD, mark as paid directly
        order.status = "paid"
        session.add(order)
        session.commit()
        
        return {
            "success": True,
            "orderId": f"ORD{order.id}",
            "order_id": order.id,
        }


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, session=Depends(get_session)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Stripe webhook secret is not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    if event["type"] == "payment_intent.succeeded":
        pi = event["data"]["object"]
        metadata = pi.get("metadata", {})
        order_id: Optional[int] = int(metadata.get("order_id")) if metadata.get("order_id") else None
        if order_id:
            order = session.get(Order, order_id)
            if order and order.status != "paid":
                order.status = "paid"
                # Update or create payment
                payment = session.exec(
                    select(Payment).where(Payment.order_id == order.id, Payment.stripe_pi == pi["id"])
                ).first()
                amount = (pi.get("amount_received") or pi.get("amount") or 0) / 100.0
                currency = pi.get("currency", "usd")
                if payment:
                    payment.status = "succeeded"
                    payment.amount = amount
                    payment.currency = currency
                else:
                    session.add(
                        Payment(
                            order_id=order.id,
                            stripe_pi=pi["id"],
                            amount=amount,
                            currency=currency,
                            status="succeeded",
                        )
                    )
                session.commit()

    return {"received": True}


@router.get("/me")
def get_my_orders(
    status: Optional[str] = None,
    limit: Optional[int] = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Get current user's orders list."""
    stmt = select(Order).where(Order.user_id == current_user.id)
    
    # Filter by status if provided
    if status:
        stmt = stmt.where(Order.status == status)
    
    # Get all orders first
    orders = session.exec(stmt).all()
    
    # Sort by created_at descending (newest first), fallback to id if created_at is None
    orders = sorted(orders, key=lambda o: (o.created_at or ""), reverse=True)
    
    # Apply pagination after sorting
    if offset:
        orders = orders[offset:]
    if limit:
        orders = orders[:limit]
    
    # Format response with order items
    result = []
    for order in orders:
        # Get order items
        order_items = session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        ).all()
        
        items = []
        for item in order_items:
            product = session.get(Product, item.product_id)
            items.append({
                "product_id": item.product_id,
                "title": item.title_snapshot,
                "unit_price": item.unit_price,
                "qty": item.qty,
                "line_total": item.line_total,
                "product": {
                    "id": product.id if product else None,
                    "title": product.title if product else item.title_snapshot,
                    "image": _get_product_image(product) if product else None,
                } if product else None,
            })
        
        # Get payment information (get the most recent one)
        payments = session.exec(
            select(Payment).where(Payment.order_id == order.id)
        ).all()
        payment = sorted(payments, key=lambda p: p.id or 0, reverse=True)[0] if payments else None
        
        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "subtotal": order.subtotal,
            "tax": order.tax,
            "shipping_fee": order.shipping_fee,
            "total": order.total,
            "created_at": order.created_at,
            "items": items,
            "payment": {
                "status": payment.status,
                "amount": payment.amount,
                "currency": payment.currency,
            } if payment else None,
        })
    
    return result


