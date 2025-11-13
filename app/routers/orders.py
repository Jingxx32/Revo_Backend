import json
import os
from typing import Optional

import stripe
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from sqlmodel import select

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import Cart, CartItem, Order, OrderItem, Payment, Product, User
from app.schemas.order import CheckoutRequest, OrderCreate, ShippingAddressSchema


router = APIRouter(prefix="/api/orders", tags=["Orders"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


def _update_user_info_from_shipping_address(user: User, shipping_address: Optional[ShippingAddressSchema], session) -> None:
    """Update user information from shipping address if user info is empty."""
    if not shipping_address:
        return
    
    updated = False
    
    # Update full_name if empty
    if not user.full_name and shipping_address.fullName:
        user.full_name = shipping_address.fullName
        updated = True
    
    # Update phone_number if empty
    if not user.phone_number and shipping_address.phone:
        user.phone_number = shipping_address.phone
        updated = True
    
    # Commit changes if any updates were made
    if updated:
        session.add(user)
        session.commit()


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


def _check_and_deduct_inventory(items: list, session) -> None:
    """Check inventory and deduct stock for order items.
    
    Args:
        items: List of items, each containing (item, product, unit_price, line_total) for create_order
               OR list of CartItemSchema objects for checkout_compatible
        session: Database session
        
    Raises:
        HTTPException: If any product has insufficient inventory
    """
    for item_data in items:
        # Handle different item formats
        if isinstance(item_data, tuple) and len(item_data) == 4:
            # Format from _compute_cart_totals: (item, product, unit_price, line_total)
            cart_item, product, unit_price, line_total = item_data
            request_qty = cart_item.qty
            product_id = product.id
            product_title = product.title
        else:
            # Format from checkout_compatible: CartItemSchema object
            product_id = item_data.id if hasattr(item_data, 'id') else item_data.get('id')
            request_qty = item_data.quantity if hasattr(item_data, 'quantity') else item_data.get('quantity', 1)
            
            product = session.get(Product, product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {product_id} not found"
                )
            product_title = product.title
        
        # Check inventory
        if product.qty < request_qty:
            available_qty = product.qty
            if available_qty == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product '{product_title}' is out of stock"
                )
            else:
                # Format error message as requested: "Product 'iPhone 14' is out of stock (Only 2 left)"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product '{product_title}' is out of stock (Only {available_qty} left)"
                )
        
        # Deduct inventory
        product.qty -= request_qty
        session.add(product)


@router.post("/")
def create_order(
    order_create: OrderCreate = Body(None),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Create order from cart with optional shipping address."""
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe secret key is not configured")

    totals = _compute_cart_totals(current_user.id, session)
    if not totals["items"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    subtotal = totals["subtotal"]
    tax = 0.0
    shipping_fee = 0.0
    total = subtotal + tax + shipping_fee

    # Convert shippingAddress to dict for JSON storage
    shipping_address_json = None
    if order_create and order_create.shippingAddress:
        shipping_address_json = order_create.shippingAddress.model_dump(exclude_none=True)
        # Update user info from shipping address if empty
        _update_user_info_from_shipping_address(current_user, order_create.shippingAddress, session)

    # Check and deduct inventory BEFORE creating order
    _check_and_deduct_inventory(totals["items"], session)

    # Create order in pending state
    order = Order(
        user_id=current_user.id,
        status="pending",
        subtotal=subtotal,
        tax=tax,
        shipping_fee=shipping_fee,
        total=total,
        shipping_address_json=shipping_address_json,
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
    orderData: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Compatible checkout endpoint for frontend (expects {items, total, paymentMethod, shippingAddress})."""
    if not stripe.api_key:
        return {
            "success": False,
            "error": "Stripe secret key is not configured"
        }
    
    # Extract items from orderData
    items = orderData.items
    if not items:
        return {
            "success": False,
            "error": "Cart is empty"
        }
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in items)
    tax = 0.0  # Frontend calculates tax
    shipping_fee = 0.0
    total = orderData.total  # total is now float type in CheckoutRequest
    
    # Convert shippingAddress to dict for JSON storage
    shipping_address_json = None
    if orderData.shippingAddress:
        shipping_address_json = orderData.shippingAddress.model_dump(exclude_none=True)
        # Update user info from shipping address if empty
        _update_user_info_from_shipping_address(current_user, orderData.shippingAddress, session)
    
    try:
        # Check and deduct inventory BEFORE creating order
        _check_and_deduct_inventory(items, session)
        
        # Create order
        order = Order(
            user_id=current_user.id,
            status="pending",
            subtotal=subtotal,
            tax=tax,
            shipping_fee=shipping_fee,
            total=total,
            shipping_address_json=shipping_address_json,
        )
        session.add(order)
        
        # Create order items
        for item in items:
            product = session.get(Product, item.id)
            if not product:
                # This should not happen if inventory check passed, but add safety check
                session.rollback()
                return {
                    "success": False,
                    "error": f"Product with ID {item.id} not found. Please refresh and try again."
                }
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    title_snapshot=item.name or product.title,
                    unit_price=item.price,
                    qty=item.quantity,
                    line_total=item.price * item.quantity,
                )
            )
        
        # Create Stripe PaymentIntent if using credit card
        payment_method = orderData.paymentMethod
        payment_intent = None
        
        if payment_method == "card" or payment_method == "credit":
            try:
                # Flush to get order.id without committing
                session.flush()
                
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
            except Exception as e:
                session.rollback()
                return {
                    "success": False,
                    "error": f"Payment processing failed: {str(e)}"
                }
        else:
            # For wallet or COD, mark as paid directly
            order.status = "paid"
        
        # Commit all changes in one transaction
        session.commit()
        session.refresh(order)
        
        # Return response based on payment method
        if payment_method == "card" or payment_method == "credit":
            return {
                "success": True,
                "orderId": f"ORD{order.id}",
                "order_id": order.id,
                "client_secret": payment_intent.client_secret,
            }
        else:
            return {
                "success": True,
                "orderId": f"ORD{order.id}",
                "order_id": order.id,
            }
            
    except HTTPException as e:
        # Re-raise HTTPException (for inventory errors)
        session.rollback()
        raise
    except Exception as e:
        # Handle any other errors
        session.rollback()
        return {
            "success": False,
            "error": f"Order creation failed: {str(e)}"
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


