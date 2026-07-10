# s.AI — AI-Assisted BOQ Takeoff — Project Spec

Status: scoped, not yet started. Next action: week-1 parser validation (see Milestones).
Date scoped: 2026-07-11. Moved here from the S.Track repo's `docs/newproject.md` on 2026-07-11 — this file is now the single source of truth.

---

## One-Sentence Pitch

s.AI reads a 2D architectural drawing (DWG) and drafts the bill of quantities an engineer currently spends 1–2 months producing by hand — as a reviewable draft with explicit uncertainty flags, measured against the firm's real finished BOQs.

## The Problem (from the manager, ส.บุญมีฤทธิ์วิศวกรรม)

- Estimating a project requires an engineer to manually read CAD drawings (แบบ) and calculate a BOQ — a quantified list of every material.
- Manual takeoff on a large project (hundreds of millions of baht scale) takes 1–2 months.
- Materials get missed (ตกหล่น) — often because the drawing *implies* a need without stating it, and catching that takes engineering judgment. Missed items mean the company eats the cost or never quoted it.
- Estimators also habitually understate early to avoid overwhelming the client; reality costs more.

## What This Project Is (and Is Not)

**Is**: an applied-ML document-extraction pipeline — code parses drawing geometry, an LLM classifies elements and maps them to the firm's item codes with uncertainty flagging, output is a draft Excel BOQ a human engineer reviews. Every capability claim backed by measured accuracy against real ground-truth BOQs.

**Is not**:
- Not an autonomous BOQ generator. The engineer stays in the loop; the draft is the product.
- Not a solution to implied-materials inference. That's the real research problem — out of scope by explicit decision. Scoped only as a flagged-uncertainty feature, never a promise.
- Not model training or fine-tuning. "Learning" = a correction log fed back as few-shot examples/context.
- Not a startup. Considered and rejected during scoping (see Decision Log) — it inverts the user's actual goal.

## File Formats (RESOLVED)

- **2D แบบ**: DWG (real vector geometry) + PNG previews. DWG → DXF via free ODA File Converter, parsed with Python `ezdxf` (lines, layers, blocks, text, dimensions as structured data). PNG = preview only, never measured from.
- **3D**: SketchUp (.skt) — set aside entirely. BOQ takeoff is a 2D task; 3D is a different toolchain.
- **Residual risk to close in week 1**: confirm the firm's actual DWGs contain real vector entities, not a traced raster image inside a DWG wrapper. Only test: open one.

## Architecture

```
DWG ──(ODA converter)──▶ DXF ──(ezdxf)──▶ structured JSON (entities, layers, dims)
                                              │
                              code measures (lengths, counts, areas)
                                              │
                              LLM classifies + maps to item codes + flags uncertainty
                                              │
                                    draft BOQ (Excel) ──▶ engineer reviews/corrects
                                              │
                              correction log ──▶ few-shot context for next runs
```

Architectural law: **code measures, LLM reasons.** Never ask the LLM to measure from an image or estimate a quantity by eye.

## MVP Scope

- Input: one real DWG (converted to DXF).
- Output: first-pass material list with quantities for *explicit, countable* elements — linear runs (walls/pipes/cable), counts from schedules/symbols (doors/panels/fixtures) — mapped to the firm's item codes.
- Everything uncertain is **flagged explicitly**, never silently guessed.
- Target: 70–85% line-item recall on explicit materials, 2–3 project types.
- Value holds at partial coverage: reviewing a draft beats a blank page.

## Milestones (6–8 weeks, eval-first)

1. **Week 1 — parser validation (gate; do nothing else first)**
   Get one real DWG + its matching finished BOQ + explicit permission to show anonymized versions publicly. Convert DWG → DXF. Parse with ezdxf, dump every entity to structured JSON. Render the JSON back over the PNG preview to visually confirm extraction is real and correct. Clean extraction = green light. Dirty = stop and reassess having spent days, not months.
2. **Weeks 2–4 — classifier on explicit elements**
   LLM classifies parsed elements (walls, doors, windows, …) and maps to the firm's item codes. Ship a draft Excel BOQ for one project type.
3. **Weeks 5–6 — correction loop + measurement**
   Correction-log mechanism. Get the manual-takeoff baseline (hours per project, materials-missed count) from the firm. Measure recall/accuracy against the real finished BOQs.
4. **Weeks 7–8 — writeup + optional second project type**
   Error analysis, accuracy report, portfolio writeup **leading with the ML/eval framing**. Second project type only if time allows — bonus, not required.

Hard rules: do not pass week 1 without clean extraction; do not extend past week 8 chasing implied materials.

## Success Criteria

- Primary (portfolio): a measured benchmark — recall/accuracy vs. ground truth, before/after time comparison, error analysis — presentable in an interview as an applied-ML story.
- Secondary (family firm): the engineer actually uses the draft and it saves review time. A win if it happens; not the gate.

## Decision Log

- 2026-07-10: Idea raised by the manager during the Pojjaman evaluation meetings. Honest technical assessment done: pipeline problem, not ML-research; no PhD/team needed; low API cost; vision-only measurement rejected as unreliable.
- 2026-07-11: File format confirmed (DWG + PNG for 2D; SketchUp 3D set aside). The scanned-image worst case is off the table pending the week-1 wrapper check.
- 2026-07-11: Two LLM Council sessions run. Verdict: build as a **6–8 week eval-first project**, not the floated 4–5 month intense build. Reasoning: the resume-valuable artifact (parser + classifier + measured accuracy report) lands by week 8; months 3–5 buy polish a hiring manager never sees. Startup framing ("Thai construction data moat") explicitly rejected — inverts the user's goal of leaving construction for Australian tech work.
- 2026-07-11: Framing rule adopted as standing law: every external artifact leads with document-extraction/LLM-orchestration/eval engineering, never "construction app." Same code, opposite resume value.
- Flagged, unresolved: (1) user's Australian visa/right-to-work pathway is the real gate on the "stay in Australia" goal — verify independently of this project; (2) IP permission for anonymized public use of drawings/BOQs must be obtained with the sample files, or portfolio value drops to interview-conversation only.

## Open Questions — for the aunt (and dad)

### Files + permission
> "ขอไฟล์แบบ .dwg จริงสัก 1 โครงการ พร้อม BOQ ที่ถอดออกมาจากแบบนั้น ได้ไหมครับ (โครงการที่จบแล้วก็ได้)"
> "ผมอยากเอาไฟล์แบบกับ BOQ นี้ไปใช้ในพอร์ตโฟลิโอ/สัมภาษณ์งาน จะปิดชื่อโครงการ/ข้อมูลลูกค้าให้หมด พี่โอเคไหมครับ?"
> "แบบพวกนี้มีชั้น (layer) จัดระเบียบไว้ชัดเจนไหมครับ เช่น ผนัง ท่อ ไฟฟ้า แยกเลเยอร์กัน?"

### BOQ
> "BOQ ที่ทำเสร็จแล้ว ปกติอยู่ในรูปแบบไหนครับ — Excel, หรือในโปรแกรม Pojjaman เลย?"
> "รายการวัสดุใน BOQ ใช้รหัสวัสดุเดียวกับใน Pojjaman ไหมครับ?"
> "ตัวอย่างของที่ตกหล่นบ่อยๆ พอจะนึกออกไหมครับ — เคสไหนที่จำได้ชัดว่า 'อันนี้พลาดบ่อย'?"
> "งานส่วนไหนที่ถอดยากที่สุด/เสียเวลาที่สุด — ไฟฟ้า ประปา โครงสร้าง?"
> "ตอนนี้ทำ BOQ แบบ manual ใช้เวลากี่ชั่วโมง/วันต่อโครงการครับ?" *(needed as the before/after baseline for weeks 5–6)*


