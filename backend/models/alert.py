from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import BIGINT, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
    )

    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    audience: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'all'"),
    )

    type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'request'"),
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
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

    __table_args__ = (
        CheckConstraint(
            "audience IN ('all', 'farmer', 'provider', 'admin')",
            name="alerts_audience_check",
        ),
        CheckConstraint(
            "type IN ('request', 'status', 'system', 'promo', 'order')",
            name="alerts_type_check",
        ),
        Index("idx_alerts_user_id", "user_id"),
        Index("idx_alerts_created_at", "created_at"),
    )