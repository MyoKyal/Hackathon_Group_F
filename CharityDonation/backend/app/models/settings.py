import uuid

from sqlalchemy import Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    require_match_approval: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
