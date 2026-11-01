from __future__ import annotations

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.utils.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    from app.models import prompt_log, security_event  # noqa: F401

    inspector = inspect(engine)
    if settings.database_url.startswith("sqlite") and inspector.has_table("prompt_logs"):
        existing_columns = {col["name"] for col in inspector.get_columns("prompt_logs")}
        missing_columns = []
        if "semantic_score" not in existing_columns:
            missing_columns.append("semantic_score FLOAT")
        if "semantic_category" not in existing_columns:
            missing_columns.append("semantic_category VARCHAR(50)")
        if "matched_attack" not in existing_columns:
            missing_columns.append("matched_attack TEXT")
        if "similarity" not in existing_columns:
            missing_columns.append("similarity FLOAT")
        if "confidence" not in existing_columns:
            missing_columns.append("confidence VARCHAR(20)")
        if missing_columns:
            with engine.begin() as conn:
                for column_sql in missing_columns:
                    conn.execute(text(f"ALTER TABLE prompt_logs ADD COLUMN {column_sql}"))

    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
