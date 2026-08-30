# database/base.py
import os
from datetime import datetime

from sqlalchemy import create_engine, event, exc
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }


# Real (non-sqlite-in-memory) engines created via get_session(), tracked so a
# Celery worker_process_init hook can dispose() them after fork without every
# caller needing to keep its own reference to the engine.
_ENGINES: list = []


def dispose_all_engines():
    """Discard pooled connections inherited across os.fork() in every tracked engine.

    Intended to be called from a post-fork hook (e.g. Celery's
    worker_process_init) so each forked process starts with an empty pool
    instead of reusing connections/sockets it inherited from the parent.
    """
    for engine in _ENGINES:
        engine.dispose(close=False)


def _guard_against_forked_connections(engine):
    """Invalidate pooled connections inherited across os.fork() (e.g. Celery prefork).

    Without this, a connection opened pre-fork is shared by every forked worker
    process, and concurrent use of the same underlying socket from multiple
    processes corrupts the libpq protocol state.
    """

    @event.listens_for(engine, "connect")
    def _record_pid(dbapi_connection, connection_record):
        connection_record.info["pid"] = os.getpid()

    @event.listens_for(engine, "checkout")
    def _check_pid(dbapi_connection, connection_record, connection_proxy):
        if connection_record.info["pid"] != os.getpid():
            connection_record.dbapi_connection = connection_proxy.dbapi_connection = (
                None
            )
            raise exc.DisconnectionError(
                f"Connection record belongs to pid {connection_record.info['pid']}, "
                f"attempting to check out in pid {os.getpid()}"
            )


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
        _guard_against_forked_connections(engine)
        _ENGINES.append(engine)

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
