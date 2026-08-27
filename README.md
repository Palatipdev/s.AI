# s.AI — reading construction quantities out of CAD drawings

**[Live demo →](https://palatipdev.github.io/s.AI/)**

A bill of quantities lists every material a building needs. An engineer spends weeks
producing one by hand from CAD drawings, because almost none of those numbers are
written in the drawing. They are counted, measured, and computed from it.

This pipeline does that automatically for the structural chapter of two real projects,
then scores itself line by line against the quantities the engineers actually produced.

## Status

Complete as scoped. This was planned as a time-boxed evaluation project: parse real
DWGs, measure real quantities, publish the error per line item, stop. It is not a
product and was never meant to become one autonomously producing full BOQs. That
problem needs per-firm onboarding, revision handling, and cross-discipline inference,
and the measurements below are the evidence for why.

What the scope deliberately excludes, with reasons:

- **Reinforcement.** Bar weights need bending schedules the drawings do not carry,
  and vary 79-192 kg/m³ by structural role. No constant would be honest.
- **Excavation.** A site-wide strip, not the per-footing pits the geometry describes.
- **Implied materials.** Catching what a drawing implies but never states takes
  engineering judgment. The pipeline flags uncertainty instead of guessing.
- **Prices.** Nothing in a drawing determines cost.

Every excluded line is reported with its reason. A quantity a reviewer cannot trust
costs more to check than to redo, so nothing is silently filled in.

## Results

**Project 1** (a temple chedi, 55k entities): 9 of 13 line items within ±10%, the
band the firm's head engineer named as useful for checking a purchase order.

| BOQ section | Concrete | Formwork | Nails | |
|---|---|---|---|---|
| 1.1 foundation | **0%** | 16% | 17% | pile count **exact** (66/66) |
| 1.2 level 1 | **6%** | 15% | 15% | floor on grade |
| 1.3 level 2 | **1%** | **2%** | **1%** | |
| 1.4 level 3 | **0%** | **8%** | **9%** | |

**Project 2** (a royal pavilion set, 503k entities, different office, different
conventions): 4 of 4 undisputed foundation lines within ±10%.

| Building | Concrete | Formwork | Sand bedding |
|---|---|---|---|
| Main building | **2%** | **4%** | **2%** |
| Pavilion type | disputed, see below | **7%** | fill, out of scope |

```
python scripts/eval.py "data/parsed/<project1>.json"
python scripts/eval_thapkaset.py "data/parsed/<project2>.json"
```

### The pipeline caught the estimate contradicting itself

For flat footing pads, concrete divided by formwork equals pad area divided by
perimeter. Thickness cancels out. The drawn footing implies 0.375; the main
building's estimate rows sit at 0.379, but the pavilion's sit at 0.278. No pad
of any thickness satisfies both of the pavilion's own rows. Its formwork row
matches the 14 footings drawn and labeled on the plan; its concrete row matches
a count of 11, and all six pavilion tabs repeat the same copied numbers.

The 26% "error" on that line is in the ground truth. An extraction pipeline
precise enough to audit the human estimate was not the goal, but it is the
strongest thing the eval produced.

## How a quantity gets built

The first project's BOQ says 66 piles. That number appears nowhere in the drawing.
Footings are placed as CAD blocks, and each block definition, geometry the visible
drawing never shows, holds its pile marks as 0.20 m squares, the size named in the
BOQ line itself. Counting squares per footing type and placements per sheet gives
the total.

The second project has no footing blocks and no sheet-number title blocks at all,
so the same method runs on different sources: Thai plan-title texts become the
anchors and pad sizes are read off the detail sheets. One rule carried over intact:
a label like F1 only means something inside its own plan-and-detail package. The
same drawing uses F1 for a 1.5 m footing on the main building and a 1.2 m footing
under the spire. Treating labels as global constants produces confidently wrong
quantities on both projects tested.

## Pipeline

```
DWG ──▶ DXF ──▶ parse ──▶ scope to sheet ──▶ measure ──▶ score against BOQ
        (ODA)   (ezdxf)   (title anchors)    (geometry)   (eval per line)
```

| Script | Does |
|---|---|
| `dump_entities.py` | DXF → JSON entities plus block definitions |
| `survey_conventions.py` | Convention report for a new drawing before extraction runs |
| `sheets.py` | Sheet regions, sized from the spacing between title blocks |
| `schedules.py` | Beam and column cross-sections from schedule sheets |
| `count_piles.py` | Pile count from footing blocks (project 1) |
| `count_concrete.py` | Foundation concrete, formwork, blinding (project 1) |
| `estimate_structural.py` | Concrete and formwork for every framed floor (project 1) |
| `count_foundation_titled.py` | Foundations from title-anchored drawings (project 2) |
| `eval.py`, `eval_thapkaset.py` | Score everything against the real BOQs |
| `render_sheets.py` | Draws each sheet the demo cites, straight from its entities |
| `classify.py` | LLM classification of ambiguous elements (structured output) |

## Running it

```bash
pip install ezdxf anthropic pydantic python-dotenv pandas matplotlib pillow
python scripts/dump_entities.py path/to/drawing.dxf     # DXF → JSON
python scripts/survey_conventions.py data/parsed/d.json # what conventions does it use
python scripts/eval.py data/parsed/d.json               # scorecard, project 1
```

Drawings and quantities are used with the firms' permission; the files themselves are
not in this repository and project details are withheld.
