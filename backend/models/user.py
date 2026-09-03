from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'farmer'"),
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'active'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('farmer', 'provider', 'seller', 'admin')",
            name="users_role_check",
        ),
        CheckConstraint(
            "status IN ('active', 'blocked', 'pending')",
            name="users_status_check",
        ),
        Index("idx_users_role", "role"),
        Index("idx_users_status", "status"),
    )