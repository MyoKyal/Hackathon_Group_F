import logging
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.geo import extract_lat_lng
from app.models.delivery import Delivery, DeliveryStatus
from app.models.donation import Donation
from app.models.receiver_request import ReceiverRequest
from app.models.user import TransportationType, User
from app.models.warehouse import Warehouse
from app.schemas.route import RoutePoint, RouteResponse
from app.services.matching import orchestrator

logger = logging.getLogger(__name__)

# Public OSRM demo server — no API key required. Rate-limited and car-oriented
# (the demo only reliably serves a "driving" profile), so every transport type
# is routed as driving; this is a deliberate tradeoff for a zero-setup demo.
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1"
OSRM_TIMEOUT_SECONDS = 8

OSRM_PROFILE_BY_TRANSPORT = {
    TransportationType.walking: "foot",
    TransportationType.bicycle: "cycling",
    TransportationType.motorbike: "driving",
    TransportationType.car: "driving",
    TransportationType.truck: "driving",
}


def _fetch_osrm_geometry(profile: str, points: list[tuple[float, float]]) -> dict | None:
    coord_str = ";".join(f"{lng},{lat}" for lat, lng in points)
    try:
        response = httpx.get(
            f"{OSRM_BASE_URL}/{profile}/{coord_str}",
            params={"overview": "full", "geometries": "geojson"},
            timeout=OSRM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None
        route = data["routes"][0]
        geometry = [[lat, lng] for lng, lat in route["geometry"]["coordinates"]]
        return {
            "geometry": geometry,
            "distance_km": route["distance"] / 1000.0,
            "duration_min": route["duration"] / 60.0,
        }
    except Exception:
        logger.warning("OSRM routing request failed", exc_info=True)
        return None


def _build_response(
    leg: str,
    volunteer: User,
    points: list[tuple[float, float, str]],
) -> RouteResponse:
    waypoints = [RoutePoint(lat=lat, lng=lng, label=label) for lat, lng, label in points]
    profile = OSRM_PROFILE_BY_TRANSPORT.get(volunteer.transportation_type, "driving")
    routed_data = _fetch_osrm_geometry(profile, [(lat, lng) for lat, lng, _ in points])
    return RouteResponse(
        leg=leg,
        volunteer_id=volunteer.id,
        volunteer_name=volunteer.full_name,
        waypoints=waypoints,
        geometry=routed_data["geometry"] if routed_data else None,
        distance_km=routed_data["distance_km"] if routed_data else None,
        duration_min=routed_data["duration_min"] if routed_data else None,
        routed=routed_data is not None,
    )


def get_pickup_route(db: Session, user: User, donation_id: UUID) -> RouteResponse:
    donation = db.get(Donation, donation_id)
    if donation is None:
        raise NotFoundError("Donation not found")

    volunteer: User | None = None
    if donation.pickup_volunteer_id is not None:
        volunteer = db.get(User, donation.pickup_volunteer_id)
    else:
        candidates = orchestrator.rank_volunteers_for_pickup(db, donation, limit=1)
        if candidates:
            volunteer = db.get(User, candidates[0].volunteer_id)

    is_offer_candidate = volunteer is not None and volunteer.id == user.id
    if not (
        user.is_admin
        or donation.donor_id == user.id
        or donation.pickup_volunteer_id == user.id
        or is_offer_candidate
    ):
        raise ForbiddenError("Not authorized to view this route", "not_authorized")

    if volunteer is None:
        raise NotFoundError("No suitable volunteer found yet")

    warehouse = db.get(Warehouse, donation.warehouse_id)
    vol_lat, vol_lng = extract_lat_lng(db, volunteer.base_location)
    donor_lat, donor_lng = extract_lat_lng(db, donation.pickup_location)
    wh_lat, wh_lng = extract_lat_lng(db, warehouse.location)

    points = [
        (vol_lat, vol_lng, f"Volunteer: {volunteer.full_name}"),
        (donor_lat, donor_lng, f"Pickup: {donation.item_name}"),
        (wh_lat, wh_lng, f"Warehouse: {warehouse.name}"),
    ]
    return _build_response("pickup", volunteer, points)


def get_delivery_route(db: Session, user: User, delivery_id: UUID) -> RouteResponse:
    delivery = db.get(Delivery, delivery_id)
    if delivery is None:
        raise NotFoundError("Delivery not found")
    donation = db.get(Donation, delivery.donation_id)
    if donation is None:
        raise NotFoundError("Donation not found")
    if delivery.receiver_request_id is None:
        raise NotFoundError("No receiver location for this delivery")

    volunteer: User | None = None
    if delivery.volunteer_id is not None:
        volunteer = db.get(User, delivery.volunteer_id)
    elif donation.pickup_status == DeliveryStatus.completed:
        candidates = orchestrator.rank_volunteers_for_delivery(db, delivery, limit=1)
        if candidates:
            volunteer = db.get(User, candidates[0].volunteer_id)

    is_offer_candidate = volunteer is not None and volunteer.id == user.id
    if not (
        user.is_admin
        or donation.donor_id == user.id
        or delivery.receiver_id == user.id
        or delivery.volunteer_id == user.id
        or is_offer_candidate
    ):
        raise ForbiddenError("Not authorized to view this route", "not_authorized")

    if volunteer is None:
        raise NotFoundError("No suitable volunteer found yet")

    warehouse = db.get(Warehouse, donation.warehouse_id)
    receiver_request = db.get(ReceiverRequest, delivery.receiver_request_id)

    vol_lat, vol_lng = extract_lat_lng(db, volunteer.base_location)
    wh_lat, wh_lng = extract_lat_lng(db, warehouse.location)
    recv_lat, recv_lng = extract_lat_lng(db, receiver_request.location)

    points = [
        (vol_lat, vol_lng, f"Volunteer: {volunteer.full_name}"),
        (wh_lat, wh_lng, f"Warehouse: {warehouse.name}"),
        (recv_lat, recv_lng, "Receiver"),
    ]
    return _build_response("delivery", volunteer, points)
