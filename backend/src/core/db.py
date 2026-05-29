from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _make_url() -> str:
    from src.core.config import get_settings
    s = get_settings()
    return f"postgresql+psycopg2://{s.DB_USER}:{s.DB_PASSWORD}@{s.DB_HOST}:{s.DB_PORT}/{s.DB_NAME}"


engine = create_engine(_make_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
