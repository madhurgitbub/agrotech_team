from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class RegistrationOTP(Base):
    __tablename__ = "registration_otps"

    email: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
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
    )

    otp_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    otp_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('farmer', 'provider', 'seller')",
            name="registration_otps_role_check",
        ),
        CheckConstraint(
            "attempts >= 0",
            name="registration_otps_attempts_check",
        ),
        Index(
            "idx_registration_otps_expires_at",
            "expires_at",
        ),
    )