# S.Track / SorTrack — Compact Recap

Predecessor project to s.AI. Full history lives in `../s-track/docs/Project-Context.md`; this is the one-page version so s.AI sessions don't need to load that repo.

## What it was

Inventory and logistics control system for ส.บุญมีฤทธิ์วิศวกรรม (the family construction firm). Brand name **SorTrack** externally, `S.Track` internally. Built solo in ~2–3 weeks (late June – early July 2026), from near-zero full-stack knowledge.

## What got built (Phase A, complete and demoed)

- **Stack**: Next.js 16 (App Router) + Tailwind v4 frontend; Python FastAPI + SQLAlchemy backend; Supabase (Postgres + Storage + Auth).
- **Backend**: 15-table Postgres schema, Alembic migrations, ~15 endpoints. Core flow: PO ingest → goods receipt with per-line condition checklist (accepted/rejected/damaged/return-to-supplier) → append-only `stock_movements` ledger + maintained `stock_levels` → withdrawals against projects. Multi-tenant (`company_id` scoping everywhere). Supabase JWT auth verified locally via JWKS (no per-request network round trip).
- **Frontend**: 8 pages (PO list/detail, receive, stock, withdraw, items, locations, shared shell), redesigned in a blue/white letterhead theme (IBM Plex Sans Thai, form-code eyebrows matching the firm's paper FM forms).
- **Demoed live over Zoom** to the firm's management and their ERP vendor, with honest seeded data.

## Why it paused (2026-07-10)

The firm already runs **Pojjaman (พจมาน)** — a mature Thai construction ERP covering BOQ, PR→PO, cost centers, a 5-level item catalog, multi-store inventory, and full equipment lifecycle. A day of vendor meetings established: (1) don't out-build an ERP; (2) the reframed idea — a mobile field-capture front-end feeding Pojjaman via granted read-only SQL/API — still didn't remove a step, because site leaders must key data at their own site anyway. Decision: train site leaders on Pojjaman directly; hold the app. Paused, not failed — a finished, demoed portfolio piece.

## What carried into s.AI

- The client relationship and goodwill (the aunt/manager), plus her stated next pain point: manual BOQ takeoff — which became s.AI.
- Pojjaman context: it holds the firm's item codes and finished BOQs live in/around it. s.AI's item-code mapping should align with those codes (open question in the spec).
- Working rules that survived contact: speed-vs-learning split, vertical slices, terse replies, grilling method, ground-designs-in-the-real-subject (the lesson that killed two wrong versions of S.Track early).

## Interview-defensible points (for reference when drafting materials)

- Built and demoed a full-stack multi-tenant inventory system to real client management and their ERP vendor in one meeting.
- Append-only audit ledger design (movements vs. levels — bank statement vs. balance).
- Local JWKS JWT verification fix (eliminated a per-request auth network round trip that caused intermittent 401s under concurrent navigation).
- The pause itself: scoping judgment — recognized the incumbent ERP owned the office side, documented the integration boundary, and moved to the higher-value problem.
