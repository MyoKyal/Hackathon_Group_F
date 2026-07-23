from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.geo import extract_lat_lng, make_point
from app.models.receiver_request import ReceiverRequest, RequestStatus
from app.models.user import User
from app.schemas.request import RequestBrowseItem, RequestCreate, RequestResponse, RequestUpdate
from app.services.matching.orchestrator import rematch_pending_donations


def _request_response(db: Session, request: ReceiverRequest) -> RequestResponse:
    lat, lng = extract_lat_lng(db, request.location)
    return RequestResponse(
        id=request.id,
        requester_id=request.requester_id,
        item_name=request.item_name,
        item_category=request.item_category,
        description=request.description,
        quantity_needed=request.quantity_needed,
        quantity_fulfilled=request.quantity_fulfilled,
        lat=lat,
        lng=lng,
        status=request.status,
        created_at=request.created_at,
    )


def create_request(db: Session, user: User, payload: RequestCreate) -> RequestResponse:
    request = ReceiverRequest(
        requester_id=user.id,
        item_name=payload.item_name,
        item_category=payload.item_category,
        description=payload.description,
        quantity_needed=payload.quantity_needed,
        location=make_point(payload.location.lat, payload.location.lng),
    )
    db.add(request)
    db.flush()
    rematch_pending_donations(db)
    db.commit()
    db.refresh(request)
    return _request_response(db, request)


def list_requests(db: Session, user: User) -> list[RequestResponse]:
    requests = db.scalars(
        select(ReceiverRequest)
        .where(ReceiverRequest.requester_id == user.id)
        .order_by(ReceiverRequest.created_at.desc())
    ).all()
    return [_request_response(db, r) for r in requests]


def list_all_requests(db: Session) -> list[RequestBrowseItem]:
    rows = db.execute(
        select(ReceiverRequest, User.full_name)
        .join(User, User.id == ReceiverRequest.requester_id)
        .order_by(ReceiverRequest.created_at.desc())
    ).all()
    return [
        RequestBrowseItem(**_request_response(db, request).model_dump(), requester_name=requester_name)
        for request, requester_name in rows
    ]


def get_request(db: Session, user: User, request_id: UUID) -> RequestResponse:
    request = db.get(ReceiverRequest, request_id)
    if request is None or request.requester_id != user.id:
        raise NotFoundError("Request not found")
    return _request_response(db, request)


def update_request(
    db: Session, user: User, request_id: UUID, payload: RequestUpdate
) -> RequestResponse:
    request = db.get(ReceiverRequest, request_id)
    if request is None or request.requester_id != user.id:
        raise NotFoundError("Request not found")

    if payload.description is not None:
        request.description = payload.description
    if payload.quantity_needed is not None:
        request.quantity_needed = payload.quantity_needed
    if payload.status is not None:
        if payload.status == RequestStatus.fulfilled and request.status == RequestStatus.open:
            request.status = RequestStatus.fulfilled
        elif payload.status != request.status:
            raise BadRequestError(
                "Invalid status transition", "invalid_status_transition"
            )

    db.commit()
    db.refresh(request)
    return _request_response(db, request)
