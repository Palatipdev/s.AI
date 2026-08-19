# s.AI — reading construction quantities out of CAD drawings

**[Live demo →](https://palatipdev.github.io/s.AI/)**

A bill of quantities lists every material a building needs. An engineer spends weeks
producing one by hand from CAD drawings, because almost none of those numbers are
written in the drawing — they are counted, measured, and computed from it.

This pipeline does that automatically for the structural chapter of a real project,
then scores itself against the bill of quantities the engineers actually produced.

## Result

**9 of 13 line items land within ±10%** — the accuracy band the firm's head engineer
named as the point where a quantity is useful as an independent check on a purchase order.

| BOQ section | Concrete | Formwork | Nails | |
|---|---|---|---|---|
| 1.1 foundation | **0%** | 16% | 17% | pile count **exact** |
| 1.2 level 1 | **6%** | 15% | 15% | floor on grade |
| 1.3 level 2 | **1%** | **2%** | **1%** | |
| 1.4 level 3 | **0%** | **8%** | **9%** | |

```
python scripts/eval.py "data/parsed/<project>.json"
```

## How a quantity gets built

The BOQ says 66 piles. That number appears nowhere in the drawing.

Footings are placed as CAD **blocks**, and each block *definition* — geometry the
visible drawing never shows — holds its pile marks as 0.20 m squares, the size named
in the BOQ line itself. Counting squares per footing type and placements per sheet
gives the total. Finding that the answer lived inside the block definitions is what
the rest of the pipeline is built on.

Beams need three sheets at once: the section from a schedule, the run length from a
framing plan, and the storey height from the elevation's level ladder. The pipeline
reads all 24 sheets and joins them.

## Pipeline

```
DWG ──▶ DXF ──▶ parse ──▶ scope to sheet ──▶ measure ──▶ score against BOQ
        (ODA)   (ezdxf)   (drawing number)   (geometry)   (eval harness)
```

| Script | Does |
|---|---|
| `dump_entities.py` | DXF → JSON: 54,889 entities plus 385 block definitions |
| `sheets.py` | Sheet regions, sized from the spacing between title blocks |
| `schedules.py` | Beam and column cross-sections from the schedule sheets |
| `count_piles.py` | Pile count from footing blocks |
| `count_concrete.py` | Foundation concrete, formwork, blinding layers |
| `estimate_structural.py` | Concrete and formwork for every framed floor |
| `eval.py` | Scores the lot against the real BOQ |
| `render_sheets.py` | Draws each sheet the demo cites, straight from its entities |
| `classify.py` | LLM classification of ambiguous elements (Claude API, structured output) |

## What it does not do

Reported as out of scope with a reason, never filled in with a plausible guess:

- **Reinforcement** — bar weights need bending schedules the drawing does not carry,
  and vary 79–192 kg/m³ by structural role. No constant would be honest.
- **Excavation** — a site-wide strip, not the per-footing pits the geometry describes.
- **The spire** — drawn as details rather than a framing plan.
- **Formwork** currently reads 15–17% low across every section. The consistency points
  at one unmodelled surface rather than scattered error.

A quantity a reviewer cannot trust costs more to check than to redo. That is why every
line is scored against ground truth and every gap is named.

## Running it

```bash
pip install ezdxf anthropic pydantic python-dotenv pandas matplotlib pillow
python scripts/dump_entities.py path/to/drawing.dxf     # DXF → JSON
python scripts/eval.py data/parsed/drawing.json         # scorecard
python scripts/export_demo.py data/parsed/drawing.json  # demo data
python scripts/build_demo_page.py index.html            # rebuild the page
```

Drawings and quantities are used with the firm's permission; the files themselves are
not in this repository and project details are withheld.
