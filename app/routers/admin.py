from typing import Optional, Dict, List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app.core.security import get_current_admin
from app.db.database import get_session
from app.db.models import (
    Evaluation,
    Order,
    OrderItem,
    Payment,
    PickupRequest,
    User,
)


router = APIRouter(prefix="/api/admin", tags=["Admin"])


class OrderUpdatePayload(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class TradeinEvaluationPayload(BaseModel):
    final_offer: float
    notes: Optional[str] = None
    status: str
    evaluation_cost: Optional[float] = None
    diagnostics: Optional[Dict[str, Any]] = None
    parts_replaced: Optional[List[str]] = None


# Sales Orders Management

@router.get("/orders", include_in_schema=False)
def list_orders(
    admin: User = Depends(get_current_admin),
    session=Depends(get_session),
):
    """
    Get all orders with customer basic info (joined with users).
    """
    stmt = select(Order, User).join(User, User.id == Order.user_id)
    rows = session.exec(stmt).all()

    results = []
    for order, user in rows:
        results.append(
            {
                "order": {
                    "id": order.id,
                    "user_id": order.user_id,
                    "status": order.status,
                    "subtotal": order.subtotal,
                    "tax": order.tax,
                    "shipping_fee": order.shipping_fee,
                    "total": order.total,
                    "notes": order.notes,
                    "shipping_address_json": order.shipping_address_json,
                    "created_at": order.created_at,
                },
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                },
            }
        )

    return results


@router.put("/orders/{order_id}", include_in_schema=False)
def update_order(
    order_id: int,
    payload: OrderUpdatePayload,
    admin: User = Depends(get_current_admin),
    session=Depends(get_session),
):
    """
    Update order status and notes.
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if payload.status is not None:
        order.status = payload.status
    if payload.notes is not None:
        order.notes = payload.notes

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
def delete_order(
    order_id: int,
    admin: User = Depends(get_current_admin),
    session=Depends(get_session),
):
    """
    Delete an order (and its dependent items/payments to avoid FK issues).
    """
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Delete order items and payments explicitly (if any)
    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()
    for item in order_items:
        session.delete(item)

    payments = session.exec(
        select(Payment).where(Payment.order_id == order_id)
    ).all()
    for payment in payments:
        session.delete(payment)

    session.delete(order)
    session.commit()
    return None


# Trade-in Orders Management

@router.get("/tradeins")
def list_tradeins(
    admin: User = Depends(get_current_admin),
    session=Depends(get_session),
):
    """
    List all pickup requests with optional evaluation info and user info
    (LEFT OUTER JOIN on evaluations and users).
    """
    stmt = (
        select(PickupRequest, Evaluation, User)
        .join(User, User.id == PickupRequest.user_id)
        .join(Evaluation, Evaluation.pickup_id == PickupRequest.id, isouter=True)
    )
    rows = session.exec(stmt).all()

    results = []
    for pickup, evaluation, user in rows:
        results.append(
            {
                "pickup": {
                    "id": pickup.id,
                    "user_id": pickup.user_id,
                    "brand_id": pickup.brand_id,
                    "model_text": pickup.model_text,
                    "storage": pickup.storage,
                    "condition": pickup.condition,
                    "additional_info": pickup.additional_info,
                    "photos": pickup.photos_json or [],
                    "address_json": pickup.address_json,
                    "created_at": pickup.created_at,
                    "scheduled_at": pickup.scheduled_at,
                    "deposit_amount": pickup.deposit_amount,
                    "status": pickup.status,
                    "notes": pickup.notes,
                    "estimated_price": pickup.estimated_price,
                },
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                },
                "evaluation": {
                    "id": evaluation.id,
                    "pickup_id": evaluation.pickup_id,
                    "tester_id": evaluation.tester_id,
                    "final_offer": evaluation.final_offer,
                    "notes": evaluation.notes,
                    "created_at": evaluation.created_at,
                }
                if evaluation
                else None,
            }
        )

    return results


@router.put("/tradeins/{pickup_id}/evaluate")
def evaluate_tradein(
    pickup_id: int,
    payload: TradeinEvaluationPayload,
    admin: User = Depends(get_current_admin),
    session=Depends(get_session),
):
    """
    Create or update evaluation for a pickup request and update pickup status.
    """
    pickup = session.get(PickupRequest, pickup_id)
    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found"
        )

    # Find existing evaluation (if any)
    evaluation = session.exec(
        select(Evaluation).where(Evaluation.pickup_id == pickup_id)
    ).first()

    if evaluation:
        evaluation.final_offer = payload.final_offer
        evaluation.notes = payload.notes
        evaluation.tester_id = admin.id
        evaluation.evaluation_cost = payload.evaluation_cost
        evaluation.diagnostics_json = payload.diagnostics
        evaluation.parts_replaced_json = payload.parts_replaced
        session.add(evaluation)
    else:
        evaluation = Evaluation(
            pickup_id=pickup_id,
            tester_id=admin.id,
            final_offer=payload.final_offer,
            notes=payload.notes,
            evaluation_cost=payload.evaluation_cost,
            diagnostics_json=payload.diagnostics,
            parts_replaced_json=payload.parts_replaced,
        )
        session.add(evaluation)

    # Update pickup request status
    pickup.status = payload.status
    session.add(pickup)

    session.commit()
    session.refresh(pickup)
    session.refresh(evaluation)

    return {
        "pickup": pickup,
        "evaluation": evaluation,
    }


@router.delete("/tradeins/{pickup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tradein(
    pickup_id: int,
    admin: User = Depends(get_current_admin),
    session=Depends(get_session),
):
    """
    Delete a pickup request (and its evaluations to avoid FK issues).
    """
    pickup = session.get(PickupRequest, pickup_id)
    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found"
        )

    evaluations = session.exec(
        select(Evaluation).where(Evaluation.pickup_id == pickup_id)
    ).all()
    for ev in evaluations:
        session.delete(ev)

    session.delete(pickup)
    session.commit()
    return None

