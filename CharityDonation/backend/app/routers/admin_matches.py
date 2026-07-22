from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, require_admin
from app.models.user import User
from app.schemas.match_proposal import MatchProposalResponse
from app.schemas.settings import SettingsResponse, SettingsUpdate
from app.schemas.warehouse import InventoryItemResponse
from app.services import match_review_service, settings_service, warehouse_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/matches/pending", response_model=list[MatchProposalResponse])
def list_pending_matches(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return match_review_service.list_pending_proposals(db)


@router.post("/matches/{proposal_id}/approve", response_model=MatchProposalResponse)
def approve_match(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return match_review_service.approve_proposal(db, proposal_id)


@router.post("/matches/{proposal_id}/reject", response_model=MatchProposalResponse)
def reject_match(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return match_review_service.reject_proposal(db, proposal_id)


@router.get("/settings", response_model=SettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return settings_service.get_settings(db)


@router.put("/settings", response_model=SettingsResponse)
def update_settings(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return settings_service.update_settings(db, payload.require_match_approval)


@router.get("/inventory", response_model=list[InventoryItemResponse])
def get_inventory(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return warehouse_service.list_inventory(db)
