# Devin brief: build all of MedEcho

You are building the whole project described in `SPEC.md`, following the rules in `AGENTS.md`. Finish everything in the Section 9 checklist of `SPEC.md`. Work autonomously, and keep going until every box is done.

## How to work

- Work in milestones, in this order. One branch and one pull request per milestone, merged to `main` only after tests pass in CI. If you have permission to merge your own PRs after green CI, do so and continue. Otherwise stack the branches and continue.
- Start every milestone by writing the tests that define done, then implement.
- After each milestone, update `docs/HUMAN_TODO.md` and tick the matching boxes in `SPEC.md` Section 9.
- Do not stop to ask questions about choices the spec already makes. Pick sensible defaults and document them in `docs/ARCHITECTURE.md`.
- Everything must run on a Mac laptop with no paid keys (see "Free by default").

## Milestones

1. **Scaffold.** Repo layout from `AGENTS.md`, `pyproject.toml`, ruff, mypy, pytest, pre-commit, GitHub Actions CI, FastAPI app with health route, SQLite models, frontend scaffold, `make run` and `make test`.
2. **Speaker and call state machine.** `SpokenText` type, English and Persian template library using shame-free AHRQ phrasing, finite-state call flow (intro, open question, grade, re-teach, re-check, escalate, wrap-up), the live "AI-generated medical words" counter computed from `SpokenText`. Hypothesis property test for the speaker invariant.
3. **Escalation.** English and Persian warning-phrase detection with table-driven tests including near-misses. Interrupts any state. Family alert event.
4. **Grader and conformal layer.** `rules` backend, `llm` backend (Anthropic, OpenAI, Ollama adapters, skipped when no key), 5-run confidence, calibration script, synthetic labeled calibration set, per-language thresholds and coverage report.
5. **Speech.** faster-whisper STT with sheet-derived vocabulary hints, word-level confidence checks on numbers, negations and drug names, clarifying re-ask flow, edge-tts voices for English and fa-IR, code-switching handling, speech benchmark script.
6. **Sheet reading.** Two-pass reader (OCR plus optional VLM plus a rules fallback), field diff and disagreement flags, local redaction of names and birthdates, crop-strip generation for the family confirm screen, mock sheet generator (3 fictional sheets, practice-only) and 40+ degraded-photo variants with ground truth, scoring script.
7. **Transports and channels.** `AudioTransport` interface, full `BrowserTransport` over WebSocket, complete flag-gated `TwilioTransport` and SMS/MMS, family message channels (web results page default, SMTP email optional).
8. **Web app.** All screens in `SPEC.md` Section 7, in English and Persian (RTL), following the UI rules exactly. Verify at 375px and 1280px, light and dark. Include the `/demo` split screen.
9. **Scheduler and history.** 2-minute in-call re-check, 48-hour callback, history page, demo mode with shortened timers and seeded randomness.
10. **Red-team harness.** 200+ scripted simulated calls across all persona types in English and Persian, automatic checks for improvised speech and missed escalation, report generator.
11. **Study toolkit.** Latin-square generator, consent form text, CSV templates, analysis scripts that produce tables 1 to 7, with clearly labeled synthetic example data so everything runs.
12. **Docs and final pass.** `ARCHITECTURE.md` (mermaid), `RUNNING.md`, `SAFETY.md` (each claim linked to its test), `STUDY.md`, generated `RESULTS.md`, `HUMAN_TODO.md`. Run the full test suite and red team, fix everything, and make sure a fresh clone runs with the documented commands.

## Definition of done

- Fresh clone, `make setup && make run` starts the app, and a browser call completes end to end in English and in Persian using only free local components.
- `make test` is green. CI is green on `main`.
- The red-team run reports 0 improvised spoken strings and 100% escalation recall on the persona set.
- Every item in `SPEC.md` Section 9 is checked.
- `docs/HUMAN_TODO.md` lists exactly what still needs people.
