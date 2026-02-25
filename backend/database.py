"""
database.py
-----------
SQLAlchemy engine, session factory, and declarative Base.
Provides the `get_db` dependency used by all FastAPI route handlers.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
# `check_same_thread=False` is required for SQLite when used with FastAPI
# (multiple threads share the same connection).  Ignored by PostgreSQL.
connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,   # Log SQL statements in development
)

# ── Session Factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ── Declarative Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All ORM models inherit from this class."""
    pass


# ── Dependency ────────────────────────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that yields a database session per request and
    guarantees the session is closed when the request completes.

    Usage in routes:
        from fastapi import Depends
        from database import get_db
        from sqlalchemy.orm import Session

        def some_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
