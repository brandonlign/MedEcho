"""Runtime settings.

Everything has a free, local default. Paid providers are opt-in through the
environment variables listed in ``.env.example``.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

log = logging.getLogger("medecho.config")

REPO_ROOT = Path(__file__).resolve().parents[1]


def _clean(value: str | None) -> str:
    """Strip whitespace and trailing ``# comment`` text copied from .env.example."""
    if value is None:
        return ""
    return value.split("#", 1)[0].strip()


def _flag(value: str | None) -> bool:
    return _clean(value).lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    demo: bool = False
    seed: int = 20251223
    db_url: str = "sqlite:///./medecho.db"
    base_url: str = "http://localhost:8000"
    data_dir: Path = field(default_factory=lambda: Path("var"))

    stt: str = "faster-whisper"
    whisper_model: str = "small"
    tts: str = "edge"
    ocr: str = "tesseract"
    grader: str = "rules"
    sheet_vlm: str = "none"
    transport: str = "browser"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = ""
    azure_speech_key: str = ""
    azure_speech_region: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    recheck_delay_override_s: float | None = None
    callback_delay_override_s: float | None = None

    @property
    def recheck_delay_s(self) -> float:
        """Pause before the in-call re-check (about 2 minutes; seconds in demo mode)."""
        if self.recheck_delay_override_s is not None:
            return self.recheck_delay_override_s
        return 6.0 if self.demo else 120.0

    @property
    def callback_delay_s(self) -> float:
        """Delay before the retention callback (48 hours; seconds in demo mode)."""
        if self.callback_delay_override_s is not None:
            return self.callback_delay_override_s
        return 20.0 if self.demo else 48 * 3600.0

    @property
    def twilio_enabled(self) -> bool:
        return self.transport == "twilio" and bool(
            self.twilio_account_sid and self.twilio_auth_token and self.twilio_phone_number
        )

    @property
    def smtp_enabled(self) -> bool:
        return bool(self.smtp_host)

    @property
    def recordings_dir(self) -> Path:
        return self.data_dir / "recordings"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def tts_cache_dir(self) -> Path:
        return self.data_dir / "tts-cache"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.recordings_dir, self.uploads_dir, self.tts_cache_dir):
            d.mkdir(parents=True, exist_ok=True)


def _opt_float(value: str) -> float | None:
    return float(value) if value else None


def load_settings(env_file: str | Path | None = ".env") -> Settings:
    """Build settings from the environment (and an optional .env file)."""
    if env_file is not None and Path(env_file).is_file():
        load_dotenv(env_file, override=False)

    def e(key: str, default: str = "") -> str:
        return _clean(os.environ.get(key)) or default

    return Settings(
        demo=_flag(os.environ.get("MEDECHO_DEMO")),
        seed=int(e("MEDECHO_SEED", "20251223")),
        db_url=e("MEDECHO_DB_URL", "sqlite:///./medecho.db"),
        base_url=e("MEDECHO_BASE_URL", "http://localhost:8000"),
        data_dir=Path(e("MEDECHO_DATA_DIR", "var")),
        stt=e("MEDECHO_STT", "faster-whisper"),
        whisper_model=e("MEDECHO_WHISPER_MODEL", "small"),
        tts=e("MEDECHO_TTS", "edge"),
        ocr=e("MEDECHO_OCR", "tesseract"),
        grader=e("MEDECHO_GRADER", "rules"),
        sheet_vlm=e("MEDECHO_SHEET_VLM", "none"),
        transport=e("MEDECHO_TRANSPORT", "browser"),
        anthropic_api_key=e("ANTHROPIC_API_KEY"),
        openai_api_key=e("OPENAI_API_KEY"),
        ollama_host=e("OLLAMA_HOST", "http://localhost:11434"),
        ollama_model=e("OLLAMA_MODEL"),
        azure_speech_key=e("AZURE_SPEECH_KEY"),
        azure_speech_region=e("AZURE_SPEECH_REGION"),
        twilio_account_sid=e("TWILIO_ACCOUNT_SID"),
        twilio_auth_token=e("TWILIO_AUTH_TOKEN"),
        twilio_phone_number=e("TWILIO_PHONE_NUMBER"),
        smtp_host=e("SMTP_HOST"),
        smtp_port=int(e("SMTP_PORT", "587")),
        smtp_user=e("SMTP_USER"),
        smtp_password=e("SMTP_PASSWORD"),
        recheck_delay_override_s=_opt_float(e("MEDECHO_RECHECK_DELAY_S")),
        callback_delay_override_s=_opt_float(e("MEDECHO_CALLBACK_DELAY_S")),
    )
