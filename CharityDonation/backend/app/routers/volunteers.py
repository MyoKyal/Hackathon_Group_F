from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.delivery import AssignmentResponse, DeliverySummary
from app.schemas.volunteer import VolunteerApplyResponse
from app.services import delivery_service

router = APIRouter(prefix="/volunteers", tags=["volunteers"])


@router.post("/apply", response_model=VolunteerApplyResponse)
def apply_volunteer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    status_value = delivery_service.apply_volunteer(db, current_user)
    return VolunteerApplyResponse(volunteer_status=status_value)


@router.post("/{user_id}/approve", response_model=UserResponse)
def approve_volunteer(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.approve_volunteer(db, user_id)


@router.get("/assignments", response_model=list[AssignmentResponse])
def list_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.list_assignments(db, current_user)


@router.post("/assignments/{delivery_id}/accept", response_model=DeliverySummary)
def accept_assignment(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.accept_assignment(db, current_user, delivery_id)


@router.post("/assignments/{delivery_id}/decline", response_model=DeliverySummary)
def decline_assignment(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.decline_assignment(db, current_user, delivery_id)
