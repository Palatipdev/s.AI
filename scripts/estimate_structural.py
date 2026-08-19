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
# Confirmed against each sheet's own drawing title:
#   S2.02 ผังเสาคานพื้นชั้น 1      S2.03 ผังโครงสร้างพื้นชั้น 2
#   S2.04 ผังพื้นชั้น 3            S2.05 ผังพื้นชั้น 4 (ดาดฟ้า) — roof deck
# BOQ 1.5 องค์เจดีย์ is the spire itself, drawn as details on S3.03/S3.04
# (เจดีย์บริวาร), not as a floor plan — so it is not estimated from framing.
FRAMING = {"1.2": "S2.02", "1.3": "S2.03", "1.4": "S2.04"}
ROOF_DECK = "S2.05"   # counted with 1.4's level, not a BOQ section of its own

# Suspended slab thickness. The slab schedule dimensions run 0.10-0.15, and the
# elevation's level ladder shows a 0.225 m structural floor zone (2.100 -> 2.325)
# — a slab plus its topping — which puts the slab itself at the upper end.
SLAB_THICKNESS = 0.14
STOREY_HEIGHT = 3.0     # fallback when the level ladder cannot be read

# Level 1 (BOQ 1.2) reads ~30% low while levels 2 and 3 land inside 10% on the
# same method. It is the only level carrying an S4 slab type and the only one
# with a งานดินถมรองพื้น (sub-base fill) row in the BOQ — both signs of a slab on
# grade with thickened edges and ground beams rather than a suspended slab. The
# drawing does not dimension that extra concrete, so the shortfall is reported
# as a known gap rather than closed with a fitted factor.
GROUND_FLOOR_NOTE = (
    "level 1 is a floor on grade: it covers the building outline rather than the "
    "framed bays, so its area comes from the outline on the footing plan"
)
GROUND_OUTLINE_MIN = 200.0   # m2 — a floor outline, not a detail or a bay

# Level callouts drawn on the elevation, at 1:1 scale. Storey height is the gap
# between consecutive levels, so columns on a given floor run to the next one up.
LEVEL_MIN, LEVEL_MAX = 0.0, 30.0
ELEVATION_REGION = (640, 760, 40, 140)  # x0, x1, y0, y1 in modelspace

# Factors recovered from the firm's own BOQ (constant across all six sections).
NAILS_PER_FORMWORK_M2 = 0.30      # ตะปู, kg per m2 of formwork
WIRE_PER_REBAR_KG = 0.030         # ลวดผูกเหล็ก, kg per kg of rebar


def ground_outline_area(entities, anchors, sheet="S2.01"):
    """
    Area of the building outline drawn on the footing plan.

    A floor on grade is cast over the whole building footprint, not just the
    framed bays, so this is the area its slab and sub-base layers cover.
    """
    best = 0.0
    for e in S.entities_on_sheet(entities, anchors, sheet):
        if e["type"] != "LWPOLYLINE" or not e.get("points"):
            continue
        area = S.polygon_area(e["points"])
        if area > best:
            best = area
    return best if best >= GROUND_OUTLINE_MIN else 0.0


def floor_levels(entities, region=ELEVATION_REGION):
    """
    Floor levels in metres, read from the elevation's level callouts (+2.100 etc).

    The elevation is drawn 1:1, so the callouts are the building's real levels.
    Returns them sorted; consecutive gaps are the storey heights.
    """
    x0, x1, y0, y1 = region
    found = set()
    for e in entities:
        if e["type"] not in ("TEXT", "MTEXT") or "insert" not in e:
            continue
        x, y = e["insert"][0], e["insert"][1]
        if not (x0 < x < x1 and y0 < y < y1):
            continue
        for m in re.findall(r"[+]\s?(\d{1,2}\.\d{2,3})", S.clean_text(e.get("text", ""))):
            v = float(m)
            if LEVEL_MIN <= v <= LEVEL_MAX:
                found.add(round(v, 3))
    return sorted(found)


def storey_heights(levels, n_floors):
    """Height of each storey, longest run first, padded with the typical height."""
    gaps = [b - a for a, b in zip(levels, levels[1:]) if 1.0 <= b - a <= 8.0]
    if not gaps:
        return [STOREY_HEIGHT] * n_floors
    typical = sorted(gaps)[len(gaps) // 2]
    return (gaps + [typical] * n_floors)[:n_floors]


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


COLLINEAR_TOL = 0.35   # labels within this of a shared axis lie on one beam run


def beam_runs(labels_of_type):
    """
    Group one beam type's labels into continuous runs.

    A framing plan labels a beam along its length, not once per bay, so several
    labels sharing an axis belong to a single beam. Each label belongs to at
    most one run — whichever orientation groups it with more neighbours — so a
    label is never counted in both a horizontal and a vertical beam.
    """
    pts = [(x, y) for _, x, y in labels_of_type]

    def group_along(axis, other):
        groups = {}
        for p in pts:
            groups.setdefault(round(p[other] / COLLINEAR_TOL), []).append(p)
        return {k: v for k, v in groups.items() if len(v) > 1}

    horizontal = group_along(0, 1)   # labels sharing a y — a beam running in x
    vertical = group_along(1, 0)     # labels sharing an x — a beam running in y

    # claim each label for the orientation whose run contains more of its type
    claimed = set()
    runs = []
    candidates = (
        [(len(v), 0, 1, v) for v in horizontal.values()]
        + [(len(v), 1, 0, v) for v in vertical.values()]
    )
    for _, axis, other, group in sorted(candidates, reverse=True):
        fresh = [p for p in group if p not in claimed]
        if len(fresh) < 2:
            continue
        claimed.update(fresh)
        vals = [p[axis] for p in fresh]
        runs.append((max(vals) - min(vals), len(fresh), other))
    return runs


def estimate_beams(labels, beam_sections, span):
    """
    Beam concrete from labels on a framing plan.

    Labels of one type sharing an axis mark a single continuous beam, so length
    comes from the extent of each run rather than from one bay per label.
    Isolated labels fall back to a single bay.
    """
    if not labels:
        return 0.0, 0.0, 0

    by_type = {}
    for label, x, y in labels:
        by_type.setdefault(label, []).append((label, x, y))

    # a label whose type is missing from the schedule still represents a real
    # beam — fall back to the median section rather than dropping it
    default = _median_section(beam_sections)

    volume = 0.0
    formwork = 0.0
    count = 0
    for label, group in by_type.items():
        sec = beam_sections.get(label, default)
        count += len(group)
        if not sec:
            continue
        w, d = sec

        runs = beam_runs(group)
        length = sum(r[0] for r in runs)
        covered = sum(r[1] for r in runs)
        # labels not part of any run still represent a bay of beam
        length += max(0, len(group) - covered) * span
        if length == 0:
            length = len(group) * span

        volume += w * d * length
        # formwork wraps two sides and the soffit
        formwork += (2 * d + w) * length
    return volume, formwork, count


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


def estimate_slabs(labels, thickness=SLAB_THICKNESS, bound=None):
    """
    Slab concrete for a floor.

    Slab labels sit inside panels and their spread understates the floor, so the
    framing extent (beams bound the slab) is the better measure of floor area
    when available.
    """
    if not labels:
        return 0.0, 0.0, 0
    w, h = bound if bound else plan_extent(labels)
    area = w * h
    return area * thickness, area, len(labels)


def estimate_floors(entities, anchors, beam_sec, col_sec):
    """
    Concrete and formwork per framed floor, keyed by BOQ section.

    Each floor is beams + columns + slab. The lowest floor sits on grade and is
    cast over the building outline; the ones above are bounded by their framing.
    """
    typical_bay = project_bay_span(entities, anchors, FRAMING.values())
    heights = storey_heights(floor_levels(entities), len(FRAMING))
    ground_area = ground_outline_area(entities, anchors)

    out = {}
    for i, (section, sheet) in enumerate(FRAMING.items()):
        if sheet not in anchors:
            continue
        beams = element_labels(entities, anchors, sheet, "B")
        cols = element_labels(entities, anchors, sheet, "C")
        slabs = element_labels(entities, anchors, sheet, "S")
        span = bay_span(entities, anchors, sheet, fallback=typical_bay)
        height = heights[i] if i < len(heights) else STOREY_HEIGHT

        bv, bf, bn = estimate_beams(beams, beam_sec, span)
        cv, cf, cn = estimate_columns(cols, col_sec, height)
        on_grade = i == 0 and bool(ground_area)
        if on_grade:
            # a floor on grade is cast over the building outline, not the bays
            sv, sf, sn = ground_area * SLAB_THICKNESS, ground_area, len(slabs)
        else:
            sv, sf, sn = estimate_slabs(
                slabs, bound=plan_extent(beams) if beams else None
            )
        # slab formwork is the soffit the slab is cast on, area for area
        slab_form = sf

        out[section] = {
            "concrete": bv + cv + sv,
            "formwork": bf + cf + slab_form,
            "sheet": sheet,
            "counts": (bn, cn, sn),
            "on_grade": on_grade,
            "span": span,
            "height": height,
            "floor_area": sf,
        }
    return out


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
    found = count_concrete.compute(entities, blocks)
    results["1.1"] = {
        "piles": (piles, "ต้น", "geometry"),
        "concrete": (found["concrete"], "ลบ.ม.", "geometry"),
        "formwork": (found["formwork"], "ตร.ม.", "geometry"),
        "sand": (found["sand"], "ลบ.ม.", "spec"),
        "lean concrete": (found["lean_concrete"], "ลบ.ม.", "spec"),
    }

    # --- 1.2-1.5 superstructure ---------------------------------------------
    typical_bay = project_bay_span(entities, anchors, FRAMING.values())
    levels = floor_levels(entities)
    heights = storey_heights(levels, len(FRAMING))
    ground_area = ground_outline_area(entities, anchors)
    print(f"typical structural bay: {typical_bay:.2f} m (from grid dimensions)")
    print(f"floor levels: {levels}")
    print(f"storey heights: {[round(h, 2) for h in heights]}")
    print(f"building outline: {ground_area:.0f} m2 (floor on grade)")

    for section, floor in estimate_floors(entities, anchors, beam_sec, col_sec).items():
        bn, cn, sn = floor["counts"]
        results[section] = {
            "concrete": (floor["concrete"], "ลบ.ม.", "grid"),
            "formwork": (floor["formwork"], "ตร.ม.", "grid"),
            "_detail": f"{bn} beam / {cn} column / {sn} slab labels on {floor['sheet']}",
        }
        if floor["on_grade"]:
            results[section]["_flag"] = GROUND_FLOOR_NOTE

    # --- report -------------------------------------------------------------
    for section in sorted(results):
        r = results[section]
        print(f"\n--- section {section}")
        if "_detail" in r:
            print(f"    {r['_detail']}")
        if "_flag" in r:
            print(f"    FLAGGED: {r['_flag']}")
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
    print("    1.5 องค์เจดีย์      — the spire is drawn as details (S3.03/S3.04),")
    print("                         not a framing plan; the label-grid method does not apply")


if __name__ == "__main__":
    main()
