from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.delivery import DeliveryDetailResponse, DeliverySummary
from app.services import delivery_service

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("/{delivery_id}", response_model=DeliveryDetailResponse)
def get_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.get_delivery_detail(db, current_user, delivery_id)


@router.post("/{delivery_id}/confirm-volunteer", response_model=DeliverySummary)
def confirm_volunteer(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.confirm_volunteer(db, current_user, delivery_id)


@router.post("/{delivery_id}/confirm-receiver", response_model=DeliverySummary)
def confirm_receiver(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.confirm_receiver(db, current_user, delivery_id)
