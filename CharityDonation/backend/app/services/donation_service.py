from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.geo import extract_lat_lng, make_point
from app.models.delivery import Delivery
from app.models.donation import Donation
from app.models.user import User
from app.schemas.delivery import DeliverySummary
from app.schemas.donation import (
    DonationCreate,
    DonationCreateResponse,
    DonationDetailResponse,
    DonationResponse,
    MatchPreviewItem,
)
from app.services.matching.orchestrator import (
    create_targeted_delivery,
    match_donation_to_receiver,
    score_open_requests,
)


def _donation_response(db: Session, donation: Donation) -> DonationResponse:
    lat, lng = extract_lat_lng(db, donation.pickup_location)
    return DonationResponse(
        id=donation.id,
        donor_id=donation.donor_id,
        item_name=donation.item_name,
        item_category=donation.item_category,
        description=donation.description,
        quantity=donation.quantity,
        pickup_lat=lat,
        pickup_lng=lng,
        target_receiver_id=donation.target_receiver_id,
        status=donation.status,
        created_at=donation.created_at,
    )


def _delivery_summary(delivery: Delivery) -> DeliverySummary:
    return DeliverySummary.model_validate(delivery)


def create_donation(
    db: Session, donor: User, payload: DonationCreate
) -> DonationCreateResponse:
    donation = Donation(
        donor_id=donor.id,
        item_name=payload.item_name,
        item_category=payload.item_category,
        description=payload.description,
        quantity=payload.quantity,
        pickup_location=make_point(payload.pickup_location.lat, payload.pickup_location.lng),
        target_receiver_id=payload.target_receiver_id,
    )
    db.add(donation)
    db.flush()

    delivery: Delivery | None = None
    if payload.target_receiver_id:
        delivery = create_targeted_delivery(db, donation, payload.target_receiver_id)
    else:
        match_donation_to_receiver(db, donation)
        delivery = db.scalar(select(Delivery).where(Delivery.donation_id == donation.id))

    db.commit()
    db.refresh(donation)

    response = _donation_response(db, donation)
    return DonationCreateResponse(
        **response.model_dump(),
        delivery=_delivery_summary(delivery) if delivery else None,
    )


def list_donations(db: Session, donor: User) -> list[DonationResponse]:
    donations = db.scalars(
        select(Donation)
        .where(Donation.donor_id == donor.id)
        .order_by(Donation.created_at.desc())
    ).all()
    return [_donation_response(db, d) for d in donations]


def get_donation(db: Session, donor: User, donation_id: UUID) -> DonationDetailResponse:
    donation = db.get(Donation, donation_id)
    if donation is None or donation.donor_id != donor.id:
        raise NotFoundError("Donation not found")

    delivery = db.scalar(select(Delivery).where(Delivery.donation_id == donation.id))
    response = _donation_response(db, donation)
    return DonationDetailResponse(
        **response.model_dump(),
        delivery=_delivery_summary(delivery) if delivery else None,
    )


def preview_matches(
    db: Session,
    item_name: str,
    item_category: str,
    description: str | None,
    lat: float,
    lng: float,
) -> list[MatchPreviewItem]:
    scored = score_open_requests(db, item_name, item_category, description, lat, lng)
    return [
        MatchPreviewItem(
            request_id=item.request_id,
            requester_name=item.requester_name,
            item_name=item.item_name,
            distance_km=item.distance_meters / 1000.0,
            score=item.score,
        )
        for item in scored
    ]
