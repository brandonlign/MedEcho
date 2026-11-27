"""Engine and session helpers."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from medecho.db.migrations import current_version, migrate


class Database:
    def __init__(self, url: str) -> None:
        args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        self.engine = create_engine(url, connect_args=args)
        self._factory = sessionmaker(self.engine, expire_on_commit=False)

    def create_all(self) -> None:
        migrate(self.engine)

    def schema_version(self) -> int:
        return current_version(self.engine)

    def session(self) -> Session:
        return self._factory()
