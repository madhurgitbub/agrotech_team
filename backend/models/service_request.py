from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import BIGINT, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
    )

    request_id: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    farmer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    farmer_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    farmer_phone: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    provider_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    service_id: Mapped[int | None] = mapped_column(
        BIGINT,
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
    )

    service_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_method: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'cod'"),
    )

    payment_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'pending'"),
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'pending'"),
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_date: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="service_requests_quantity_check",
        ),
        CheckConstraint(
            "price >= 0",
            name="service_requests_price_check",
        ),
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'success', 'completed', 'failed', 'refunded')",
            name="service_requests_payment_status_check",
        ),
        CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected', 'confirmed', 'completed', 'cancelled')",
            name="service_requests_status_check",
        ),
        Index("idx_service_requests_farmer", "farmer_id"),
        Index("idx_service_requests_provider", "provider_id"),
        Index("idx_service_requests_service", "service_id"),
    )