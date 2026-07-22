from dataclasses import dataclass
from uuid import UUID

from geoalchemy2.functions import ST_Distance
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.geo import extract_lat_lng, make_point
from app.models.delivery import Delivery, DeliveryStatus
from app.models.donation import Donation, DonationStatus
from app.models.donation_pickup_decline import DonationPickupDecline
from app.models.match_proposal import MatchProposal, MatchProposalStatus
from app.models.receiver_request import ReceiverRequest, RequestStatus
from app.models.user import User, VolunteerStatus
from app.models.volunteer_decline import VolunteerDecline
from app.models.warehouse import Warehouse
from app.services import settings_service
from app.services.matching import stage2_gemini
from app.services.matching.stage1_rules import (
    ScoredRequest,
    ScoredVolunteer,
    category_match_score,
    compute_donor_receiver_score,
    compute_volunteer_score,
    keyword_score,
    passes_hard_filter,
    passes_volunteer_mandatory,
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
    donation_quantity: int,
    pickup_lat: float,
    pickup_lng: float,
    limit: int = PREVIEW_SIZE,
    exclude_user_id: UUID | None = None,
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
    if exclude_user_id is not None:
        stmt = stmt.where(ReceiverRequest.requester_id != exclude_user_id)
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
            donation_quantity,
            request.item_category,
            request.item_name,
            request.description,
            request.quantity_needed,
            float(distance_meters),
        )
        scored.append(
            ScoredRequest(
                request_id=request.id,
                requester_name=requester_name,
                item_name=request.item_name,
                quantity_needed=request.quantity_needed,
                distance_meters=float(distance_meters),
                score=score,
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]


def match_donation_to_receiver(db: Session, donation: Donation) -> DonorReceiverMatchResult | None:
    if donation.status != DonationStatus.pending:
        return None

    has_pending_proposal = db.scalar(
        select(MatchProposal.id).where(
            MatchProposal.donation_id == donation.id,
            MatchProposal.status == MatchProposalStatus.pending,
        )
    )
    if has_pending_proposal is not None:
        return None

    pickup_lat, pickup_lng = extract_lat_lng(db, donation.pickup_location)
    candidates = score_open_requests(
        db,
        donation.item_name,
        donation.item_category,
        donation.description,
        donation.quantity,
        pickup_lat,
        pickup_lng,
        limit=SHORTLIST_SIZE,
        exclude_user_id=donation.donor_id,
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
        donation.quantity,
        candidates,
    )
    request = db.get(ReceiverRequest, selected.request_id)
    if request is None:
        return None

    if settings_service.get_settings(db).require_match_approval:
        proposal = MatchProposal(
            donation_id=donation.id,
            receiver_request_id=request.id,
            receiver_id=request.requester_id,
            stage1_score=selected.score,
            gemini_reasoning=reasoning,
        )
        db.add(proposal)
        db.flush()
        return DonorReceiverMatchResult(
            donation_id=donation.id,
            receiver_request_id=request.id,
            receiver_id=request.requester_id,
            stage1_score=selected.score,
            gemini_reasoning=reasoning,
            matched=False,
        )

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


def find_nearest_warehouse(db: Session, pickup_point) -> Warehouse:
    warehouse = db.scalars(
        select(Warehouse).order_by(ST_Distance(Warehouse.location, pickup_point)).limit(1)
    ).first()
    if warehouse is None:
        raise ValueError("No warehouses configured")
    return warehouse


def _get_declined_volunteer_ids(db: Session, delivery_id: UUID) -> set[UUID]:
    rows = db.scalars(
        select(VolunteerDecline.volunteer_id).where(
            VolunteerDecline.delivery_id == delivery_id
        )
    ).all()
    return set(rows)


def _get_declined_pickup_volunteer_ids(db: Session, donation_id: UUID) -> set[UUID]:
    rows = db.scalars(
        select(DonationPickupDecline.volunteer_id).where(
            DonationPickupDecline.donation_id == donation_id
        )
    ).all()
    return set(rows)


def _rank_volunteers(
    db: Session,
    pickup_point_subq,
    donation_weight_kg: float,
    donation_item_category: str,
    extra_leg_km: float,
    excluded_volunteer_ids: set[UUID],
    limit: int,
) -> list[ScoredVolunteer]:
    # Keep both sides of every ST_Distance call as SQL column/subquery references
    # (never round-tripped through a Python-side WKBElement) — passing an
    # ORM-loaded geography value back in as a literal makes PostGIS silently
    # resolve the Geometry (planar degrees) overload instead of Geography
    # (geodesic meters), because WKBElement literals bind without a Geography
    # type annotation.
    stmt = select(
        User, ST_Distance(User.base_location, pickup_point_subq).label("distance_meters")
    ).where(
        User.is_volunteer.is_(True),
        User.volunteer_status == VolunteerStatus.approved,
        User.is_available.is_(True),
        User.base_location.is_not(None),
        User.transportation_type.is_not(None),
        User.max_travel_distance_km.is_not(None),
    )
    rows = db.execute(stmt).all()
    scored: list[ScoredVolunteer] = []

    for volunteer, distance_meters in rows:
        if volunteer.id in excluded_volunteer_ids:
            continue
        if distance_meters is None:
            continue
        distance_km = float(distance_meters) / 1000.0
        total_travel_km = distance_km + extra_leg_km

        if not passes_volunteer_mandatory(
            volunteer.is_available,
            volunteer.max_carrying_capacity_kg,
            donation_weight_kg,
            volunteer.max_travel_distance_km,
            total_travel_km,
        ):
            continue

        score = compute_volunteer_score(
            volunteer.transportation_type.value,
            distance_km,
            volunteer.active_deliveries,
            volunteer.reliability_rating,
            volunteer.preferred_categories,
            donation_item_category,
            volunteer.completed_deliveries,
        )
        scored.append(
            ScoredVolunteer(
                volunteer_id=volunteer.id,
                full_name=volunteer.full_name,
                distance_meters=float(distance_meters),
                score=score,
                is_available=volunteer.is_available,
                transportation_type=volunteer.transportation_type.value,
            )
        )

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]


def rank_volunteers_for_pickup(
    db: Session, donation: Donation, limit: int = SHORTLIST_SIZE
) -> list[ScoredVolunteer]:
    """Leg 1: rank volunteers to carry the item from the donor to the warehouse."""
    declined = _get_declined_pickup_volunteer_ids(db, donation.id)
    donor_point_subq = (
        select(Donation.pickup_location).where(Donation.id == donation.id).scalar_subquery()
    )
    return _rank_volunteers(
        db,
        donor_point_subq,
        donation.weight_kg,
        donation.item_category,
        extra_leg_km=0.0,
        excluded_volunteer_ids=declined,
        limit=limit,
    )


def rank_volunteers_for_delivery(
    db: Session, delivery: Delivery, limit: int = SHORTLIST_SIZE
) -> list[ScoredVolunteer]:
    """Leg 2: rank volunteers to carry the item from the warehouse to the receiver."""
    declined = _get_declined_volunteer_ids(db, delivery.id)
    donation = db.get(Donation, delivery.donation_id)
    if donation is None:
        return []

    warehouse_point_subq = (
        select(Warehouse.location).where(Warehouse.id == donation.warehouse_id).scalar_subquery()
    )

    warehouse_to_receiver_km = 0.0
    if delivery.receiver_request_id is not None:
        receiver_point_subq = (
            select(ReceiverRequest.location)
            .where(ReceiverRequest.id == delivery.receiver_request_id)
            .scalar_subquery()
        )
        meters = db.scalar(select(ST_Distance(warehouse_point_subq, receiver_point_subq)))
        if meters is not None:
            warehouse_to_receiver_km = float(meters) / 1000.0

    return _rank_volunteers(
        db,
        warehouse_point_subq,
        donation.weight_kg,
        donation.item_category,
        extra_leg_km=warehouse_to_receiver_km,
        excluded_volunteer_ids=declined,
        limit=limit,
    )


def get_current_volunteer_offer(db: Session, delivery: Delivery) -> UUID | None:
    if delivery.status != DeliveryStatus.awaiting_volunteer or delivery.volunteer_id is not None:
        return delivery.volunteer_id
    donation = db.get(Donation, delivery.donation_id)
    if donation is None or donation.pickup_status != DeliveryStatus.completed:
        return None
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

    # Leg 2 can't be offered until the item has physically arrived at the warehouse.
    if donation.pickup_status != DeliveryStatus.completed:
        return VolunteerMatchResult(
            delivery_id=delivery.id,
            volunteer_id=None,
            stage1_score=None,
            gemini_reasoning=None,
            matched=False,
        )

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


def select_volunteer_for_pickup(db: Session, donation_id: UUID) -> VolunteerMatchResult:
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise ValueError("Donation not found")

    if donation.pickup_volunteer_id is not None:
        return VolunteerMatchResult(
            delivery_id=donation.id,
            volunteer_id=donation.pickup_volunteer_id,
            stage1_score=donation.pickup_stage1_score,
            gemini_reasoning=donation.pickup_gemini_reasoning,
            matched=True,
        )

    candidates = rank_volunteers_for_pickup(db, donation)
    if not candidates:
        return VolunteerMatchResult(
            delivery_id=donation.id,
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
    donation.pickup_stage1_score = selected.score
    donation.pickup_gemini_reasoning = reasoning
    db.flush()

    return VolunteerMatchResult(
        delivery_id=donation.id,
        volunteer_id=selected.volunteer_id,
        stage1_score=selected.score,
        gemini_reasoning=reasoning,
        matched=True,
    )


def select_next_volunteer_for_pickup(db: Session, donation_id: UUID) -> VolunteerMatchResult:
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise ValueError("Donation not found")
    donation.pickup_volunteer_id = None
    db.flush()
    return select_volunteer_for_pickup(db, donation_id)


def _maybe_trigger_leg2_matching(db: Session, donation: Donation) -> None:
    """Kick off Leg-2 volunteer selection once Leg 1 has completed, if a delivery
    is already waiting on it."""
    delivery = db.scalar(select(Delivery).where(Delivery.donation_id == donation.id))
    if (
        delivery is not None
        and delivery.status == DeliveryStatus.awaiting_volunteer
        and delivery.volunteer_id is None
    ):
        select_volunteer_for_delivery(db, delivery.id)
