import os
from typing import Optional

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import select

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import Cart, CartItem, Order, OrderItem, Payment, Product, User


router = APIRouter(prefix="/api/orders", tags=["Orders"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


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


