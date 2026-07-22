from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, require_admin
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.delivery import AssignmentResponse, DeliverySummary
from app.schemas.donation import DonationResponse
from app.schemas.volunteer import VolunteerApplyRequest, VolunteerApplyResponse
from app.services import delivery_service

router = APIRouter(prefix="/volunteers", tags=["volunteers"])


@router.post("/apply", response_model=VolunteerApplyResponse)
def apply_volunteer(
    payload: VolunteerApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    status_value = delivery_service.apply_volunteer(db, current_user, payload)
    return VolunteerApplyResponse(volunteer_status=status_value)


@router.post("/{user_id}/approve", response_model=UserResponse)
def approve_volunteer(
    user_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return delivery_service.approve_volunteer(db, user_id)


@router.post("/{user_id}/revoke", response_model=UserResponse)
def revoke_volunteer(
    user_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return delivery_service.revoke_volunteer(db, user_id)


@router.get("/users", response_model=list[UserResponse])
def list_all_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return delivery_service.list_all_users(db)


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


@router.post("/pickups/{donation_id}/accept", response_model=DonationResponse)
def accept_pickup(
    donation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.accept_pickup_assignment(db, current_user, donation_id)


@router.post("/pickups/{donation_id}/decline", response_model=DonationResponse)
def decline_pickup(
    donation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.decline_pickup_assignment(db, current_user, donation_id)


@router.post("/pickups/{donation_id}/confirm", response_model=DonationResponse)
def confirm_pickup(
    donation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.confirm_pickup(db, current_user, donation_id)
