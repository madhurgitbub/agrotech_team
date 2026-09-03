from logging.config import fileConfig

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context


# ============================================================
# PATH SETUP
# ============================================================

# backend/
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Make backend available for imports
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)


# ============================================================
# IMPORT DATABASE BASE + ALL MODELS
# ============================================================

from database.base import Base

# IMPORTANT:
# Import every model so every table is registered
# inside Base.metadata before Alembic compares it.
from models.user import User
from models.service import Service
from models.service_request import ServiceRequest
from models.complaint import Complaint
from models.alert import Alert
from models.notification import Notification
from models.registration_otp import RegistrationOTP


# ============================================================
# ALEMBIC CONFIGURATION
# ============================================================

config = context.config


# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Tell Alembic exactly which SQLAlchemy metadata to compare
target_metadata = Base.metadata


# ============================================================
# DATABASE URL
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set in backend/.env"
    )


# Alembic configparser treats % specially,
# so escape percent signs.
config.set_section_option(
    config.config_ini_section,
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%"),
)


# ============================================================
# OFFLINE MIGRATIONS
# ============================================================

def run_migrations_offline() -> None:
    """Run migrations without a database connection."""

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# ONLINE MIGRATIONS
# ============================================================

def run_migrations_online() -> None:
    """Run migrations using a database connection."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================
# RUN
# ============================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()