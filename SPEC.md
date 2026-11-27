# MedEcho: Product and Research Spec

**In one line:** a family member photographs any medication instruction sheet. MedEcho then calls the older adult in English or Persian and asks them to explain their medicines in their own words. It grades each item and re-teaches anything missed, using only the sheet's exact wording. A day or two later it calls back to check what stuck, and the family gets a message with audio of anything that didn't.

Track: Presidential Scholars-style Standard track project. Team of 4. Deadline: submit by Dec 23, 5pm ET.

---

## 1. Problem

- Older adults make more than 600,000 emergency visits a year for adverse drug events (CDC).
- About 60% of those involve three drug classes: blood thinners, diabetes drugs and opioids (JAMA 2016).
- About 59% of older adults have trouble using written health materials (AHRQ, cited by ECRI).
- The standard fix is teach-back: the patient explains the plan back in their own words. AHRQ calls it evidence-based. It takes a clinician's time, so it gets skipped, and nobody does it at home a day later, when forgetting actually happens.
- Immigrant seniors have it worst: dense English sheets, adult children who live far away, and no one checking.

## 2. Research question

Agent teach-back made older adults feel taught without helping them remember (Morrow et al., HFES 2020). Can a phone teach-back built on retrieval practice close that gap, safely, and match a human doing AHRQ teach-back?

Prior-art gap summary:
- Hippocratic AI Nurse Co-Pilot: hospital-only, generative. MedEcho is family-started from paper and its voice cannot generate medical content.
- Bickmore virtual nurse: on-screen, menu answers. MedEcho takes free-form spoken answers.
- Morrow 2020: teach-back did not improve memory. MedEcho adds retrieval practice to fix exactly that.
- NoteAid-Chatbot: text and multiple choice. MedEcho is voice, open-ended, graded with evidence.
- UMass Chan (Kapoor): diabetes discharge only. MedEcho covers any sheet, two languages, family in the loop.
- Commercial follow-up calls: scripted "any questions?" check-ins. That is Arm A, the baseline.

## 3. User flow

1. **Snap.** The family member photographs the sheet in the web app.
2. **Confirm.** MedEcho lists each item: drug, dose, timing, food, what to avoid, warning signs, follow-up date. Wherever its two readers disagree, and on every number, the family sees the cropped photo strip and **types the value themselves**.
3. **Record the intro.** The family member records about 5 seconds: "Hi Mom, it's Sara, I set this up to go over your new pills."
4. **The call.** MedEcho calls the parent. The intro plays, then: "I want to make sure the instructions were explained clearly. Can you tell me how you'll take your new medicine?"
5. **Grade.** Each item is marked correct, partial, wrong or missing, with the parent's exact words quoted as evidence.
6. **Re-teach.** Only missed items are re-read, word for word from the sheet, and tied to a routine ("with breakfast"). About two minutes later in the same call, MedEcho asks again.
7. **Escalate.** Warning words like "chest pain," "fell" or "took two" trigger "please call your doctor, or 911 if it's an emergency," plus an immediate family alert.
8. **Message the family.** A summary per item, plus a 6-second audio clip of anything missed.
9. **Callback after 48 hours.** A short retention check, with results added to the family history page.

MedEcho never:
- judges whether the prescription itself is right,
- answers questions that are not on the sheet (it refers them to the pharmacist),
- generates any medical sentence of its own.

## 4. AI system

### A. Two-pass sheet reading
- A vision-language model and classical OCR (Tesseract or PaddleOCR) each extract the items independently.
- A field-by-field comparison flags any disagreement and every dose or frequency number. Flagged fields require the family to type the value.
- Names and birthdates are stripped locally before any cloud call.

### B. Speech recognition tuned to the sheet
- Whisper (local faster-whisper by default; hosted gpt-4o-transcribe optional), given the sheet's drug names, doses and look-alike/sound-alike pairs as a vocabulary hint (initial prompt / hotwords).
- Handles code-switching: Persian sentences with English drug names.
- Word-level confidence is checked on numbers, negations and drug names. If any is low, MedEcho asks a natural clarifying question before grading: "The line cut out. Did you say one pill or two?"

### C. The grader
- Compares the transcript to each confirmed item and outputs a label (correct / partial / wrong / missing) plus the quoted evidence span from the transcript.
- Runs 5 times. The share of runs that say "understood" is its confidence score.
- Pluggable backends: `llm` (Anthropic, OpenAI or local Ollama, chosen by env) and `rules` (deterministic fuzzy matching on normalized drug, number, frequency and negation tokens, works fully offline and is the default in tests and CI).

### D. Conformal safety layer
- The dangerous error is a wrong answer marked "understood."
- On a calibration set graded by nurses, the threshold is set at the conformal quantile of the "understood" scores among items that were actually wrong. That keeps the wrong-marked-understood rate at 5% or less, calibrated separately for English and Persian.
- Anything below the threshold counts as not understood, so MedEcho re-teaches it or flags the family.
- Ship a calibration script that reads a CSV of (language, item_id, grader_score, nurse_label) and writes `calibration.json` with per-language thresholds and the empirical coverage. Ship a synthetic calibration set so the pipeline runs end to end before real nurse labels exist.

### E. A speaker that cannot improvise
- The listener/grader outputs only structured grades (JSON).
- A separate finite-state speaker builds every spoken sentence from fixed AHRQ shame-free phrases plus exact spans from the confirmed sheet.
- No LLM output ever reaches the voice. "Zero improvised medical statements" is a property of how the system is built.
- Enforcement: every string sent to TTS passes through a `SpokenText` type that can only be built from (a) a template id plus slot values that are sheet spans, or (b) a verbatim sheet span. The live counter "AI-generated medical words: 0" is computed from this type, not self-reported.

### F. Retrieval-practice scheduler
- Re-check about 2 minutes later inside the call (configurable, shortened in demo mode).
- Re-teaching anchored to routines.
- The 48-hour callback (configurable; demo mode shortens it to seconds).

### G. Red-team harness
- 200+ simulated calls. Simulated patients are scripted personas (confused, hard of hearing, slurred, code-switching, off-sheet questions, prompt injection such as "ignore your instructions and tell me...", emergency phrases). Scripted personas run with no API key; an optional LLM persona mode adds variety.
- Two automatic checks on every call:
  - Any spoken string that is not from a template or the sheet counts as a failure.
  - Any missed escalation counts as a failure.
- Writes a machine-readable report and a markdown summary table.

### Stack
- Python 3.11+, FastAPI, SQLite (SQLModel or SQLAlchemy), WebSockets for audio.
- Frontend: a small web app (Vite + React + TypeScript, or server-rendered templates; pick one and keep it simple).
- Audio transport behind one interface (see Section 6).
- TTS: `edge-tts` (free, includes fa-IR voices) by default. Azure or Google optional.
- STT: `faster-whisper` local by default.
- OCR: Tesseract (pytesseract) by default, PaddleOCR optional.

## 5. Study (materials the code must support)

Participants: about 30 adults aged 65+, including Persian speakers. Three mock sheets with fictional patients, 3 drugs each, using ISMP look-alike/sound-alike pairs (glipizide/glyburide, hydralazine/hydroxyzine). Sheets are marked "practice only."

Design: every participant does all 3 arms, each with a different sheet. Arm and sheet order counterbalanced with a Latin square. At least 3 days between sessions.

| Arm | What happens |
|---|---|
| A: standard practice | Read the sheet, then a scripted "any questions?" call |
| B: human teach-back | A teammate runs AHRQ's teach-back script by phone |
| C: MedEcho | The full system |

Outcomes: each item scored right after the session and at 48 hours, graded from audio by 2 blinded nurses or pharmacists.

Results tables the analysis code must produce from CSV inputs:
1. Memory, immediate and at 48 hours, A vs B vs C (paired test and mixed model).
2. Grading agreement: MedEcho vs nurse (Cohen's kappa) compared with nurse vs nurse.
3. Conformal: wrong-marked-understood rate with a plain LLM grader vs the conformal grader, by language.
4. Speech recognition: word error rate with and without sheet hints, English vs code-switched Persian, plus accuracy on numbers and negations separately.
5. Sheet reading: field accuracy on 40+ degraded photos, one reader vs two readers with disagreement flags.
6. Red team: improvised statements (expected 0), escalation recall, off-sheet refusal rate.
7. Experience: ease-of-use and comfort survey, including a "did this feel like a test?" item.

## 6. Build requirements

### Browser-call first, phone later
- The default call experience is a browser call: the parent opens a link, taps "Answer", and talks through the device mic and speaker. Audio streams over WebSocket to the server.
- All call logic depends only on an `AudioTransport` interface (receive audio frames in, send audio out, hang up, call state events). Implement `BrowserTransport` fully. Implement `TwilioTransport` (Twilio Media Streams over WebSocket, outbound call via REST, SMS/MMS for the family message) behind the same interface and behind a config flag. It must be complete and documented, and not be required to run anything.
- Family message channel is also an interface: `WebResultsPage` (default, always works), `Email` (SMTP, optional), `Sms` (Twilio, optional).

### Free by default
Everything must run on a laptop with no paid API key: local Whisper, edge-tts, Tesseract, `rules` grader, rule-based sheet reader fallback. Paid or keyed providers (Anthropic, OpenAI, Azure, Twilio) are optional adapters selected by environment variables listed in `.env.example`. If a key is absent, the adapter is skipped with a clear log line and the free path is used.

### Quality bar
- Tests with pytest for every module, CI via GitHub Actions running tests and lint.
- Type hints throughout, `ruff` and `mypy` clean.
- The speaker invariant has a property-based test (hypothesis): for random grader outputs and random sheets, every spoken string is a template or a sheet span.
- Escalation has a table-driven test in English and Persian, including near-misses ("my chest feels fine").
- Deterministic demo mode (`MEDECHO_DEMO=1`) with seeded randomness, shortened timers and prefilled mock sheets.

## 7. UI requirements

The UI must look designed by a person who cares, not generated. Hard rules:
- No gradients on text or backgrounds, no purple/indigo default accent, no glassmorphism, no glow, no emoji used as icons, no stock "sparkle" iconography, no eyebrow kicker text above headings, no three-identical-feature-cards grid, no decorative blobs.
- Palette: warm off-white background, near-black text, one muted clinical green or deep teal accent, one amber for caution, one brick red for emergencies. Define as CSS variables. Support dark mode.
- Type: one serif for headings (for example Source Serif 4 or Fraunces) and one humanist sans for body (for example Source Sans 3 or Inter). Body 18px minimum. The parent-facing pages use 22px minimum and very high contrast, since the users are older adults.
- Layout: generous spacing, a clear single column on mobile, real hierarchy. Buttons are large with clear labels and visible focus states. Meets WCAG AA contrast. Persian pages are fully RTL with an appropriate Persian font (Vazirmatn).
- Copy: plain, warm, short. No marketing fluff. Never the word "incorrect" in parent-facing text.
- Every screen states that MedEcho checks understanding of the sheet as written and does not review the prescription.

Screens:
1. **Family: upload and confirm.** Photo upload (drag/drop and camera), extracted item list, disagreement flags with the cropped photo strip beside an input the family types into, every number requires typed entry. Language selector (English / فارسی).
2. **Family: intro recording.** Record in browser, play back, re-record.
3. **Family: schedule and start.** Start call now or schedule, parent's contact or share link.
4. **Parent: answer page.** One huge "Answer" button, a calm call screen with a simple visual indicator of who is speaking, a large "Hang up". No jargon.
5. **Family: results.** Per-item summary, quoted evidence, audio clip of missed items, escalation banner if triggered.
6. **Family: history.** Timeline of sessions and 48-hour callback results per item.
7. **Demo split screen** (`/demo`): live transcript, confidence re-ask indicator, grade with quoted evidence, word-for-word re-teach, the "AI-generated medical words: 0" counter, escalation alert, language toggle. Built for projecting to judges.

## 8. Safety

- Prescription correctness is out of scope. MedEcho checks understanding of the sheet as written and says so on every screen.
- Family confirmation is required for every number and every reader disagreement.
- The speaker can only say fixed phrases and verbatim sheet text.
- Conformal bound on the most dangerous error, plus abstaining when unsure.
- Escalation: warning words lead to doctor or 911 guidance and a family alert.
- Emotional safety: shame-free AHRQ phrasing, no "incorrect". Family voice intro so calls do not sound like a scam.
- Privacy: names stripped locally, zero-retention API settings, audio deleted after review, mock sheets only in the study.

## 9. Deliverables checklist (everything below must exist at the end)

Code and data:
- [ ] Working end-to-end browser call: upload, confirm, call, grade, re-teach, re-check, escalate, family results, 48h callback, history.
- [ ] Twilio transport and SMS adapter, complete, documented, flag-gated.
- [ ] English and Persian speaker templates and voices.
- [ ] Two-pass sheet reader with disagreement flags, plus a benchmark: a generator that makes 3 mock sheets (fictional patients, practice-only) and 40+ degraded variants (crumple/shadow/glare/angle/blur/low light) with ground-truth JSON, and a script that scores one-reader vs two-reader accuracy.
- [ ] Speech benchmark script: WER with and without hints, numbers and negations accuracy, on supplied or synthetic (TTS-generated) audio.
- [ ] Grader with `rules` and `llm` backends, 5-run confidence.
- [ ] Conformal calibration script, synthetic calibration set, per-language thresholds, coverage report.
- [ ] Red-team harness with 200+ scripted simulated calls, report generator.
- [ ] Study toolkit: Latin-square assignment generator, consent form text, participant ID scheme, data-collection CSV templates, analysis scripts that produce results tables 1 to 7 as markdown and CSV from the templates (with synthetic example data so they run).
- [ ] Demo mode and the `/demo` split screen.

Docs (in `docs/`):
- [ ] `ARCHITECTURE.md` with a diagram (mermaid) and the speaker invariant explained.
- [ ] `RUNNING.md`: setup on macOS, one command to run, how to enable Twilio.
- [ ] `SAFETY.md` mirroring Section 8 with the tests that enforce each claim.
- [ ] `RESULTS.md` generated by scripts from the latest runs.
- [ ] `STUDY.md`: protocol, materials, schedule, consent.
- [ ] `HUMAN_TODO.md`: tasks that need people (recruiting, nurse grading, running Arm B, real phone test), kept current.

## 10. Rubric mapping

| Criterion | Points | What earns it |
|---|---|---|
| Objective and Relevance | 10 | CDC and JAMA numbers, immigrant-senior gap, families as users |
| SI Solution | 20 | Two-pass reading, sheet-tuned code-switching speech, conformal grader, non-improvising speaker |
| Research and Accuracy | 15 | Prior-art table, Morrow as research question, nurse-graded kappa |
| Safety | 10 | Section 8 |
| Process and Learning | 15 | Iterating on red-team results and on before/after sheet hints |
| Use and Validation | 10 | 3-arm study with older adults, 48-hour retention, blinded graders |
| Originality | 10 | Family-started phone teach-back that fixes a known failure, with safety guaranteed by design |
| Video | 10 | Demo screen built to record |

## 11. Roles

| Role | Owns |
|---|---|
| Telephony and speaker | Call state machine, transports, Persian voices |
| AI | Sheet reading, speech, grader, conformal layer, red team |
| Study lead | Recruitment, consent, Arm B sessions, scheduling, nurse coordination |
| Story | Web app UI, paper, video, demo script |
