"""Manual verification script: drives partial-fulfillment scenarios through the
real service layer (same functions the HTTP routers call) against the live DB
configured in .env. Creates its own users/warehouse-independent data and
cleans up everything it creates at the end, including on failure.

Run: uv run python scripts/verify_partial_fulfillment.py
"""
import sys
import traceback
from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.datastructures import Headers, UploadFile

from app.core.geo import make_point
from app.core.security import hash_password
from app.db import SessionLocal
from app.models.delivery import Delivery, DeliveryStatus
from app.models.donation import Donation, DonationStatus
from app.models.receiver_request import ReceiverRequest, RequestStatus
from app.models.user import User, VolunteerStatus, TransportationType
from app.models.warehouse import Warehouse
from app.services import delivery_service, photo_verification_service
from app.services.matching.orchestrator import match_donation_to_receiver, score_open_requests

created_user_ids: list = []
created_request_ids: list = []
created_donation_ids: list = []
results: list[tuple[str, bool, str]] = []


def record(name: str, passed: bool, detail: str = ""):
    results.append((name, passed, detail))
    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {name}" + (f" -- {detail}" if detail else ""))


def make_user(db: Session, tag: str, volunteer: bool = False) -> User:
    user = User(
        email=f"verify_{tag}_{uuid4().hex[:8]}@test.local",
        password_hash=hash_password("password123"),
        full_name=f"Verify {tag}",
        base_location=make_point(16.8, 96.15),
    )
    if volunteer:
        user.is_volunteer = True
        user.volunteer_status = VolunteerStatus.approved
        user.transportation_type = TransportationType.truck
        user.max_carrying_capacity_kg = None
        user.max_travel_distance_km = 100.0
    db.add(user)
    db.flush()
    created_user_ids.append(user.id)
    return user


def make_request(db: Session, receiver: User, quantity_needed: int, item_name="rice") -> ReceiverRequest:
    r = ReceiverRequest(
        requester_id=receiver.id,
        item_name=item_name,
        item_category="food",
        quantity_needed=quantity_needed,
        location=make_point(16.8, 96.15),
    )
    db.add(r)
    db.flush()
    created_request_ids.append(r.id)
    return r


def make_donation(db: Session, donor: User, quantity: int, warehouse: Warehouse, item_name="rice", target_receiver_id=None) -> Donation:
    d = Donation(
        donor_id=donor.id,
        item_name=item_name,
        item_category="food",
        quantity=quantity,
        weight_kg=1.0,
        pickup_location=make_point(16.8, 96.15),
        warehouse_id=warehouse.id,
        target_receiver_id=target_receiver_id,
    )
    db.add(d)
    db.flush()
    created_donation_ids.append(d.id)
    return d


def _fake_photo() -> UploadFile:
    return UploadFile(file=BytesIO(b"fake-bytes"), headers=Headers({"content-type": "image/jpeg"}))


def complete_delivery_for_donation(db: Session, donation: Donation, volunteer: User, receiver: User):
    """Fast-forward a donation's delivery straight to completed, bypassing
    the pickup leg (not under test here) and photo-verification (mocked)."""
    delivery = db.scalar(select(Delivery).where(Delivery.donation_id == donation.id))
    if delivery is None:
        raise AssertionError(f"no delivery created for donation {donation.id}")
    delivery.volunteer_id = volunteer.id
    delivery.status = DeliveryStatus.in_transit
    donation.pickup_status = DeliveryStatus.completed
    donation.status = DonationStatus.in_transit
    db.flush()

    photo_verification_service.verify_photo = lambda *a, **k: (None, None)
    delivery_service.confirm_volunteer(db, volunteer, delivery.id)
    delivery_service.confirm_receiver(db, receiver, delivery.id, _fake_photo())
    db.refresh(delivery)
    return delivery


def scenario(fn):
    def wrapper(db: Session):
        try:
            fn(db)
        except Exception as exc:
            record(fn.__name__, False, f"EXCEPTION: {exc}\n{traceback.format_exc(limit=3)}")
            db.rollback()
    return wrapper


@scenario
def test_01_exact_match_one_donation_one_request(db: Session):
    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d01")
    receiver = make_user(db, "r01")
    volunteer = make_user(db, "v01", volunteer=True)
    request = make_request(db, receiver, quantity_needed=10, item_name="unique-rice-01")
    donation = make_donation(db, donor, quantity=10, warehouse=warehouse, item_name="unique-rice-01")
    db.commit()

    match_donation_to_receiver(db, donation)
    db.commit()
    db.refresh(request)
    assert request.status == RequestStatus.matched, f"expected matched, got {request.status}"

    complete_delivery_for_donation(db, donation, volunteer, receiver)
    db.commit()
    db.refresh(request)
    record(
        "01 exact 1req/1donation -> fulfilled",
        request.quantity_fulfilled == 10 and request.status == RequestStatus.fulfilled,
        f"quantity_fulfilled={request.quantity_fulfilled} status={request.status}",
    )


@scenario
def test_02_donation_smaller_than_request_stays_open(db: Session):
    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d02")
    receiver = make_user(db, "r02")
    volunteer = make_user(db, "v02", volunteer=True)
    request = make_request(db, receiver, quantity_needed=20, item_name="unique-rice-02")
    donation = make_donation(db, donor, quantity=10, warehouse=warehouse, item_name="unique-rice-02")
    db.commit()

    match_donation_to_receiver(db, donation)
    db.commit()
    complete_delivery_for_donation(db, donation, volunteer, receiver)
    db.commit()
    db.refresh(request)
    record(
        "02 request needs 20, gets 10 -> stays open, fulfilled=10",
        request.quantity_fulfilled == 10 and request.status == RequestStatus.open,
        f"quantity_fulfilled={request.quantity_fulfilled} status={request.status}",
    )


@scenario
def test_03_two_donations_fully_cover_one_request(db: Session):
    warehouse = db.scalar(select(Warehouse).limit(1))
    donor1 = make_user(db, "d03a")
    donor2 = make_user(db, "d03b")
    receiver = make_user(db, "r03")
    volunteer = make_user(db, "v03", volunteer=True)
    request = make_request(db, receiver, quantity_needed=20, item_name="unique-rice-03")
    donation1 = make_donation(db, donor1, quantity=10, warehouse=warehouse, item_name="unique-rice-03")
    db.commit()

    match_donation_to_receiver(db, donation1)
    db.commit()
    complete_delivery_for_donation(db, donation1, volunteer, receiver)
    db.commit()
    db.refresh(request)
    assert request.status == RequestStatus.open, f"expected open after first donation, got {request.status}"

    donation2 = make_donation(db, donor2, quantity=10, warehouse=warehouse, item_name="unique-rice-03")
    db.commit()
    match_donation_to_receiver(db, donation2)
    db.commit()
    complete_delivery_for_donation(db, donation2, volunteer, receiver)
    db.commit()
    db.refresh(request)
    record(
        "03 two 10-donations cover a 20-request -> fulfilled=20",
        request.quantity_fulfilled == 20 and request.status == RequestStatus.fulfilled,
        f"quantity_fulfilled={request.quantity_fulfilled} status={request.status}",
    )


@scenario
def test_04_partially_fulfilled_request_still_appears_in_open_scoring(db: Session):
    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d04")
    receiver = make_user(db, "r04")
    volunteer = make_user(db, "v04", volunteer=True)
    request = make_request(db, receiver, quantity_needed=20, item_name="unique-rice-04")
    donation1 = make_donation(db, donor, quantity=5, warehouse=warehouse, item_name="unique-rice-04")
    db.commit()
    match_donation_to_receiver(db, donation1)
    db.commit()
    complete_delivery_for_donation(db, donation1, volunteer, receiver)
    db.commit()

    scored = score_open_requests(
        db, "unique-rice-04", "food", None, 5, 16.8, 96.15, exclude_user_id=donor.id,
    )
    match = next((s for s in scored if s.request_id == request.id), None)
    record(
        "04 partially-fulfilled request still matchable for top-up",
        match is not None and match.quantity_needed == 15,
        f"match={match}",
    )


@scenario
def test_05_fully_fulfilled_request_excluded_from_open_scoring(db: Session):
    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d05")
    receiver = make_user(db, "r05")
    volunteer = make_user(db, "v05", volunteer=True)
    request = make_request(db, receiver, quantity_needed=10, item_name="unique-rice-05")
    donation = make_donation(db, donor, quantity=10, warehouse=warehouse, item_name="unique-rice-05")
    db.commit()
    match_donation_to_receiver(db, donation)
    db.commit()
    complete_delivery_for_donation(db, donation, volunteer, receiver)
    db.commit()
    db.refresh(request)
    assert request.status == RequestStatus.fulfilled

    scored = score_open_requests(
        db, "unique-rice-05", "food", None, 5, 16.8, 96.15, exclude_user_id=donor.id,
    )
    match = next((s for s in scored if s.request_id == request.id), None)
    record(
        "05 fully-fulfilled request excluded from further matching",
        match is None,
        f"match={match}",
    )


@scenario
def test_06_oversupply_donation_marks_fulfilled_not_overflow_error(db: Session):
    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d06")
    receiver = make_user(db, "r06")
    volunteer = make_user(db, "v06", volunteer=True)
    request = make_request(db, receiver, quantity_needed=10, item_name="unique-rice-06")
    donation = make_donation(db, donor, quantity=25, warehouse=warehouse, item_name="unique-rice-06")
    db.commit()
    match_donation_to_receiver(db, donation)
    db.commit()
    complete_delivery_for_donation(db, donation, volunteer, receiver)
    db.commit()
    db.refresh(request)
    record(
        "06 oversupply (25 given, 10 needed) -> fulfilled, no error, fulfilled=25",
        request.status == RequestStatus.fulfilled and request.quantity_fulfilled == 25,
        f"quantity_fulfilled={request.quantity_fulfilled} status={request.status}",
    )


@scenario
def test_07_three_small_donations_incrementally_fulfill(db: Session):
    warehouse = db.scalar(select(Warehouse).limit(1))
    receiver = make_user(db, "r07")
    volunteer = make_user(db, "v07", volunteer=True)
    request = make_request(db, receiver, quantity_needed=15, item_name="unique-rice-07")

    expected_running_total = 0
    statuses = []
    for i in range(3):
        donor = make_user(db, f"d07_{i}")
        donation = make_donation(db, donor, quantity=5, warehouse=warehouse, item_name="unique-rice-07")
        db.commit()
        match_donation_to_receiver(db, donation)
        db.commit()
        complete_delivery_for_donation(db, donation, volunteer, receiver)
        db.commit()
        db.refresh(request)
        expected_running_total += 5
        statuses.append((request.quantity_fulfilled, request.status))

    record(
        "07 three 5-unit donations against a 15-need request reach fulfilled incrementally",
        statuses == [(5, RequestStatus.open), (10, RequestStatus.open), (15, RequestStatus.fulfilled)],
        f"progression={statuses}",
    )


@scenario
def test_08_request_needs_one_donation_gives_two(db: Session):
    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d08")
    receiver = make_user(db, "r08")
    volunteer = make_user(db, "v08", volunteer=True)
    request = make_request(db, receiver, quantity_needed=1, item_name="unique-rice-08")
    donation = make_donation(db, donor, quantity=2, warehouse=warehouse, item_name="unique-rice-08")
    db.commit()
    match_donation_to_receiver(db, donation)
    db.commit()
    complete_delivery_for_donation(db, donation, volunteer, receiver)
    db.commit()
    db.refresh(request)
    record(
        "08 request needs 1, donation gives 2 -> fulfilled, no crash",
        request.status == RequestStatus.fulfilled and request.quantity_fulfilled == 2,
        f"quantity_fulfilled={request.quantity_fulfilled} status={request.status}",
    )


@scenario
def test_09_donation_with_no_receiver_request_id_unaffected(db: Session):
    """Targeted donations (direct to a receiver, no ReceiverRequest row) must
    not touch any request's quantity_fulfilled — regression guard for the
    `if delivery.receiver_request_id` branch."""
    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d09")
    receiver = make_user(db, "r09")
    volunteer = make_user(db, "v09", volunteer=True)
    donation = make_donation(db, donor, quantity=5, warehouse=warehouse, target_receiver_id=receiver.id)
    db.commit()

    from app.services.matching.orchestrator import create_targeted_delivery
    create_targeted_delivery(db, donation, receiver.id)
    db.commit()

    delivery = db.scalar(select(Delivery).where(Delivery.donation_id == donation.id))
    record(
        "09 targeted donation has no receiver_request_id, doesn't crash quantity logic",
        delivery is not None and delivery.receiver_request_id is None,
        f"delivery.receiver_request_id={delivery.receiver_request_id if delivery else None}",
    )


@scenario
def test_10_zero_remaining_request_not_matched_again_even_if_status_stale(db: Session):
    """Defensive: a request manually left at status=matched but with
    quantity_fulfilled >= quantity_needed should still be excluded (tests the
    quantity_fulfilled < quantity_needed clause independent of status)."""
    warehouse = db.scalar(select(Warehouse).limit(1))
    receiver = make_user(db, "r10")
    request = ReceiverRequest(
        requester_id=receiver.id,
        item_name="unique-rice-10",
        item_category="food",
        quantity_needed=10,
        quantity_fulfilled=10,
        status=RequestStatus.matched,
        location=make_point(16.8, 96.15),
    )
    db.add(request)
    db.flush()
    created_request_ids.append(request.id)
    db.commit()

    scored = score_open_requests(db, "unique-rice-10", "food", None, 5, 16.8, 96.15)
    match = next((s for s in scored if s.request_id == request.id), None)
    record(
        "10 quantity_fulfilled>=needed excluded even if status is stale 'matched'",
        match is None,
        f"match={match}",
    )


@scenario
def test_11_admin_approval_path_rejects_when_fully_fulfilled(db: Session):
    from app.core.exceptions import ConflictError
    from app.models.match_proposal import MatchProposal, MatchProposalStatus
    from app.services.match_review_service import approve_proposal

    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d11")
    receiver = make_user(db, "r11")
    request = ReceiverRequest(
        requester_id=receiver.id,
        item_name="unique-rice-11",
        item_category="food",
        quantity_needed=10,
        quantity_fulfilled=10,
        status=RequestStatus.fulfilled,
        location=make_point(16.8, 96.15),
    )
    db.add(request)
    db.flush()
    created_request_ids.append(request.id)

    donation = make_donation(db, donor, quantity=5, warehouse=warehouse, item_name="unique-rice-11")
    proposal = MatchProposal(
        donation_id=donation.id,
        receiver_request_id=request.id,
        receiver_id=receiver.id,
        stage1_score=0.9,
        status=MatchProposalStatus.pending,
    )
    db.add(proposal)
    db.commit()

    rejected = False
    try:
        approve_proposal(db, proposal.id)
    except ConflictError:
        rejected = True
    record(
        "11 admin-approval rejects proposal for already-fulfilled request",
        rejected,
        f"rejected={rejected}",
    )


@scenario
def test_12_admin_approval_path_allows_when_partially_fulfilled(db: Session):
    from app.models.match_proposal import MatchProposal, MatchProposalStatus
    from app.services.match_review_service import approve_proposal

    warehouse = db.scalar(select(Warehouse).limit(1))
    donor = make_user(db, "d12")
    receiver = make_user(db, "r12")
    request = ReceiverRequest(
        requester_id=receiver.id,
        item_name="unique-rice-12",
        item_category="food",
        quantity_needed=20,
        quantity_fulfilled=10,
        status=RequestStatus.matched,
        location=make_point(16.8, 96.15),
    )
    db.add(request)
    db.flush()
    created_request_ids.append(request.id)

    donation = make_donation(db, donor, quantity=10, warehouse=warehouse, item_name="unique-rice-12")
    proposal = MatchProposal(
        donation_id=donation.id,
        receiver_request_id=request.id,
        receiver_id=receiver.id,
        stage1_score=0.9,
        status=MatchProposalStatus.pending,
    )
    db.add(proposal)
    db.commit()

    approve_proposal(db, proposal.id)
    db.refresh(request)
    record(
        "12 admin-approval allows second donation for partially-fulfilled request",
        request.status == RequestStatus.matched,
        f"request.status={request.status}",
    )


def cleanup(db: Session):
    db.rollback()
    for delivery in db.scalars(select(Delivery).where(Delivery.donation_id.in_(created_donation_ids))).all():
        db.delete(delivery)
    db.flush()
    from app.models.match_proposal import MatchProposal
    for proposal in db.scalars(select(MatchProposal).where(MatchProposal.donation_id.in_(created_donation_ids))).all():
        db.delete(proposal)
    db.flush()
    for donation in db.scalars(select(Donation).where(Donation.id.in_(created_donation_ids))).all():
        db.delete(donation)
    db.flush()
    for request in db.scalars(select(ReceiverRequest).where(ReceiverRequest.id.in_(created_request_ids))).all():
        db.delete(request)
    db.flush()
    for user in db.scalars(select(User).where(User.id.in_(created_user_ids))).all():
        db.delete(user)
    db.commit()
    print(f"\nCleaned up {len(created_donation_ids)} donations, {len(created_request_ids)} requests, {len(created_user_ids)} users.")


def main():
    db = SessionLocal()
    try:
        for fn in [
            test_01_exact_match_one_donation_one_request,
            test_02_donation_smaller_than_request_stays_open,
            test_03_two_donations_fully_cover_one_request,
            test_04_partially_fulfilled_request_still_appears_in_open_scoring,
            test_05_fully_fulfilled_request_excluded_from_open_scoring,
            test_06_oversupply_donation_marks_fulfilled_not_overflow_error,
            test_07_three_small_donations_incrementally_fulfill,
            test_08_request_needs_one_donation_gives_two,
            test_09_donation_with_no_receiver_request_id_unaffected,
            test_10_zero_remaining_request_not_matched_again_even_if_status_stale,
            test_11_admin_approval_path_rejects_when_fully_fulfilled,
            test_12_admin_approval_path_allows_when_partially_fulfilled,
        ]:
            fn(db)
    finally:
        cleanup(db)
        db.close()

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n{passed}/{total} scenarios passed")
    if passed != total:
        sys.exit(1)


if __name__ == "__main__":
    main()
