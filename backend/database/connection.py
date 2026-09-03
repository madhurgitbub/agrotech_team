import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


# Load backend/.env
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")


# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    FastAPI dependency.

    Creates one database session for a request
    and closes it when the request is finished.
    """
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Simple connection test
if __name__ == "__main__":
    with engine.connect() as connection:
        print("✅ Successfully connected to Supabase PostgreSQL!")