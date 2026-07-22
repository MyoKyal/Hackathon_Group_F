from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.delivery import DeliveryDetailResponse, DeliverySummary, MatchCardResponse
from app.schemas.route import RouteResponse
from app.services import delivery_service, route_service

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("", response_model=list[MatchCardResponse])
def list_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.list_matches(db, current_user, all_matches=current_user.is_admin)


@router.get("/{delivery_id}", response_model=DeliveryDetailResponse)
def get_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_service.get_delivery_detail(db, current_user, delivery_id)


@router.get("/{delivery_id}/route", response_model=RouteResponse)
def get_delivery_route(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return route_service.get_delivery_route(db, current_user, delivery_id)


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
