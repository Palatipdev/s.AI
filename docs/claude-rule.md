# Claude Coding Rules — s.AI

Rules Claude must follow when writing code in this project. Read this at the start of every coding session. Carried over from S.Track with the stack and learning-split examples updated for s.AI.

---

## 0. HIGHEST PRIORITY — Speed vs Learning Split

**Claude writes repeated patterns directly into the codebase. User writes genuinely new patterns only.**

- **Claude writes**: anything the user has already done before in S.Track or here — FastAPI endpoints, Pydantic schemas, SQLAlchemy models, React/Next fetch + state patterns, CRUD boilerplate, file upload plumbing.
- **User writes**: anything genuinely new — a new concept, a new tool, a new pattern never implemented by them before.
- "New" means a concept or pattern the user has not yet implemented themselves, not just a different endpoint.
- Do NOT give code snippets for the user to transcribe letter-by-letter on repeated patterns. Write it directly.
- DO hand off new patterns with hints and let the user attempt first.

**What counts as NEW in s.AI (user writes, with hints):**
- DXF parsing with `ezdxf` — first entity extraction, first layer walk, first dimension read.
- Geometry math — measuring lengths/areas from parsed entities.
- First LLM API call, first structured-output prompt, first classification prompt.
- The evaluation harness — comparing pipeline output to ground-truth BOQ, computing recall/accuracy.
- The correction-log / few-shot feedback loop.

**What counts as REPEATED (Claude writes directly):**
- Any FastAPI endpoint, Pydantic schema, or SQLAlchemy model (learned in S.Track).
- Any React/Next.js frontend work (see Rule 11 — frontend stays AI-heavy).
- Excel/CSV output plumbing after the first one.
- Second-and-later instances of any pattern above once the user has done one.

**Periodic recall tests**: After writing 3–4 instances of the same pattern, randomly assign the next one to the user as a solo task. Claude acts as tutor/crutch only — hints and error fixes, no writing the code.

**Recall over recognition**: Reading Claude's code builds *recognition*, not *recall*. Claude must NOT write more than ~2 repeated-pattern slices in a row without handing the next one back as a solo recall rep. Track this across the session; don't wait to be asked. The goal is recalling the *trigger* ("this situation → this tool/pattern"), not memorizing syntax — looking up API details every time is normal.

---

## 1. The 80 / 20 Split

- **Claude writes ~80% of the code. The user writes the remaining ~20%.**
- The 20% is intentionally where the user learns — **only on genuinely new patterns** (see Rule 0).
- When stopping for the user's 20%, mark it explicitly:
  ```python
  # TODO(user): extract all LINE entities on the WALL layer and sum their lengths
  # hint: ezdxf's modelspace().query("LINE[layer=='WALL']")
  ```
- Do NOT silently fill in the user's portion. If unsure where to stop, ask.

## 2. Vertical Slices, Not Feature Dumps

- Never implement an entire feature in one go.
- **500 lines is too much. Aim for ~50 lines per step.**
- A "step" = one thin vertical slice the user can run, read, and understand before moving on.
- Example for the week-1 parser validation, broken into steps:
  1. DWG → DXF conversion confirmed by hand (no code).
  2. Script that opens the DXF and prints entity counts per layer (~30 lines).
  3. Dump entities to structured JSON (~40 lines).
  4. Render the JSON back over the PNG preview to eyeball extraction (~50 lines).
  5. First measurement: sum lengths of one entity type on one layer (~30 lines).

  Each step ships, runs, and is reviewed before the next begins.

## 3. Stop and Wait Cadence

- After each ~50-line slice: **stop, summarize what was added, and wait for the user**.
- Do not chain slices without confirmation.
- If the user says "continue" without other instructions, proceed to the next planned slice — don't skip ahead.

## 4. Explain as You Go

- **Answers to conceptual questions: 1–2 sentences max, hard cap.** No paragraphs unless the user explicitly asks for more depth. Reading time is the bottleneck.
- For each code slice, at most one short line of *why* (not what — code shows what). Skip explanation entirely if the pattern's already been explained earlier in the project.
- Call out new concepts by name only, don't unpack them unless asked.
- Prefer linking to / quoting the relevant library docs (ezdxf, Anthropic API, FastAPI) over inventing explanations.

## 5. Respect the Stack & Constraints

- **Pipeline**: Python. DWG → DXF via ODA File Converter (manual/scripted), geometry parsing via `ezdxf`, output via `openpyxl`/pandas to Excel.
- **LLM**: Claude API for classification / item-code mapping / uncertainty flagging. Structured outputs. No model training, no fine-tuning.
- **Division of labor is architectural law**: code parses and measures geometry; the LLM reasons over parsed structure. Never ask the LLM to measure from an image or eyeball quantities.
- **Uncertainty is flagged, never silently guessed.** Every output line the pipeline isn't sure about gets an explicit flag for the human reviewer.
- **Eval-first**: every capability claim is backed by measurement against the real ground-truth BOQs. No accuracy claims without numbers.
- If/when a web UI is added: FastAPI + Next.js + Supabase, same conventions as S.Track (verify Next.js APIs against `node_modules/next/dist/docs/`, never assume training-data conventions).
- **Confidentiality**: the firm's drawings and BOQs are proprietary. Nothing from them goes into a public repo, screenshot, or doc without the anonymization permission recorded in the spec.

## 6. Don't Over-Engineer

- No abstractions before there are 3 concrete uses.
- No premature config files, base classes, or wrapper utilities.
- No error handling for cases that can't happen (trust internal calls; validate only at boundaries).
- No comments that restate the code. Only comment when *why* is non-obvious.
- **Scope guard specific to s.AI**: do not chase the implied-materials inference problem. It is out of scope by decision (see spec). If a slice starts drifting toward it, stop and flag.

## 7. Ask Before Risky / Wide-Reaching Changes

- Changes to the eval methodology or ground-truth data → confirm first.
- Renames across many files → confirm first.
- Anything that would put proprietary drawing/BOQ data somewhere public → confirm first, always.
- Destructive Git ops (drop, force-push) → confirm first.

## 8. Learning Hand-Off

- When a slice introduces a new concept the user hasn't met, suggest a single line for `learned.md` so the user can capture it.
- Don't write to `learned.md` directly — that's the user's file.

## 9. Code Review + Architecture Grilling

- **Applies especially to AI-heavy code** — since it wasn't written solo, it needs a comprehension pass so the user can defend it in an interview.
- After any large chunk of Claude-written code lands, do a walkthrough review right after, while context is fresh — not batched before a demo.
- Periodically (before a demo, or when asked), grill the user on the codebase like an interviewer: "why this approach and not X," trace end-to-end for a given input, make them find answers in the actual code.
- Two registers, always: technical (engineer) and plain-customer (the aunt / a non-technical stakeholder).
- Goal: the user can talk through s.AI's architecture confidently in an interview — especially the ML/eval story, since that's the resume framing that matters.

## 10. Session Close-Out

At the end of a coding session, Claude updates:
- `Project-Context.md` → new session entry (what changed, decisions, where to resume).
- Spec's milestone checklist → mark done / add follow-ups.

Claude does NOT update `learned.md` (user-owned).

## 11. Frontend Stays AI-Heavy

Carried from S.Track: frontend (Next.js/React/Tailwind) is not a learning priority — Claude writes it directly without recall-rep pacing. The user's learning focus in s.AI is the pipeline, the LLM integration, and the eval harness. Backend/pipeline code follows the full Rule 0 discipline.

## 12. Interview Framing Discipline

Every README, writeup, demo script, or external description of this project leads with the **applied-ML / document-extraction / evaluation** story, never "a construction app." This is a standing decision from the project's scoping council — the same code reads as niche or as hireable depending entirely on framing. Claude enforces this in every user-facing artifact it drafts.
