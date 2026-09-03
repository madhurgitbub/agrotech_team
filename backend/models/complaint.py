from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import BIGINT, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
    )

    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    subject: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'low'"),
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'open'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="complaints_priority_check",
        ),
        CheckConstraint(
            "status IN ('open', 'assigned', 'resolved', 'closed')",
            name="complaints_status_check",
        ),
    )