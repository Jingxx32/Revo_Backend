from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import PickupRequest, User


router = APIRouter(prefix="/api/tradein", tags=["Trade-in"])


class PickupRequestCreate(BaseModel):
    brand_id: int | None = None
    model_text: str | None = None
    condition: str | None = None
    address_json: str | None = None
    scheduled_at: str | None = None


class RespondPayload(BaseModel):
    action: str  # "accept" or "reject"


@router.post("/pickup-requests", status_code=status.HTTP_201_CREATED)
def create_pickup_request(
    payload: PickupRequestCreate,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    pr = PickupRequest(
        user_id=current_user.id,
        brand_id=payload.brand_id,
        model_text=payload.model_text,
        condition=payload.condition,
        address_json=payload.address_json,
        scheduled_at=payload.scheduled_at,
        status="requested",
    )
    session.add(pr)
    session.commit()
    session.refresh(pr)
    return pr


@router.get("/pickup-requests/me")
def list_my_pickups(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    stmt = select(PickupRequest).where(PickupRequest.user_id == current_user.id)
    return session.exec(stmt).all()


@router.post("/pickup-requests/{pickup_id}/respond")
def respond_to_offer(
    pickup_id: int,
    payload: RespondPayload,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    pr = session.get(PickupRequest, pickup_id)
    if not pr or pr.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found")

    action = payload.action.lower().strip()
    if action not in {"accept", "reject"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

    pr.status = "accepted" if action == "accept" else "rejected"
    session.add(pr)
    session.commit()
    session.refresh(pr)
    return pr


