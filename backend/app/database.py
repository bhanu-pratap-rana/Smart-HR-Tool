"""Database connection and session management.

Provides SQLModel engine, session factory, and dependency injection
for FastAPI endpoints.
"""

import logging
from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import NullPool

from backend.app.config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create database engine with connection pooling
# For development, we use a smaller pool; production should use larger pools
connect_args = {}
if settings.database_url.startswith("sqlite"):
    # SQLite requires check_same_thread=False for FastAPI
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    connect_args=connect_args
)


def create_db_and_tables():
    """
    Create all database tables.

    This should be called on application startup.
    In production, use Alembic migrations instead.
    """
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Yields a database session and ensures it's closed after use.
    Use this in FastAPI endpoints with Depends().

    Example:
        @app.get("/items/")
        def get_items(session: Session = Depends(get_session)):
            return session.exec(select(Item)).all()

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Type alias for dependency injection
SessionDep = Generator[Session, None, None]


__all__ = [
    "engine",
    "create_db_and_tables",
    "get_session",
    "SessionDep",
]
