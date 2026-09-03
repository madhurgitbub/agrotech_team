from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import BIGINT, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
    )

    audience: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'all'"),
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )