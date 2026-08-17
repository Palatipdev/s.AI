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
# a label sits beside its own section; sections on a schedule are drawn far
# enough apart that a small fixed radius picks the right one
SECTION_RADIUS = 0.55


def _centroid(points):
    return (sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points))


def read_schedule(entities, anchors, sheet, prefix, ents=None):
    """
    {label: (width, depth)} for every `prefix`-labelled element drawn on `sheet`.
    Matches each label to the nearest plausibly-sized rectangle.
    """
    if ents is None:
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

    out = {}
    for label, x, y in labels:
        if label in out:
            continue
        # a section is drawn as nested rectangles (outline + rebar cage) — the
        # outline is the outermost, so take the largest box near the label.
        # Widen once for labels whose section is drawn further off (small
        # lintel-type beams sit apart from the main section grid).
        for radius in (SECTION_RADIUS, MAX_LABEL_DIST):
            nearby = [
                b for b in boxes
                if ((b[0][0] - x) ** 2 + (b[0][1] - y) ** 2) ** 0.5 <= radius
            ]
            if nearby:
                best = max(nearby, key=lambda b: b[1] * b[2])
                out[label] = (round(best[1], 3), round(best[2], 3))
                break
    return out


def all_schedules(entities, anchors, sheets=("S3.02", "S3.03", "S3.04")):
    """
    Merge beam and column schedules across the detail sheets.

    A single element type's section may be drawn on any of the adjacent detail
    sheets, so they are read as one region rather than sheet by sheet.
    """
    present = [s for s in sheets if s in anchors]
    ents = S.entities_near(entities, anchors, present)
    # a section drawn right at a frame edge can fall between two adaptive frames;
    # include the band the detail sheets span so nothing is lost in the seams
    if present:
        xs = [anchors[s][0] for s in present]
        ys = [anchors[s][1] for s in present]
        x0, x1 = min(xs) - S.SHEET_W, max(xs) + 1.0
        y0, y1 = min(ys) - 1.5, max(ys) + S.SHEET_H
        seen = {e.get("handle") for e in ents}
        for e in entities:
            p = S.position(e)
            if p and x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and e.get("handle") not in seen:
                ents.append(e)
                seen.add(e.get("handle"))
    beams = read_schedule(entities, anchors, None, "B", ents=ents)
    columns = read_schedule(entities, anchors, None, "C", ents=ents)
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
