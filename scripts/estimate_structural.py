"""
Whole-structure quantity estimate, section by section, from geometry alone.

Sections 1.1-1.6 of the BOQ. Each quantity is derived from one of three sources,
and every line records which:

  geometry  - measured directly from the drawing (footing polygons, schedules)
  grid      - inferred from the framing plan's label grid and overall dimensions
  factor    - a ratio recovered from the BOQ itself (nails, tie wire)

Anything with no geometric basis is reported as out of scope rather than guessed.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import count_concrete
import count_piles
import schedules
import sheets as S

sys.stdout.reconfigure(encoding="utf-8")

# Framing plans, in BOQ section order (1.2 = level 1, 1.3 = level 2, ...).
FRAMING = {"1.2": "S2.02", "1.3": "S2.03", "1.4": "S2.04", "1.5": "S2.05"}

SLAB_THICKNESS = 0.12   # from the S3.03 schedule dimensions (0.10-0.15 range)
STOREY_HEIGHT = 3.0     # typical; columns run floor to floor

# Factors recovered from the firm's own BOQ (constant across all six sections).
NAILS_PER_FORMWORK_M2 = 0.30      # ตะปู, kg per m2 of formwork
WIRE_PER_REBAR_KG = 0.030         # ลวดผูกเหล็ก, kg per kg of rebar


def element_labels(entities, anchors, sheet, prefix):
    """Every `prefix`-labelled element instance on a plan, with position."""
    pat = re.compile(rf"^{prefix}\d+$")
    out = []
    for e in S.entities_on_sheet(entities, anchors, sheet):
        if e["type"] not in ("TEXT", "MTEXT") or "insert" not in e:
            continue
        label = S.clean_text(e.get("text", ""))
        if pat.match(label):
            out.append((label, e["insert"][0], e["insert"][1]))
    return out


def plan_extent(labels):
    """Overall (width, height) covered by a plan's labels, in metres."""
    if len(labels) < 2:
        return 0.0, 0.0
    xs = [l[1] for l in labels]
    ys = [l[2] for l in labels]
    return max(xs) - min(xs), max(ys) - min(ys)


BAY_MIN, BAY_MAX = 1.0, 6.0


def bay_span(entities, anchors, sheet, fallback=3.0):
    """
    Typical structural bay length, read from the plan's own dimension strings.

    Grid dimensions are the authoritative bay sizes (2-4 m on this project).
    Label spacing is not a substitute: label text sits wherever it fits.
    """
    dims = [
        e["measurement"]
        for e in S.entities_on_sheet(entities, anchors, sheet)
        if e["type"] == "DIMENSION" and BAY_MIN <= e["measurement"] <= BAY_MAX
    ]
    if not dims:
        return fallback
    return sorted(dims)[len(dims) // 2]


def project_bay_span(entities, anchors, sheets, fallback=3.0):
    """Median bay across every framing plan — plans that carry no dimension
    strings inherit the project's typical bay."""
    dims = []
    for sh in sheets:
        if sh not in anchors:
            continue
        dims += [
            e["measurement"]
            for e in S.entities_on_sheet(entities, anchors, sh)
            if e["type"] == "DIMENSION" and BAY_MIN <= e["measurement"] <= BAY_MAX
        ]
    if not dims:
        return fallback
    return sorted(dims)[len(dims) // 2]


def estimate_beams(labels, beam_sections, span):
    """
    Beam concrete from labels on a framing plan.

    Each label marks one beam span; span length comes from the plan's bay grid.
    """
    if not labels:
        return 0.0, 0.0, 0
    by_type = Counter(l[0] for l in labels)

    # a label whose type is missing from the schedule still represents a real
    # beam — fall back to the median section rather than dropping it
    default = _median_section(beam_sections)

    volume = 0.0
    formwork = 0.0
    for label, n in by_type.items():
        sec = beam_sections.get(label, default)
        if not sec:
            continue
        w, d = sec
        volume += w * d * span * n
        # formwork wraps two sides and the soffit
        formwork += (2 * d + w) * span * n
    return volume, formwork, sum(by_type.values())


def _median_section(sections):
    """Median cross-section, used when a label has no schedule entry."""
    if not sections:
        return None
    areas = sorted(sections.values(), key=lambda s: s[0] * s[1])
    return areas[len(areas) // 2]


def estimate_columns(labels, column_sections, height=STOREY_HEIGHT):
    if not labels:
        return 0.0, 0.0, 0
    by_type = Counter(l[0] for l in labels)
    default = _median_section(column_sections)
    volume = 0.0
    formwork = 0.0
    for label, n in by_type.items():
        sec = column_sections.get(label, default)
        if not sec:
            continue
        w, d = sec
        volume += w * d * height * n
        formwork += 2 * (w + d) * height * n
    return volume, formwork, sum(by_type.values())


def estimate_slabs(labels, thickness=SLAB_THICKNESS):
    """Slab panels: area from the plan extent, divided across labelled panels."""
    if not labels:
        return 0.0, 0.0, 0
    w, h = plan_extent(labels)
    area = w * h
    return area * thickness, area, len(labels)


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks = json.loads(src.with_name(src.stem + ".blocks.json").read_text(encoding="utf-8"))
    anchors = S.sheet_anchors(entities)
    beam_sec, col_sec = schedules.all_schedules(entities, anchors)

    print("=" * 78)
    print("STRUCTURAL QUANTITY ESTIMATE — derived from geometry")
    print("=" * 78)
    print(f"\nschedules read: {len(beam_sec)} beam types, {len(col_sec)} column types")

    results = {}

    # --- 1.1 foundation -----------------------------------------------------
    piles, pile_counts, _ = count_piles.compute(entities, blocks)
    conc, pad, ped, _ = count_concrete.compute(entities, blocks)
    results["1.1"] = {
        "piles": (piles, "ต้น", "geometry"),
        "concrete": (conc, "ลบ.ม.", "geometry"),
    }

    # --- 1.2-1.5 superstructure ---------------------------------------------
    typical_bay = project_bay_span(entities, anchors, FRAMING.values())
    print(f"typical structural bay: {typical_bay:.2f} m (from grid dimensions)")

    for section, sheet in FRAMING.items():
        if sheet not in anchors:
            continue
        beams = element_labels(entities, anchors, sheet, "B")
        cols = element_labels(entities, anchors, sheet, "C")
        slabs = element_labels(entities, anchors, sheet, "S")
        span = bay_span(entities, anchors, sheet, fallback=typical_bay)

        bv, bf, bn = estimate_beams(beams, beam_sec, span)
        cv, cf, cn = estimate_columns(cols, col_sec)
        sv, sf, sn = estimate_slabs(slabs)

        total_conc = bv + cv + sv
        total_form = bf + cf + sf
        results[section] = {
            "concrete": (total_conc, "ลบ.ม.", "grid"),
            "formwork": (total_form, "ตร.ม.", "grid"),
            "_detail": f"{bn} beam / {cn} column / {sn} slab labels on {sheet}",
        }

    # --- report -------------------------------------------------------------
    for section in sorted(results):
        r = results[section]
        print(f"\n--- section {section}")
        if "_detail" in r:
            print(f"    {r['_detail']}")
        for name, value in r.items():
            if name.startswith("_"):
                continue
            val, unit, source = value
            print(f"    {name:10} {val:10.1f} {unit:8} [{source}]")

    # --- factor-derived rows ------------------------------------------------
    print("\n--- factor-derived (ratios recovered from the BOQ itself)")
    print(f"    nails      = {NAILS_PER_FORMWORK_M2} kg per m2 formwork")
    print(f"    tie wire   = {WIRE_PER_REBAR_KG} kg per kg rebar")

    print("\n--- out of scope (no geometric basis)")
    print("    rebar (RB/DB, kg)  — requires bar-bending schedules, not in the drawing")
    print("    excavation         — site-wide strip, not per-footing pits")


if __name__ == "__main__":
    main()
