from sqlalchemy import select

from app.core.geo import make_point
from app.models.delivery import Delivery, DeliveryStatus
from app.models.donation import Donation, DonationStatus
from app.models.user import User, VolunteerStatus
from app.models.warehouse import Warehouse
from app.services.delivery_service import confirm_receiver, confirm_volunteer


def _create_user(db, email: str, name: str) -> User:
    from app.core.security import hash_password

    user = User(
        email=email,
        password_hash=hash_password("password123"),
        full_name=name,
        is_volunteer=True,
        volunteer_status=VolunteerStatus.approved,
        base_location=make_point(16.8, 96.15),
    )
    db.add(user)
    db.flush()
    return user


def _create_delivery_setup(db):
    donor = _create_user(db, "donor_del@example.com", "Donor Del")
    receiver = _create_user(db, "receiver_del@example.com", "Receiver Del")
    volunteer = _create_user(db, "volunteer_del@example.com", "Volunteer Del")

    warehouse = db.scalar(select(Warehouse).limit(1))

    donation = Donation(
        donor_id=donor.id,
        item_name="Food Pack",
        item_category="food",
        quantity=1,
        pickup_location=make_point(16.8, 96.15),
        status=DonationStatus.in_transit,
        warehouse_id=warehouse.id,
    )
    db.add(donation)
    db.flush()

    delivery = Delivery(
        donation_id=donation.id,
        receiver_id=receiver.id,
        volunteer_id=volunteer.id,
        status=DeliveryStatus.in_transit,
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return donor, receiver, volunteer, donation, delivery


def test_only_volunteer_confirmed_stays_in_transit(db):
    _, receiver, volunteer, _, delivery = _create_delivery_setup(db)

    confirm_volunteer(db, volunteer, delivery.id)
    db.refresh(delivery)

    assert delivery.volunteer_confirmed is True
    assert delivery.receiver_confirmed is False
    assert delivery.status == DeliveryStatus.in_transit


def test_only_receiver_confirmed_stays_in_transit(db):
    _, receiver, volunteer, _, delivery = _create_delivery_setup(db)

    confirm_receiver(db, receiver, delivery.id)
    db.refresh(delivery)

    assert delivery.receiver_confirmed is True
    assert delivery.volunteer_confirmed is False
    assert delivery.status == DeliveryStatus.in_transit


def test_both_confirmations_complete_delivery(db):
    _, receiver, volunteer, donation, delivery = _create_delivery_setup(db)

    confirm_volunteer(db, volunteer, delivery.id)
    confirm_receiver(db, receiver, delivery.id)
    db.refresh(delivery)
    db.refresh(donation)

    assert delivery.status == DeliveryStatus.completed
    assert delivery.volunteer_confirmed is True
    assert delivery.receiver_confirmed is True
    assert delivery.completed_at is not None
    assert donation.status == DonationStatus.completed
