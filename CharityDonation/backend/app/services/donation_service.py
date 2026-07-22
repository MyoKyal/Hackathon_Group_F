from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.geo import extract_lat_lng, make_point
from app.models.delivery import Delivery
from app.models.donation import Donation
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.delivery import DeliverySummary
from app.schemas.donation import (
    DonationBrowseItem,
    DonationCreate,
    DonationCreateResponse,
    DonationDetailResponse,
    DonationResponse,
    MatchPreviewItem,
)
from app.schemas.warehouse import WarehouseSummary
from app.services.matching.orchestrator import (
    create_targeted_delivery,
    find_nearest_warehouse,
    match_donation_to_receiver,
    score_open_requests,
    select_volunteer_for_pickup,
)


def _warehouse_summary(db: Session, warehouse: Warehouse) -> WarehouseSummary:
    lat, lng = extract_lat_lng(db, warehouse.location)
    return WarehouseSummary(id=warehouse.id, name=warehouse.name, lat=lat, lng=lng)


def _donation_response(db: Session, donation: Donation) -> DonationResponse:
    lat, lng = extract_lat_lng(db, donation.pickup_location)
    warehouse = db.get(Warehouse, donation.warehouse_id)
    return DonationResponse(
        id=donation.id,
        donor_id=donation.donor_id,
        item_name=donation.item_name,
        item_category=donation.item_category,
        description=donation.description,
        quantity=donation.quantity,
        weight_kg=donation.weight_kg,
        pickup_lat=lat,
        pickup_lng=lng,
        target_receiver_id=donation.target_receiver_id,
        status=donation.status,
        warehouse=_warehouse_summary(db, warehouse),
        pickup_status=donation.pickup_status,
        pickup_volunteer_id=donation.pickup_volunteer_id,
        pickup_stage1_score=donation.pickup_stage1_score,
        pickup_gemini_reasoning=donation.pickup_gemini_reasoning,
        pickup_volunteer_confirmed=donation.pickup_volunteer_confirmed,
        pickup_completed_at=donation.pickup_completed_at,
        created_at=donation.created_at,
    )


def _delivery_summary(delivery: Delivery) -> DeliverySummary:
    return DeliverySummary.model_validate(delivery)


def create_donation(
    db: Session, donor: User, payload: DonationCreate
) -> DonationCreateResponse:
    pickup_point = make_point(payload.pickup_location.lat, payload.pickup_location.lng)
    warehouse = find_nearest_warehouse(db, pickup_point)
    donation = Donation(
        donor_id=donor.id,
        item_name=payload.item_name,
        item_category=payload.item_category,
        description=payload.description,
        quantity=payload.quantity,
        weight_kg=payload.weight_kg,
        pickup_location=pickup_point,
        target_receiver_id=payload.target_receiver_id,
        warehouse_id=warehouse.id,
    )
    db.add(donation)
    db.flush()

    # Leg 1: assign a volunteer to carry the item from the donor to the warehouse.
    # Independent of whether/when a receiver is matched.
    select_volunteer_for_pickup(db, donation.id)

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


def list_all_donations(db: Session) -> list[DonationBrowseItem]:
    rows = db.execute(
        select(Donation, User.full_name)
        .join(User, User.id == Donation.donor_id)
        .order_by(Donation.created_at.desc())
    ).all()
    return [
        DonationBrowseItem(**_donation_response(db, donation).model_dump(), donor_name=donor_name)
        for donation, donor_name in rows
    ]


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
    quantity: int,
    lat: float,
    lng: float,
    exclude_user_id: UUID | None = None,
) -> list[MatchPreviewItem]:
    scored = score_open_requests(
        db, item_name, item_category, description, quantity, lat, lng,
        exclude_user_id=exclude_user_id,
    )
    return [
        MatchPreviewItem(
            request_id=item.request_id,
            requester_name=item.requester_name,
            item_name=item.item_name,
            quantity_needed=item.quantity_needed,
            distance_km=item.distance_meters / 1000.0,
            score=item.score,
        )
        for item in scored
    ]
