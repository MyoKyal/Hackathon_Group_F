from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.settings import AppSettings


def get_settings(db: Session) -> AppSettings:
    settings = db.scalars(select(AppSettings).limit(1)).first()
    if settings is None:
        settings = AppSettings(require_match_approval=False)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(db: Session, require_match_approval: bool) -> AppSettings:
    settings = get_settings(db)
    was_gated = settings.require_match_approval
    settings.require_match_approval = require_match_approval
    db.commit()
    db.refresh(settings)

    if was_gated and not require_match_approval:
        from app.services.match_review_service import clear_pending_backlog

        clear_pending_backlog(db)

    return settings
