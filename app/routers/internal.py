from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import Evaluation, PickupRequest, User


router = APIRouter(prefix="/api/internal", tags=["Internal"])


def get_current_evaluator(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "evaluator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Evaluator role required")
    return current_user


class EvaluationCreate(BaseModel):
    pickup_id: int
    diagnostics_json: str | None = None
    parts_replaced_json: str | None = None
    evaluation_cost: float | None = None
    final_offer: float | None = None
    notes: str | None = None


@router.post("/evaluations", status_code=status.HTTP_201_CREATED)
def create_evaluation(
    payload: EvaluationCreate,
    evaluator: User = Depends(get_current_evaluator),
    session=Depends(get_session),
):
    pr = session.get(PickupRequest, payload.pickup_id)
    if not pr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found")

    ev = Evaluation(
        pickup_id=payload.pickup_id,
        tester_id=evaluator.id,
        diagnostics_json=payload.diagnostics_json,
        parts_replaced_json=payload.parts_replaced_json,
        evaluation_cost=payload.evaluation_cost,
        final_offer=payload.final_offer,
        notes=payload.notes,
    )
    session.add(ev)

    # Update pickup request status to 'offered'
    pr.status = "offered"
    session.add(pr)

    session.commit()
    session.refresh(ev)
    return ev


