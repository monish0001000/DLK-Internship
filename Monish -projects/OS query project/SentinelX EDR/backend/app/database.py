"""
SentinelX EDR - Database Configuration
=======================================
SQLAlchemy engine, session factory, and base model setup.

Supports:
    - SQLite (default, zero-config for development)
    - PostgreSQL (production, change DATABASE_URL env var)

Usage:
    from app.database import get_db, Base, engine

    # In FastAPI route:
    @router.get("/items")
    def get_items(db: Session = Depends(get_db)):
        return db.query(Item).all()

    # Create all tables:
    Base.metadata.create_all(bind=engine)
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from app.config import get_settings

settings = get_settings()

# ── Engine Configuration ────────────────────────────────────────
# SQLite requires special handling for concurrent access and foreign keys
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
        poolclass=StaticPool,  # Single connection pool for SQLite
        echo=settings.DEBUG,
    )

    # Enable foreign key enforcement for SQLite (off by default)
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Better concurrent read performance
        cursor.close()
else:
    # PostgreSQL (or any other database)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before using
        echo=settings.DEBUG,
    )

# ── Session Factory ─────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Declarative Base ────────────────────────────────────────────
Base = declarative_base()


# ── FastAPI Dependency ──────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically commits on success or rolls back on error.

    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables defined by ORM models.
    Called during application startup in main.py lifespan handler.

    For production with PostgreSQL, use Alembic migrations instead:
        alembic upgrade head
    """
    # Import all models so they register with Base.metadata
    import app.models.endpoint  # noqa: F401
    import app.models.telemetry  # noqa: F401
    import app.models.alert  # noqa: F401
    import app.models.investigation  # noqa: F401
    import app.models.case  # noqa: F401
    import app.models.report  # noqa: F401
    import app.models.threat_intel  # noqa: F401
    import app.models.detection_rule  # noqa: F401
    import app.models.metric  # noqa: F401
    import app.models.simulation  # noqa: F401

    Base.metadata.create_all(bind=engine)
