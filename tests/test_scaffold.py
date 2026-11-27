"""Milestone 1: scaffold, health route, config and database."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from medecho.config import Settings, load_settings
from medecho.db import models
from medecho.db.session import Database

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = [
    "api", "call", "transports", "channels", "sheet", "speech",
    "grader", "conformal", "redteam", "study", "db",
]  # fmt: skip


@pytest.mark.parametrize("name", PACKAGES)
def test_repo_layout(name: str) -> None:
    assert (ROOT / "medecho" / name / "__init__.py").is_file()


@pytest.mark.parametrize("name", ["web", "tests", "docs", "scripts", "data"])
def test_top_level_dirs(name: str) -> None:
    assert (ROOT / name).is_dir()


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["demo"] is True
    assert body["paid_keys_required"] is False


def test_home_page_states_scope(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "does not review the prescription" in r.text


def test_defaults_are_free_and_local(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("MEDECHO_STT", "MEDECHO_TTS", "MEDECHO_GRADER", "MEDECHO_TRANSPORT",
                "MEDECHO_SHEET_VLM", "MEDECHO_OCR", "MEDECHO_DEMO"):  # fmt: skip
        monkeypatch.delenv(key, raising=False)
    s = load_settings(env_file=None)
    assert (s.stt, s.tts, s.grader, s.transport, s.sheet_vlm, s.ocr) == (
        "faster-whisper", "edge", "rules", "browser", "none", "tesseract",
    )  # fmt: skip
    assert s.demo is False


def test_env_values_tolerate_inline_comments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEDECHO_GRADER", "llm   # rules | llm")
    monkeypatch.setenv("MEDECHO_DEMO", "1")
    s = load_settings(env_file=None)
    assert s.grader == "llm"
    assert s.demo is True


def test_demo_mode_shortens_timers() -> None:
    normal, demo = Settings(demo=False), Settings(demo=True)
    assert normal.recheck_delay_s == 120
    assert normal.callback_delay_s == 48 * 3600
    assert demo.recheck_delay_s < 30
    assert demo.callback_delay_s < 120


def test_database_tables_and_roundtrip(settings: Settings) -> None:
    db = Database(settings.db_url)
    db.create_all()
    tables = set(inspect(db.engine).get_table_names())
    assert {"sessions", "calls", "item_results", "call_events", "alerts", "schema_version"} <= tables
    with db.session() as s:
        sess = models.CareSession(language="fa")
        s.add(sess)
        s.flush()
        call = models.Call(session_id=sess.id, kind="initial")
        s.add(call)
        s.flush()
        s.add(models.ItemResult(call_id=call.id, item_id="med-1", phase="immediate",
                                label="partial", evidence="one pill", score=0.4, understood=False))  # fmt: skip
        s.commit()
        sid = sess.id
    with db.session() as s:
        got = s.get(models.CareSession, sid)
        assert got is not None
        assert got.share_token and got.share_token != got.id
        assert got.calls[0].results[0].evidence == "one pill"


def test_migrations_are_idempotent(settings: Settings) -> None:
    db = Database(settings.db_url)
    db.create_all()
    db.create_all()
    assert db.schema_version() >= 1
