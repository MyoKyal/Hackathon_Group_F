from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.geo import extract_lat_lng, make_point
from app.models.delivery import Delivery, DeliveryStatus
from app.models.donation import Donation, DonationStatus
from app.models.donation_pickup_decline import DonationPickupDecline
from app.models.enums import ItemCategory
from app.models.receiver_request import ReceiverRequest, RequestStatus
from app.models.user import User, VolunteerStatus
from app.models.volunteer_decline import VolunteerDecline
from app.models.warehouse import Warehouse, WarehouseInventory
from app.schemas.auth import UserResponse
from app.schemas.delivery import (
    AssignmentResponse,
    DeliveryDetailResponse,
    DeliverySummary,
    DonationSummary,
    MatchCardResponse,
    ReceiverSummary,
)
from app.schemas.donation import DonationResponse
from app.schemas.volunteer import VolunteerApplyRequest
from app.schemas.warehouse import WarehouseSummary
from app.services.matching import orchestrator
from app.services.matching.orchestrator import (
    get_current_volunteer_offer,
    select_next_volunteer_for_delivery,
    select_volunteer_for_delivery,
)
from app.services.matching.stage1_rules import TRANSPORT_CAPACITY_KG


def _donation_summary(db: Session, donation: Donation) -> DonationSummary:
    lat, lng = extract_lat_lng(db, donation.pickup_location)
    return DonationSummary(
        id=donation.id,
        item_name=donation.item_name,
        item_category=donation.item_category,
        quantity=donation.quantity,
        pickup_lat=lat,
        pickup_lng=lng,
    )


def _warehouse_summary(db: Session, warehouse_id: UUID) -> WarehouseSummary:
    warehouse = db.get(Warehouse, warehouse_id)
    lat, lng = extract_lat_lng(db, warehouse.location)
    return WarehouseSummary(id=warehouse.id, name=warehouse.name, lat=lat, lng=lng)


def _donation_response(db: Session, donation: Donation) -> DonationResponse:
    lat, lng = extract_lat_lng(db, donation.pickup_location)
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
        warehouse=_warehouse_summary(db, donation.warehouse_id),
        pickup_status=donation.pickup_status,
        pickup_volunteer_id=donation.pickup_volunteer_id,
        pickup_stage1_score=donation.pickup_stage1_score,
        pickup_gemini_reasoning=donation.pickup_gemini_reasoning,
        pickup_volunteer_confirmed=donation.pickup_volunteer_confirmed,
        pickup_completed_at=donation.pickup_completed_at,
        created_at=donation.created_at,
    )


def _increment_inventory(
    db: Session, warehouse_id: UUID, category: ItemCategory, delta: int
) -> None:
    row = db.scalar(
        select(WarehouseInventory)
        .where(
            WarehouseInventory.warehouse_id == warehouse_id,
            WarehouseInventory.category == category,
        )
        .with_for_update()
    )
    if row is None:
        row = WarehouseInventory(warehouse_id=warehouse_id, category=category, quantity=0)
        db.add(row)
        db.flush()
    row.quantity = max(0, row.quantity + delta)


def _can_access_delivery(db: Session, delivery: Delivery, user: User) -> bool:
    if user.is_admin:
        return True
    donation = db.get(Donation, delivery.donation_id)
    if donation and donation.donor_id == user.id:
        return True
    if delivery.receiver_id == user.id:
        return True
    if delivery.volunteer_id == user.id:
        return True
    return False


def get_delivery_detail(db: Session, user: User, delivery_id: UUID) -> DeliveryDetailResponse:
    delivery = db.get(Delivery, delivery_id)
    if delivery is None or not _can_access_delivery(db, delivery, user):
        raise NotFoundError("Delivery not found")

    donation = db.get(Donation, delivery.donation_id)
    receiver = db.get(User, delivery.receiver_id)
    if donation is None or receiver is None:
        raise NotFoundError("Delivery not found")

    return DeliveryDetailResponse(
        id=delivery.id,
        donation_id=delivery.donation_id,
        receiver_request_id=delivery.receiver_request_id,
        receiver_id=delivery.receiver_id,
        volunteer_id=delivery.volunteer_id,
        stage1_score=delivery.stage1_score,
        gemini_reasoning=delivery.gemini_reasoning,
        status=delivery.status,
        volunteer_confirmed=delivery.volunteer_confirmed,
        receiver_confirmed=delivery.receiver_confirmed,
        created_at=delivery.created_at,
        completed_at=delivery.completed_at,
        donation=_donation_summary(db, donation),
        receiver=ReceiverSummary(id=receiver.id, full_name=receiver.full_name),
    )


def list_matches(db: Session, user: User, all_matches: bool) -> list[MatchCardResponse]:
    donor = aliased(User)
    receiver = aliased(User)
    stmt = (
        select(Delivery, Donation, donor.full_name, receiver.full_name, ReceiverRequest)
        .join(Donation, Donation.id == Delivery.donation_id)
        .join(donor, donor.id == Donation.donor_id)
        .join(receiver, receiver.id == Delivery.receiver_id)
        .outerjoin(ReceiverRequest, ReceiverRequest.id == Delivery.receiver_request_id)
        .order_by(Delivery.created_at.desc())
    )
    if not all_matches:
        stmt = stmt.where(
            (Donation.donor_id == user.id) | (Delivery.receiver_id == user.id)
        )

    rows = db.execute(stmt).all()
    return [
        MatchCardResponse(
            id=delivery.id,
            status=delivery.status,
            created_at=delivery.created_at,
            stage1_score=delivery.stage1_score,
            gemini_reasoning=delivery.gemini_reasoning,
            donation_item_name=donation.item_name,
            donation_quantity=donation.quantity,
            donor_name=donor_name,
            request_item_name=request.item_name if request else None,
            request_quantity_needed=request.quantity_needed if request else None,
            receiver_name=receiver_name,
        )
        for delivery, donation, donor_name, receiver_name, request in rows
    ]


def _maybe_complete_delivery(db: Session, delivery: Delivery) -> None:
    if not (delivery.volunteer_confirmed and delivery.receiver_confirmed):
        return

    delivery.status = DeliveryStatus.completed
    delivery.completed_at = datetime.now(timezone.utc)

    donation = db.get(Donation, delivery.donation_id)
    if donation:
        donation.status = DonationStatus.completed
        _increment_inventory(db, donation.warehouse_id, donation.item_category, delta=-1)

    if delivery.receiver_request_id:
        request = db.get(ReceiverRequest, delivery.receiver_request_id)
        if request:
            request.status = RequestStatus.fulfilled

    if delivery.volunteer_id:
        volunteer = db.get(User, delivery.volunteer_id)
        if volunteer:
            elapsed_minutes = (delivery.completed_at - delivery.created_at).total_seconds() / 60.0
            old_count = volunteer.completed_deliveries
            volunteer.avg_delivery_time_minutes = (
                (volunteer.avg_delivery_time_minutes or 0.0) * old_count + elapsed_minutes
            ) / (old_count + 1)
            volunteer.completed_deliveries += 1
            volunteer.active_deliveries = max(0, volunteer.active_deliveries - 1)


def confirm_volunteer(db: Session, user: User, delivery_id: UUID) -> DeliverySummary:
    delivery = db.get(Delivery, delivery_id)
    if delivery is None or delivery.volunteer_id != user.id:
        raise NotFoundError("Delivery not found")

    if delivery.status != DeliveryStatus.in_transit:
        raise ForbiddenError("Delivery is not in transit", "invalid_delivery_state")

    delivery.volunteer_confirmed = True
    _maybe_complete_delivery(db, delivery)
    db.commit()
    db.refresh(delivery)
    return DeliverySummary.model_validate(delivery)


def confirm_receiver(db: Session, user: User, delivery_id: UUID) -> DeliverySummary:
    delivery = db.get(Delivery, delivery_id)
    if delivery is None or delivery.receiver_id != user.id:
        raise NotFoundError("Delivery not found")

    if delivery.status not in (DeliveryStatus.in_transit, DeliveryStatus.completed):
        raise ForbiddenError("Delivery is not in transit", "invalid_delivery_state")

    delivery.receiver_confirmed = True
    _maybe_complete_delivery(db, delivery)
    db.commit()
    db.refresh(delivery)
    return DeliverySummary.model_validate(delivery)


def apply_volunteer(db: Session, user: User, payload: VolunteerApplyRequest) -> VolunteerStatus:
    if user.volunteer_status in (VolunteerStatus.pending, VolunteerStatus.approved):
        raise ConflictError("Volunteer application already submitted", "already_applied")

    user.volunteer_status = VolunteerStatus.pending
    user.is_volunteer = False
    user.base_location = make_point(payload.location.lat, payload.location.lng)
    user.transportation_type = payload.transportation_type
    user.max_carrying_capacity_kg = TRANSPORT_CAPACITY_KG[payload.transportation_type.value]
    user.max_travel_distance_km = payload.max_travel_distance_km
    user.township = payload.township
    user.full_address = payload.full_address
    user.available_days = payload.available_days
    user.available_start_time = payload.available_start_time
    user.available_end_time = payload.available_end_time
    user.preferred_categories = payload.preferred_categories
    db.commit()
    return user.volunteer_status


def approve_volunteer(db: Session, user_id: UUID) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")

    user.volunteer_status = VolunteerStatus.approved
    user.is_volunteer = True
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def revoke_volunteer(db: Session, user_id: UUID) -> UserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")

    user.volunteer_status = VolunteerStatus.rejected
    user.is_volunteer = False
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def list_all_users(db: Session) -> list[UserResponse]:
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [UserResponse.model_validate(u) for u in users]


def _get_current_pickup_offer(db: Session, donation: Donation) -> UUID | None:
    if (
        donation.pickup_status != DeliveryStatus.awaiting_volunteer
        or donation.pickup_volunteer_id is not None
    ):
        return donation.pickup_volunteer_id
    ranked = orchestrator.rank_volunteers_for_pickup(db, donation, limit=1)
    if not ranked:
        return None
    return ranked[0].volunteer_id


def list_pickup_assignments(db: Session, volunteer: User) -> list[AssignmentResponse]:
    donations = db.scalars(
        select(Donation).where(
            Donation.pickup_status.in_(
                [DeliveryStatus.awaiting_volunteer, DeliveryStatus.in_transit]
            )
        )
    ).all()
    results: list[AssignmentResponse] = []

    for donation in donations:
        is_assigned = donation.pickup_volunteer_id == volunteer.id
        is_offer = (
            donation.pickup_status == DeliveryStatus.awaiting_volunteer
            and donation.pickup_volunteer_id is None
            and _get_current_pickup_offer(db, donation) == volunteer.id
        )
        if not (is_assigned or is_offer):
            continue

        results.append(
            AssignmentResponse(
                id=donation.id,
                leg="pickup",
                status=donation.pickup_status,
                volunteer_id=donation.pickup_volunteer_id,
                is_current_offer=is_offer,
                donation=_donation_summary(db, donation),
                receiver=None,
                warehouse=_warehouse_summary(db, donation.warehouse_id),
                stage1_score=donation.pickup_stage1_score,
                gemini_reasoning=donation.pickup_gemini_reasoning,
                volunteer_confirmed=donation.pickup_volunteer_confirmed,
                receiver_confirmed=None,
                created_at=donation.created_at,
            )
        )

    return results


def list_delivery_assignments(db: Session, volunteer: User) -> list[AssignmentResponse]:
    deliveries = db.scalars(select(Delivery)).all()
    results: list[AssignmentResponse] = []

    for delivery in deliveries:
        current_offer = get_current_volunteer_offer(db, delivery)
        is_assigned = delivery.volunteer_id == volunteer.id
        is_offer = (
            delivery.status == DeliveryStatus.awaiting_volunteer
            and current_offer == volunteer.id
            and delivery.volunteer_id is None
        )
        if not (is_assigned or is_offer):
            continue

        donation = db.get(Donation, delivery.donation_id)
        receiver = db.get(User, delivery.receiver_id)
        if donation is None or receiver is None:
            continue

        results.append(
            AssignmentResponse(
                id=delivery.id,
                leg="delivery",
                status=delivery.status,
                volunteer_id=delivery.volunteer_id,
                is_current_offer=is_offer,
                donation=_donation_summary(db, donation),
                receiver=ReceiverSummary(id=receiver.id, full_name=receiver.full_name),
                warehouse=_warehouse_summary(db, donation.warehouse_id),
                stage1_score=delivery.stage1_score,
                gemini_reasoning=delivery.gemini_reasoning,
                volunteer_confirmed=delivery.volunteer_confirmed,
                receiver_confirmed=delivery.receiver_confirmed,
                created_at=delivery.created_at,
            )
        )

    return results


def list_assignments(db: Session, volunteer: User) -> list[AssignmentResponse]:
    return list_pickup_assignments(db, volunteer) + list_delivery_assignments(db, volunteer)


def accept_pickup_assignment(
    db: Session, volunteer: User, donation_id: UUID
) -> DonationResponse:
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise NotFoundError("Donation not found")

    if donation.pickup_volunteer_id is not None and donation.pickup_volunteer_id != volunteer.id:
        raise ConflictError("Pickup already accepted by another volunteer", "already_accepted")

    current_offer = _get_current_pickup_offer(db, donation)
    if donation.pickup_volunteer_id is None and current_offer != volunteer.id:
        raise ForbiddenError("This pickup is not offered to you", "not_current_offer")

    donation.pickup_volunteer_id = volunteer.id
    donation.pickup_status = DeliveryStatus.in_transit
    volunteer.active_deliveries += 1

    db.commit()
    db.refresh(donation)
    return _donation_response(db, donation)


def decline_pickup_assignment(
    db: Session, volunteer: User, donation_id: UUID
) -> DonationResponse:
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise NotFoundError("Donation not found")

    if donation.pickup_volunteer_id is not None:
        raise ConflictError("Pickup already accepted", "already_accepted")

    current_offer = _get_current_pickup_offer(db, donation)
    if current_offer != volunteer.id:
        raise ForbiddenError("This pickup is not offered to you", "not_current_offer")

    db.add(DonationPickupDecline(donation_id=donation.id, volunteer_id=volunteer.id))
    db.flush()
    orchestrator.select_next_volunteer_for_pickup(db, donation.id)
    db.commit()
    db.refresh(donation)
    return _donation_response(db, donation)


def confirm_pickup(db: Session, user: User, donation_id: UUID) -> DonationResponse:
    donation = db.get(Donation, donation_id)
    if donation is None or donation.pickup_volunteer_id != user.id:
        raise NotFoundError("Donation not found")

    if donation.pickup_status != DeliveryStatus.in_transit:
        raise ForbiddenError("Pickup is not in transit", "invalid_pickup_state")

    donation.pickup_status = DeliveryStatus.completed
    donation.pickup_volunteer_confirmed = True
    donation.pickup_completed_at = datetime.now(timezone.utc)

    _increment_inventory(db, donation.warehouse_id, donation.item_category, delta=1)

    volunteer = db.get(User, donation.pickup_volunteer_id)
    if volunteer:
        elapsed_minutes = (
            donation.pickup_completed_at - donation.created_at
        ).total_seconds() / 60.0
        old_count = volunteer.completed_deliveries
        volunteer.avg_delivery_time_minutes = (
            (volunteer.avg_delivery_time_minutes or 0.0) * old_count + elapsed_minutes
        ) / (old_count + 1)
        volunteer.completed_deliveries += 1
        volunteer.active_deliveries = max(0, volunteer.active_deliveries - 1)

    orchestrator._maybe_trigger_leg2_matching(db, donation)

    db.commit()
    db.refresh(donation)
    return _donation_response(db, donation)


def accept_assignment(db: Session, volunteer: User, delivery_id: UUID) -> DeliverySummary:
    delivery = db.get(Delivery, delivery_id)
    if delivery is None:
        raise NotFoundError("Delivery not found")

    if delivery.volunteer_id is not None and delivery.volunteer_id != volunteer.id:
        raise ConflictError("Delivery already accepted by another volunteer", "already_accepted")

    current_offer = get_current_volunteer_offer(db, delivery)
    if delivery.volunteer_id is None and current_offer != volunteer.id:
        raise ForbiddenError("This delivery is not offered to you", "not_current_offer")

    delivery.volunteer_id = volunteer.id
    delivery.status = DeliveryStatus.in_transit
    volunteer.active_deliveries += 1

    donation = db.get(Donation, delivery.donation_id)
    if donation:
        donation.status = DonationStatus.in_transit

    db.commit()
    db.refresh(delivery)
    return DeliverySummary.model_validate(delivery)


def decline_assignment(db: Session, volunteer: User, delivery_id: UUID) -> DeliverySummary:
    delivery = db.get(Delivery, delivery_id)
    if delivery is None:
        raise NotFoundError("Delivery not found")

    if delivery.volunteer_id is not None:
        raise ConflictError("Delivery already accepted", "already_accepted")

    current_offer = get_current_volunteer_offer(db, delivery)
    if current_offer != volunteer.id:
        raise ForbiddenError("This delivery is not offered to you", "not_current_offer")

    db.add(VolunteerDecline(delivery_id=delivery.id, volunteer_id=volunteer.id))
    db.flush()
    select_next_volunteer_for_delivery(db, delivery.id)
    db.commit()
    db.refresh(delivery)
    return DeliverySummary.model_validate(delivery)


def run_volunteer_matching(db: Session, delivery_id: UUID):
    return select_volunteer_for_delivery(db, delivery_id)


def run_next_volunteer_matching(db: Session, delivery_id: UUID):
    return select_next_volunteer_for_delivery(db, delivery_id)
