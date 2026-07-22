from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.geo import extract_lat_lng
from app.models.delivery import Delivery, DeliveryStatus
from app.models.donation import Donation, DonationStatus
from app.models.receiver_request import ReceiverRequest, RequestStatus
from app.models.user import User, VolunteerStatus
from app.models.volunteer_decline import VolunteerDecline
from app.schemas.auth import UserResponse
from app.schemas.delivery import (
    AssignmentResponse,
    DeliveryDetailResponse,
    DeliverySummary,
    DonationSummary,
    ReceiverSummary,
)
from app.services.matching.orchestrator import (
    get_current_volunteer_offer,
    select_next_volunteer_for_delivery,
    select_volunteer_for_delivery,
)


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


def _can_access_delivery(db: Session, delivery: Delivery, user: User) -> bool:
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


def _maybe_complete_delivery(db: Session, delivery: Delivery) -> None:
    if not (delivery.volunteer_confirmed and delivery.receiver_confirmed):
        return

    delivery.status = DeliveryStatus.completed
    delivery.completed_at = datetime.now(timezone.utc)

    donation = db.get(Donation, delivery.donation_id)
    if donation:
        donation.status = DonationStatus.completed

    if delivery.receiver_request_id:
        request = db.get(ReceiverRequest, delivery.receiver_request_id)
        if request:
            request.status = RequestStatus.fulfilled


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


def apply_volunteer(db: Session, user: User) -> VolunteerStatus:
    if user.volunteer_status in (VolunteerStatus.pending, VolunteerStatus.approved):
        raise ConflictError("Volunteer application already submitted", "already_applied")

    user.volunteer_status = VolunteerStatus.pending
    user.is_volunteer = False
    db.commit()
    return user.volunteer_status


def approve_volunteer(db: Session, user_id: UUID) -> UserResponse:
    # TODO: no permission check — see open items
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")

    user.volunteer_status = VolunteerStatus.approved
    user.is_volunteer = True
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def list_assignments(db: Session, volunteer: User) -> list[AssignmentResponse]:
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
                status=delivery.status,
                volunteer_id=delivery.volunteer_id,
                is_current_offer=is_offer,
                donation=_donation_summary(db, donation),
                receiver=ReceiverSummary(id=receiver.id, full_name=receiver.full_name),
                stage1_score=delivery.stage1_score,
                gemini_reasoning=delivery.gemini_reasoning,
                volunteer_confirmed=delivery.volunteer_confirmed,
                receiver_confirmed=delivery.receiver_confirmed,
                created_at=delivery.created_at,
            )
        )

    return results


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
