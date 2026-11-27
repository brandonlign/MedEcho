"""Tiny forward-only migrations.

Version 1 is the full schema created from the models. Later versions append a
function to ``MIGRATIONS``; each runs once and is recorded in ``schema_version``.
"""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import Connection, insert, select
from sqlalchemy.engine import Engine

from medecho.db.models import Base, SchemaVersion


def _v1(conn: Connection) -> None:
    Base.metadata.create_all(conn)


MIGRATIONS: list[Callable[[Connection], None]] = [_v1]


def current_version(engine: Engine) -> int:
    with engine.connect() as conn:
        if not engine.dialect.has_table(conn, SchemaVersion.__tablename__):
            return 0
        versions = conn.execute(select(SchemaVersion.version)).scalars().all()
        return max(versions, default=0)


def migrate(engine: Engine) -> int:
    done = current_version(engine)
    for number, step in enumerate(MIGRATIONS, start=1):
        if number <= done:
            continue
        with engine.begin() as conn:
            Base.metadata.tables[SchemaVersion.__tablename__].create(conn, checkfirst=True)
            step(conn)
            conn.execute(insert(SchemaVersion).values(version=number))
    return current_version(engine)
