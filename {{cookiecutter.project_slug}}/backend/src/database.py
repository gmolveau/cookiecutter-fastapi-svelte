"""SQLite database engine and session factory."""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_db_path = os.environ.get("DATABASE_URL", "sqlite:///./data/meme_generator.db")

database_engine = create_engine(
    _db_path,
    connect_args={"check_same_thread": False},
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
    bind=database_engine,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
