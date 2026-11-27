PY ?= .venv/bin/python
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: setup run demo test lint typecheck format

setup:
	@command -v tesseract >/dev/null 2>&1 || { \
	  if command -v brew >/dev/null 2>&1; then brew install tesseract; \
	  else echo "NOTE: tesseract not found. Install it (macOS: brew install tesseract). Mock sheets still work without it."; fi; }
	@if command -v uv >/dev/null 2>&1; then uv venv --python 3.11 --allow-existing .venv && uv pip install --python $(PY) -e ".[dev]"; \
	else python3 -m venv .venv && $(PY) -m pip install -U pip && $(PY) -m pip install -e ".[dev]"; fi
	@[ -f .env ] || cp .env.example .env
	@[ -d .git ] && $(PY) -m pre_commit install >/dev/null 2>&1 || true
	@echo "Setup done. Start the app with: make run"

run:
	$(PY) -m uvicorn medecho.api.app:app --host $(HOST) --port $(PORT)

demo:
	MEDECHO_DEMO=1 $(PY) -m uvicorn medecho.api.app:app --host $(HOST) --port $(PORT)

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

typecheck:
	$(PY) -m mypy

format:
	$(PY) -m ruff check --fix .
	$(PY) -m ruff format .

test: lint typecheck
	$(PY) -m pytest
