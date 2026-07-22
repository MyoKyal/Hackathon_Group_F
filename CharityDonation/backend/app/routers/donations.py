from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.donation import (
    DonationCreate,
    DonationCreateResponse,
    DonationDetailResponse,
    DonationResponse,
    MatchPreviewItem,
)
from app.services import donation_service

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


@router.get("/matches", response_model=list[MatchPreviewItem])
def preview_matches(
    item_name: str = Query(...),
    item_category: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    description: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return donation_service.preview_matches(
        db, item_name, item_category, description, lat, lng
    )


@router.get("/{donation_id}", response_model=DonationDetailResponse)
def get_donation(
    donation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return donation_service.get_donation(db, current_user, donation_id)
