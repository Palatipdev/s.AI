"""
Read structural element schedules (S3.xx sheets) into cross-section dimensions.

A schedule sheet draws each element type once, at true scale, with its label
beside it: B1 -> 0.20 x 0.50 m, C2 -> 0.30 x 0.30 m. Those sections are what
turns a length or a count into a concrete volume.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sheets as S

# plausible cross-section bounds (m) — filters out rebar ticks and sheet borders
MIN_DIM, MAX_DIM = 0.10, 1.60
MAX_LABEL_DIST = 1.0
# a label must sit closer to its own section than to any neighbouring one, so the
# search radius is capped at half the spacing between labels on that schedule
NEIGHBOUR_FRACTION = 0.45


def _centroid(points):
    return (sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points))


def read_schedule(entities, anchors, sheet, prefix):
    """
    {label: (width, depth)} for every `prefix`-labelled element drawn on `sheet`.
    Matches each label to the nearest plausibly-sized rectangle.
    """
    ents = S.entities_on_sheet(entities, anchors, sheet)

    boxes = []
    for e in ents:
        if e["type"] != "LWPOLYLINE" or not e.get("points"):
            continue
        w, h = S.bbox_size(e["points"])
        if MIN_DIM <= w <= MAX_DIM and MIN_DIM <= h <= MAX_DIM:
            boxes.append((_centroid(e["points"]), w, h))

    pat = re.compile(rf"^{prefix}\d+$")
    labels = []
    for e in ents:
        if e["type"] not in ("TEXT", "MTEXT") or "insert" not in e:
            continue
        label = S.clean_text(e.get("text", ""))
        if pat.match(label):
            labels.append((label, e["insert"][0], e["insert"][1]))
    if not labels:
        return {}

    # how far apart are neighbouring labels on this schedule?
    spacing = MAX_LABEL_DIST
    if len(labels) > 1:
        gaps = []
        for i, (_, x, y) in enumerate(labels):
            d = [((x - ox) ** 2 + (y - oy) ** 2) ** 0.5
                 for j, (_, ox, oy) in enumerate(labels) if i != j]
            if d:
                gaps.append(min(d))
        if gaps:
            spacing = min(MAX_LABEL_DIST, sorted(gaps)[len(gaps) // 2])
    radius = max(0.25, spacing * NEIGHBOUR_FRACTION)

    out = {}
    for label, x, y in labels:
        if label in out:
            continue
        nearby = [
            b for b in boxes
            if ((b[0][0] - x) ** 2 + (b[0][1] - y) ** 2) ** 0.5 <= radius
        ]
        if not nearby:
            continue
        # a section is drawn as nested rectangles (outline + rebar cage) — the
        # outline is the outermost, so take the largest box within the radius
        best = max(nearby, key=lambda b: b[1] * b[2])
        out[label] = (round(best[1], 3), round(best[2], 3))
    return out


def all_schedules(entities, anchors, sheets=("S3.02", "S3.03", "S3.04")):
    """Merge beam and column schedules across the detail sheets."""
    beams, columns = {}, {}
    for sh in sheets:
        if sh not in anchors:
            continue
        for label, dims in read_schedule(entities, anchors, sh, "B").items():
            beams.setdefault(label, dims)
        for label, dims in read_schedule(entities, anchors, sh, "C").items():
            columns.setdefault(label, dims)
    return beams, columns


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    anchors = S.sheet_anchors(entities)
    beams, columns = all_schedules(entities, anchors)

    print("BEAM schedule (width x depth, m)")
    for k in sorted(beams, key=lambda s: (len(s), s)):
        w, d = beams[k]
        print(f"  {k:5} {w:.2f} x {d:.2f}   area {w * d:.4f} m2")
    print("\nCOLUMN schedule (width x depth, m)")
    for k in sorted(columns, key=lambda s: (len(s), s)):
        w, d = columns[k]
        print(f"  {k:5} {w:.2f} x {d:.2f}   area {w * d:.4f} m2")
