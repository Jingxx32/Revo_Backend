import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import Brand, Order, OrderItem, PickupRequest, Product, User


router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me/items")
def get_my_items(
    limit: Optional[int] = Query(50, description="Maximum number of items to return"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Get current user's transaction history (orders and pickup requests)."""
    # Get orders
    orders_stmt = select(Order).where(Order.user_id == current_user.id)
    orders = session.exec(orders_stmt).all()
    
    # Sort by created_at descending (newest first)
    orders = sorted(orders, key=lambda o: (o.created_at or ""), reverse=True)
    
    # Apply pagination
    if offset:
        orders = orders[offset:]
    if limit:
        orders = orders[:limit]
    
    # Format orders
    orders_list = []
    for order in orders:
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
            })
        
        orders_list.append({
            "id": order.id,
            "type": "order",
            "status": order.status,
            "total": order.total,
            "created_at": order.created_at,
            "items": items,
        })
    
    # Get pickup requests
    pickup_stmt = select(PickupRequest).where(PickupRequest.user_id == current_user.id)
    pickups = session.exec(pickup_stmt).all()
    
    # Sort by id descending (newest first)
    pickups = sorted(pickups, key=lambda p: p.id or 0, reverse=True)
    
    # Apply pagination
    if offset:
        pickups = pickups[offset:]
    if limit:
        pickups = pickups[:limit]
    
    # Format pickup requests
    pickups_list = []
    for pickup in pickups:
        brand = session.get(Brand, pickup.brand_id) if pickup.brand_id else None
        pickups_list.append({
            "id": pickup.id,
            "type": "tradein",
            "brand_name": brand.name if brand else None,
            "model_text": pickup.model_text,
            "condition": pickup.condition,
            "status": pickup.status,
            "created_at": pickup.scheduled_at or None,
        })
    
    # Combine and sort by creation time (most recent first)
    all_items = orders_list + pickups_list
    all_items.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    
    # Apply limit to combined list
    if limit:
        all_items = all_items[:limit]
    
    return {
        "orders": orders_list,
        "pickup_requests": pickups_list,
        "total_orders": len(orders_list),
        "total_tradeins": len(pickups_list),
        "all_items": all_items,
    }

