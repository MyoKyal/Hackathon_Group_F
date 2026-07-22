from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.geo import extract_lat_lng
from app.models.delivery import Delivery, DeliveryStatus
from app.models.donation import Donation, DonationStatus
from app.models.match_proposal import MatchProposal, MatchProposalStatus
from app.models.receiver_request import ReceiverRequest, RequestStatus
from app.models.user import User
from app.schemas.delivery import DonationSummary, ReceiverSummary
from app.schemas.match_proposal import MatchProposalResponse
from app.services.matching.orchestrator import select_volunteer_for_delivery


def _to_response(db: Session, proposal: MatchProposal) -> MatchProposalResponse:
    donation = db.get(Donation, proposal.donation_id)
    receiver = db.get(User, proposal.receiver_id)
    lat, lng = extract_lat_lng(db, donation.pickup_location)
    return MatchProposalResponse(
        id=proposal.id,
        donation_id=proposal.donation_id,
        receiver_request_id=proposal.receiver_request_id,
        receiver_id=proposal.receiver_id,
        stage1_score=proposal.stage1_score,
        gemini_reasoning=proposal.gemini_reasoning,
        status=proposal.status,
        created_at=proposal.created_at,
        donation=DonationSummary(
            id=donation.id,
            item_name=donation.item_name,
            item_category=donation.item_category,
            quantity=donation.quantity,
            pickup_lat=lat,
            pickup_lng=lng,
        ),
        receiver=ReceiverSummary(id=receiver.id, full_name=receiver.full_name),
    )


def list_pending_proposals(db: Session) -> list[MatchProposalResponse]:
    proposals = db.scalars(
        select(MatchProposal).where(MatchProposal.status == MatchProposalStatus.pending)
    ).all()
    return [_to_response(db, p) for p in proposals]


def _get_pending_proposal(db: Session, proposal_id: UUID) -> MatchProposal:
    proposal = db.get(MatchProposal, proposal_id)
    if proposal is None:
        raise NotFoundError("Match proposal not found")
    if proposal.status != MatchProposalStatus.pending:
        raise ConflictError("Match proposal already reviewed")
    return proposal


def approve_proposal(db: Session, proposal_id: UUID) -> MatchProposalResponse:
    proposal = _get_pending_proposal(db, proposal_id)
    donation = db.get(Donation, proposal.donation_id)
    if donation is None:
        raise NotFoundError("Donation not found")
    if donation.status != DonationStatus.pending:
        raise ConflictError("Donation is no longer available to match")

    delivery = Delivery(
        donation_id=donation.id,
        receiver_request_id=proposal.receiver_request_id,
        receiver_id=proposal.receiver_id,
        stage1_score=proposal.stage1_score,
        gemini_reasoning=proposal.gemini_reasoning,
        status=DeliveryStatus.awaiting_volunteer,
    )
    if proposal.receiver_request_id:
        request = db.get(ReceiverRequest, proposal.receiver_request_id)
        if request is not None and request.status != RequestStatus.open:
            raise ConflictError("Receiver request is no longer available to match")
        if request is not None:
            request.status = RequestStatus.matched

    donation.status = DonationStatus.matched

    proposal.status = MatchProposalStatus.approved
    db.add(delivery)
    db.flush()

    select_volunteer_for_delivery(db, delivery.id)
    db.commit()
    db.refresh(proposal)
    return _to_response(db, proposal)


def reject_proposal(db: Session, proposal_id: UUID) -> MatchProposalResponse:
    proposal = _get_pending_proposal(db, proposal_id)
    proposal.status = MatchProposalStatus.rejected
    db.commit()
    db.refresh(proposal)
    return _to_response(db, proposal)


def clear_pending_backlog(db: Session) -> None:
    pending = db.scalars(
        select(MatchProposal).where(MatchProposal.status == MatchProposalStatus.pending)
    ).all()
    for proposal in pending:
        proposal.status = MatchProposalStatus.rejected
    db.commit()

    from app.services.matching.orchestrator import rematch_pending_donations

    rematch_pending_donations(db)
    db.commit()
