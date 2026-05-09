# database/base.py
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }


def get_session(db_path: str = "sqlite:///batch4llm.db"):
    if db_path.startswith("sqlite:///:memory:"):
        # Special handling for in-memory DB
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        connect_args = {}
        if db_path.startswith("sqlite://"):
            connect_args["check_same_thread"] = False

        engine = create_engine(
            db_path,
            connect_args=connect_args,
            pool_size=3,
            max_overflow=5,
            pool_pre_ping=True,
        )

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
