# Project Context — s.AI

> Rolling log of session-level context. Each session appends a new entry under **Session History** so the next session can pick up without re-deriving state. Keep entries short and factual — code itself is the source of truth.

---

## Project Snapshot

- **Project**: s.AI — AI-assisted BOQ takeoff from CAD drawings (display name s.AI, folder/repo `sAI`).
- **Spec**: `docs/Project-Spec.md` (single source of truth — scope, milestones, decision log, open questions).
- **Rules**: `docs/claude-rule.md` (speed-vs-learning split, slices, terse replies, grilling, framing discipline).
- **Stack (planned)**: Python pipeline (ODA converter → ezdxf → structured JSON), Claude API for classification/mapping/uncertainty, openpyxl/pandas → Excel out. FastAPI + Next.js UI only if/when needed later.
- **Predecessor**: S.Track/SorTrack (`../s-track`), paused 2026-07-10 — see `docs/strack-recap.md`.
- **Working directory**: `C:\Users\riaza\Documents\sAI`
- **Platform**: Windows 11, PowerShell

## Current State

- No code yet. Spec scoped and council-reviewed. Waiting on: one real DWG + matching finished BOQ + anonymization permission from the aunt (Thai questions ready in the spec).
- Gate: week-1 parser validation must pass before anything else gets built.

## Open Questions / TODO

- [ ] Send the file-request message to the aunt (questions in `Project-Spec.md`).
- [ ] Week-1 parser validation once files arrive (DWG → DXF → JSON → render over PNG).
- [ ] Get the manual-takeoff time baseline (hours/days per project) — needed for the week 5–6 before/after measurement.
- [ ] User to verify Australian post-study visa pathway (485) independently — flagged by both council rounds as the real gate on the "stay in Australia" goal; not a project task but tracked here so it doesn't get lost.

---

## Session History

### Session 2026-07-11: Project bootstrapped from S.Track
- Folder created, docs migrated from the S.Track repo: spec (from `newproject.md`, now deleted there in favor of a pointer), rules (adapted from S.Track's `claude-rule.md` — stack + learning-split examples updated for the pipeline/LLM/eval work), `learned.md` carried over as one continuous log, `strack-recap.md` written as the compact predecessor summary.
- No code. Next session: if sample files have arrived, run week-1 parser validation per the spec. If not, the only task is chasing the files.

<!--
Template for the next session:

### Session YYYY-MM-DD — <short title>
- **Goal**: …
- **Changes**: files touched, key commits.
- **Decisions**: any non-obvious choices and why.
- **Unfinished**: what's mid-flight, where to resume.
- **Next**: explicit next step for the following session.
-->
