from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.enums import ItemCategory
from app.models.user import User
from app.schemas.donation import (
    DonationBrowseItem,
    DonationCreate,
    DonationCreateResponse,
    DonationDetailResponse,
    DonationResponse,
    MatchPreviewItem,
)
from app.schemas.route import RouteResponse
from app.services import donation_service, route_service

router = APIRouter(prefix="/donations", tags=["donations"])


@router.post("", response_model=DonationCreateResponse, status_code=201)
def create_donation(
    payload: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return donation_service.create_donation(db, current_user, payload)


@router.get("", response_model=list[DonationResponse])
def list_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return donation_service.list_donations(db, current_user)


@router.get("/all", response_model=list[DonationBrowseItem])
def list_all_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return donation_service.list_all_donations(db)


@router.get("/matches", response_model=list[MatchPreviewItem])
def preview_matches(
    item_name: str = Query(...),
    item_category: ItemCategory = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    description: str | None = Query(None),
    quantity: int = Query(1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return donation_service.preview_matches(
        db, item_name, item_category, description, quantity, lat, lng,
        exclude_user_id=current_user.id,
    )


@router.get("/{donation_id}", response_model=DonationDetailResponse)
def get_donation(
    donation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return donation_service.get_donation(db, current_user, donation_id)


@router.get("/{donation_id}/route", response_model=RouteResponse)
def get_donation_route(
    donation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return route_service.get_pickup_route(db, current_user, donation_id)
