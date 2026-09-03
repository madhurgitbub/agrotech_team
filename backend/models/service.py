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


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        server_default=text("'per hour'"),
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    rating: Mapped[float | None] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        server_default=text("0"),
    )

    reviews: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        server_default=text("0"),
    )

    available: Mapped[bool] = mapped_column(
        nullable=False,
        server_default=text("true"),
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'pending'"),
    )

    posted_by: Mapped[UUID | None] = mapped_column(
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
            "price >= 0",
            name="services_price_check",
        ),
        CheckConstraint(
            "rating >= 0 AND rating <= 5",
            name="services_rating_check",
        ),
        CheckConstraint(
            "reviews >= 0",
            name="services_reviews_check",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="services_status_check",
        ),
        Index("idx_services_category", "category"),
        Index("idx_services_posted_by", "posted_by"),
    )