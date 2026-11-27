"""Shared fixtures."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from medecho.api.app import create_app
from medecho.config import Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        demo=True,
        db_url=f"sqlite:///{tmp_path / 'test.db'}",
        data_dir=tmp_path / "var",
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as c:
        yield c
