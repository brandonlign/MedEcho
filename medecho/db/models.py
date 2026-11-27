"""SQLite models. Mock data only: no real patient data is ever stored."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _id() -> str:
    return uuid.uuid4().hex[:12]


def _token() -> str:
    return secrets.token_urlsafe(12)


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class SchemaVersion(Base):
    __tablename__ = "schema_version"
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class CareSession(Base):
    """One sheet set up by a family member, with its calls."""

    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_id)
    share_token: Mapped[str] = mapped_column(String(32), unique=True, default=_token)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    language: Mapped[str] = mapped_column(String(4), default="en")
    status: Mapped[str] = mapped_column(String(24), default="draft")
    family_label: Mapped[str] = mapped_column(String(80), default="")
    parent_contact: Mapped[str] = mapped_column(String(120), default="")
    photo_path: Mapped[str] = mapped_column(String(400), default="")
    extraction_json: Mapped[str] = mapped_column(Text, default="")
    confirmed_json: Mapped[str] = mapped_column(Text, default="")
    intro_audio_path: Mapped[str] = mapped_column(String(400), default="")

    calls: Mapped[list[Call]] = relationship(
        back_populates="session", order_by="Call.created_at", cascade="all, delete-orphan"
    )
    alerts: Mapped[list[Alert]] = relationship(
        back_populates="session", order_by="Alert.created_at", cascade="all, delete-orphan"
    )


class Call(Base):
    __tablename__ = "calls"
    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_id)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    kind: Mapped[str] = mapped_column(String(12), default="initial")  # initial | callback
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    spoken_count: Mapped[int] = mapped_column(Integer, default=0)
    generated_words: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped[CareSession] = relationship(back_populates="calls")
    results: Mapped[list[ItemResult]] = relationship(
        back_populates="call", order_by="ItemResult.id", cascade="all, delete-orphan"
    )
    events: Mapped[list[CallEvent]] = relationship(
        back_populates="call", order_by="CallEvent.id", cascade="all, delete-orphan"
    )


class ItemResult(Base):
    __tablename__ = "item_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id"), index=True)
    item_id: Mapped[str] = mapped_column(String(40))
    phase: Mapped[str] = mapped_column(String(12))  # immediate | recheck | callback
    label: Mapped[str] = mapped_column(String(10))  # correct | partial | wrong | missing
    evidence: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    understood: Mapped[bool] = mapped_column(Boolean, default=False)
    clip_path: Mapped[str] = mapped_column(String(400), default="")

    call: Mapped[Call] = relationship(back_populates="results")


class CallEvent(Base):
    """Append-only call log: spoken strings, transcripts and state changes."""

    __tablename__ = "call_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    call_id: Mapped[str] = mapped_column(ForeignKey("calls.id"), index=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    kind: Mapped[str] = mapped_column(String(24))
    payload_json: Mapped[str] = mapped_column(Text, default="{}")

    call: Mapped[Call] = relationship(back_populates="events")


class Alert(Base):
    """A family alert, raised when a warning phrase is heard."""

    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    call_id: Mapped[str] = mapped_column(String(16), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    kind: Mapped[str] = mapped_column(String(24), default="escalation")
    category: Mapped[str] = mapped_column(String(40), default="")
    phrase: Mapped[str] = mapped_column(Text, default="")
    channels: Mapped[str] = mapped_column(String(120), default="web")

    session: Mapped[CareSession] = relationship(back_populates="alerts")
