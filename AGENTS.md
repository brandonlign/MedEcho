# AGENTS.md

Read `SPEC.md` first. It is the source of truth. This file lists the rules that apply to every change.

## Hard invariants (never break these)

1. **No LLM output reaches TTS.** Every spoken string is built through the `SpokenText` type in the speaker module, from a fixed template plus slot values, or from a verbatim span of the family-confirmed sheet. Nothing else can be passed to a TTS function. Do not add a code path that bypasses this, even for "friendly" filler.
2. **The grader only emits structured data** (label, evidence quote, score). It never emits text meant to be spoken.
3. **Family confirmation gates the call.** A call cannot start while any number or flagged field is unconfirmed.
4. **Escalation always wins.** Warning phrases (English and Persian) interrupt any state, play the escalation script and trigger a family alert.
5. **No improvised medical statements, no judging the prescription, off-sheet questions are referred to the pharmacist.**
6. **Never say "incorrect" to a parent.** Use the shame-free AHRQ phrasing in the templates.
7. **Mock data only.** No real patient data anywhere in the repo, fixtures or logs. Names and birthdates are stripped before any cloud call.
8. **No secrets in git.** Keys live in `.env` (gitignored). `.env.example` lists names only.

## Working rules

- Free by default: the whole app runs locally with no paid key. Paid providers are optional adapters chosen by env vars.
- Audio goes through the `AudioTransport` interface. Do not import Twilio or browser specifics in call logic.
- Python 3.11+, type hints everywhere, `ruff` and `mypy` clean, `pytest` green before every PR.
- Small PRs, one per task, with a description and test evidence. Do not push to `main` directly after the initial scaffold; branch and open a PR.
- Every claim in `docs/SAFETY.md` must link to the test that enforces it.
- Keep `docs/HUMAN_TODO.md` current. If something needs a person (recruiting, nurse grading, a real phone call), put it there rather than faking it.
- Never fabricate results. Results tables are produced by scripts from data files. Synthetic data is labeled synthetic in file names and table captions.

## UI rules

Follow Section 7 of `SPEC.md`. In short: warm off-white and near-black, one muted green or teal accent, serif headings, humanist sans body, large type for the parent pages, full RTL Persian, WCAG AA. No gradients, glows, emoji icons, eyebrow kickers, indigo accents or feature-card grids. Check screens at 375px and 1280px wide and in dark mode before finishing.

## Repo layout (create this)

```
medecho/
  api/            FastAPI app, routes, websockets
  call/           call state machine, speaker (templates, SpokenText), escalation, scheduler
  transports/     base.py (AudioTransport), browser.py, twilio.py
  channels/       web_results.py, email.py, sms.py
  sheet/          two-pass reader, OCR, VLM, diff, redaction
  speech/         STT (faster-whisper), hints, confidence checks, TTS (edge-tts)
  grader/         rules backend, llm backend, 5-run confidence
  conformal/      calibration, thresholds
  redteam/        personas, runner, checks, report
  study/          latin square, analysis, tables
  db/             models, migrations
web/              frontend
tests/
docs/
scripts/
data/             mock sheets, synthetic data (clearly labeled)
```
