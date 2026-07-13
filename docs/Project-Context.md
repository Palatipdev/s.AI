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

- **Week-1 gate: PASSED.** Real vector geometry confirmed. Files received (DWG + PDF รวมแบบ + xls BOQ), permission granted, DWG → DXF converted, first parser script runs on real data.
- Project: เจดีย์วัดไทยลุมพินี (a chedi/temple). 55,382 entities in modelspace.
- Next: dump entities to structured JSON, then render back over the drawing to visually confirm extraction.

## Open Questions / TODO

- [ ] Slice 2: dump entities to structured JSON (spec week-1 step 3).
- [ ] Slice 3: render parsed JSON back over the PDF/PNG preview to eyeball extraction.
- [ ] Test the pile hypothesis: `PILE` layer has 20 LWPOLYLINEs, BOQ says 66 ต้น — likely grouped per footing. Confirm the relationship.
- [ ] Get the manual-takeoff time baseline (hours/days per project) — needed for the week 5–6 before/after measurement.
- [ ] User to verify Australian post-study visa pathway (485) independently — flagged by both council rounds as the real gate on the "stay in Australia" goal; not a project task but tracked here so it doesn't get lost.

---

## Session History

### Session 2026-07-11: Project bootstrapped from S.Track
- Folder created, docs migrated from the S.Track repo: spec (from `newproject.md`, now deleted there in favor of a pointer), rules (adapted from S.Track's `claude-rule.md` — stack + learning-split examples updated for the pipeline/LLM/eval work), `learned.md` carried over as one continuous log, `strack-recap.md` written as the compact predecessor summary.
- No code. Next session: if sample files have arrived, run week-1 parser validation per the spec. If not, the only task is chasing the files.

### Session 2026-07-13 — Week-1 gate passed, first parser running
- **Goal**: get files, validate the DWG contains real vector geometry, write the first parser slice.
- **Files received**: เจดีย์วัดไทยลุมพินี — `.dwg`, PDF รวมแบบ, `.xls` BOQ. Anonymization permission granted. BOQ↔DWG match confirmed (same title on both).
- **Gate result — PASSED**: Autodesk Viewer showed organized layers (WALL, GRID, PILE, FOOTING, COL, BEAM, DIM, a-sym-*) and crisp vector geometry at zoom. No raster-in-wrapper. ODA File Converter → 2018 ASCII DXF (60 MB) into `data/raw/`.
- **Changes**: `.gitignore` — added `data/`, secrets, scratch (was stock Python template only; proprietary files were unprotected). `scripts/count_entities.py` — user-written, first NEW pattern (ezdxf → modelspace → Counter over (layer, dxftype)).
- **Findings from the entity dump (55,382 entities)**:
  - ~40% of geometry sits on semantically meaningless numeric layers (`1`, `3`, `8`, `10`). Layer names alone cannot classify. This is the justification for the LLM stage.
  - Meaningful structural layers exist and map to BOQ section 1.1 vocabulary: `PILE` (20 LWPOLYLINE), `FOOTING`, `COL` (160), `BEAM`, `WALL` (298 LINE), `GRID`.
  - ~4,500 `INSERT` entities = block instances; the path to counting doors/windows/fixtures by block name.
- **BOQ structure**: fully itemized (qty, unit, unit cost, total). But most rows are *derived*, not drawn — excavation volume, concrete m³, rebar kg, formwork m². Only some are directly countable (piles, doors). Implication for eval: score recall **per class** (countable / derivable / rule-of-thumb factor), not one blended number.
- **Next**: slice 2 — dump entities to structured JSON.

<!--
Template for the next session:

### Session YYYY-MM-DD — <short title>
- **Goal**: …
- **Changes**: files touched, key commits.
- **Decisions**: any non-obvious choices and why.
- **Unfinished**: what's mid-flight, where to resume.
- **Next**: explicit next step for the following session.
-->
