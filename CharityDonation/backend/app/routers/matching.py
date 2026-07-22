from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.donation import Donation, DonationStatus
from app.models.user import User
from app.services.matching.orchestrator import match_donation_to_receiver
from app.services import delivery_service

# Internal matching endpoints exposed for debugging. No role gate yet — open item.

router = APIRouter(prefix="/matching", tags=["matching"])


class DonationMatchRequest(BaseModel):
    donation_id: UUID


class DeliveryMatchRequest(BaseModel):
    delivery_id: UUID


@router.post("/donor-receiver")
def match_donor_receiver(
    payload: DonationMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    donation = db.get(Donation, payload.donation_id)
    if donation is None:
        return {"matched": False, "reason": "donation_not_found"}
    result = match_donation_to_receiver(db, donation)
    db.commit()
    return result


@router.post("/volunteer")
def match_volunteer(
    payload: DeliveryMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = delivery_service.run_volunteer_matching(db, payload.delivery_id)
    db.commit()
    return result


@router.post("/volunteer/next")
def match_volunteer_next(
    payload: DeliveryMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = delivery_service.run_next_volunteer_matching(db, payload.delivery_id)
    db.commit()
    return result


@router.get("/pending")
def list_pending(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    donations = db.scalars(
        select(Donation).where(Donation.status == DonationStatus.pending)
    ).all()
    return [{"id": d.id, "item_name": d.item_name, "status": d.status.value} for d in donations]
