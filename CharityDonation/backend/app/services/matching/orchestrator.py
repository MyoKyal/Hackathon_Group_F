from dataclasses import dataclass
from uuid import UUID

from geoalchemy2.functions import ST_Distance
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.geo import extract_lat_lng, make_point
from app.models.delivery import Delivery, DeliveryStatus
from app.models.donation import Donation, DonationStatus
from app.models.receiver_request import ReceiverRequest, RequestStatus
from app.models.user import User, VolunteerStatus
from app.models.volunteer_decline import VolunteerDecline
from app.services.matching import stage2_gemini
from app.services.matching.stage1_rules import (
    ScoredRequest,
    ScoredVolunteer,
    category_match_score,
    compute_donor_receiver_score,
    keyword_score,
    passes_hard_filter,
)


@dataclass
class DonorReceiverMatchResult:
    donation_id: UUID
    receiver_request_id: UUID | None
    receiver_id: UUID
    stage1_score: float
    gemini_reasoning: str | None
    matched: bool


@dataclass
class VolunteerMatchResult:
    delivery_id: UUID
    volunteer_id: UUID | None
    stage1_score: float | None
    gemini_reasoning: str | None
    matched: bool


SHORTLIST_SIZE = 5
PREVIEW_SIZE = 10


def score_open_requests(
    db: Session,
    item_name: str,
    item_category: str,
    description: str | None,
    pickup_lat: float,
    pickup_lng: float,
    limit: int = PREVIEW_SIZE,
) -> list[ScoredRequest]:
    pickup_point = make_point(pickup_lat, pickup_lng)
    stmt = (
        select(
            ReceiverRequest,
            User.full_name,
            ST_Distance(ReceiverRequest.location, pickup_point).label("distance_meters"),
        )
        .join(User, User.id == ReceiverRequest.requester_id)
        .where(ReceiverRequest.status == RequestStatus.open)
    )
    rows = db.execute(stmt).all()
    scored: list[ScoredRequest] = []

    for request, requester_name, distance_meters in rows:
        cat = category_match_score(item_category, request.item_category)
        kw = keyword_score(item_name, description, request.item_name, request.description)
        if not passes_hard_filter(cat, kw):
            continue
        score = compute_donor_receiver_score(
            item_category,
            item_name,
            description,
            request.item_category,
            request.item_name,
            request.description,
            float(distance_meters),
        )
        scored.append(
            ScoredRequest(
                request_id=request.id,
                requester_name=requester_name,
                item_name=request.item_name,
                distance_meters=float(distance_meters),
                score=score,
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]


def match_donation_to_receiver(db: Session, donation: Donation) -> DonorReceiverMatchResult | None:
    if donation.status != DonationStatus.pending:
        return None

    pickup_lat, pickup_lng = extract_lat_lng(db, donation.pickup_location)
    candidates = score_open_requests(
        db,
        donation.item_name,
        donation.item_category,
        donation.description,
        pickup_lat,
        pickup_lng,
        limit=SHORTLIST_SIZE,
    )
    if not candidates:
        return DonorReceiverMatchResult(
            donation_id=donation.id,
            receiver_request_id=None,
            receiver_id=donation.donor_id,
            stage1_score=0.0,
            gemini_reasoning=None,
            matched=False,
        )

    selected, reasoning = stage2_gemini.select_receiver_request(
        donation.item_name,
        donation.item_category,
        donation.description,
        candidates,
    )
    request = db.get(ReceiverRequest, selected.request_id)
    if request is None:
        return None

    delivery = Delivery(
        donation_id=donation.id,
        receiver_request_id=request.id,
        receiver_id=request.requester_id,
        stage1_score=selected.score,
        gemini_reasoning=reasoning,
        status=DeliveryStatus.awaiting_volunteer,
    )
    donation.status = DonationStatus.matched
    request.status = RequestStatus.matched
    db.add(delivery)
    db.flush()

    select_volunteer_for_delivery(db, delivery.id)

    return DonorReceiverMatchResult(
        donation_id=donation.id,
        receiver_request_id=request.id,
        receiver_id=request.requester_id,
        stage1_score=selected.score,
        gemini_reasoning=reasoning,
        matched=True,
    )


def create_targeted_delivery(
    db: Session, donation: Donation, target_receiver_id: UUID
) -> Delivery:
    delivery = Delivery(
        donation_id=donation.id,
        receiver_request_id=None,
        receiver_id=target_receiver_id,
        status=DeliveryStatus.awaiting_volunteer,
    )
    donation.status = DonationStatus.matched
    db.add(delivery)
    db.flush()
    select_volunteer_for_delivery(db, delivery.id)
    return delivery


def rematch_pending_donations(db: Session) -> list[DonorReceiverMatchResult]:
    pending = db.scalars(
        select(Donation).where(Donation.status == DonationStatus.pending)
    ).all()
    results: list[DonorReceiverMatchResult] = []
    for donation in pending:
        result = match_donation_to_receiver(db, donation)
        if result and result.matched:
            results.append(result)
    return results


def _get_declined_volunteer_ids(db: Session, delivery_id: UUID) -> set[UUID]:
    rows = db.scalars(
        select(VolunteerDecline.volunteer_id).where(
            VolunteerDecline.delivery_id == delivery_id
        )
    ).all()
    return set(rows)


def rank_volunteers_for_delivery(
    db: Session, delivery: Delivery, limit: int = SHORTLIST_SIZE
) -> list[ScoredVolunteer]:
    declined = _get_declined_volunteer_ids(db, delivery.id)
    donation = db.get(Donation, delivery.donation_id)
    if donation is None:
        return []

    pickup_point = donation.pickup_location
    stmt = select(User).where(
        User.is_volunteer.is_(True),
        User.volunteer_status == VolunteerStatus.approved,
        User.is_available.is_(True),
        User.base_location.is_not(None),
    )
    volunteers = db.scalars(stmt).all()
    scored: list[ScoredVolunteer] = []

    for volunteer in volunteers:
        if volunteer.id in declined:
            continue
        distance_meters = db.scalar(
            select(ST_Distance(volunteer.base_location, pickup_point))
        )
        if distance_meters is None:
            continue
        score = 1.0 / (1.0 + float(distance_meters) / 1000.0)
        scored.append(
            ScoredVolunteer(
                volunteer_id=volunteer.id,
                full_name=volunteer.full_name,
                distance_meters=float(distance_meters),
                score=score,
                is_available=volunteer.is_available,
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]


def get_current_volunteer_offer(db: Session, delivery: Delivery) -> UUID | None:
    if delivery.status != DeliveryStatus.awaiting_volunteer or delivery.volunteer_id is not None:
        return delivery.volunteer_id
    ranked = rank_volunteers_for_delivery(db, delivery, limit=1)
    if not ranked:
        return None
    return ranked[0].volunteer_id


def select_volunteer_for_delivery(db: Session, delivery_id: UUID) -> VolunteerMatchResult:
    delivery = db.get(Delivery, delivery_id)
    if delivery is None:
        raise ValueError("Delivery not found")

    if delivery.volunteer_id is not None:
        return VolunteerMatchResult(
            delivery_id=delivery.id,
            volunteer_id=delivery.volunteer_id,
            stage1_score=delivery.stage1_score,
            gemini_reasoning=delivery.gemini_reasoning,
            matched=True,
        )

    donation = db.get(Donation, delivery.donation_id)
    if donation is None:
        raise ValueError("Donation not found")

    candidates = rank_volunteers_for_delivery(db, delivery)
    if not candidates:
        return VolunteerMatchResult(
            delivery_id=delivery.id,
            volunteer_id=None,
            stage1_score=None,
            gemini_reasoning=None,
            matched=False,
        )

    selected, reasoning = stage2_gemini.select_volunteer(
        donation.item_name,
        donation.item_category,
        donation.description,
        candidates,
    )
    delivery.stage1_score = selected.score
    delivery.gemini_reasoning = reasoning
    db.flush()

    return VolunteerMatchResult(
        delivery_id=delivery.id,
        volunteer_id=selected.volunteer_id,
        stage1_score=selected.score,
        gemini_reasoning=reasoning,
        matched=True,
    )


def select_next_volunteer_for_delivery(db: Session, delivery_id: UUID) -> VolunteerMatchResult:
    delivery = db.get(Delivery, delivery_id)
    if delivery is None:
        raise ValueError("Delivery not found")
    delivery.volunteer_id = None
    db.flush()
    return select_volunteer_for_delivery(db, delivery_id)
