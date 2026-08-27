"""
Foundation concrete for drawings anchored by Thai plan titles (ทับเกษตร set).

The chedi pipeline scoped labels by sheet-number TEXT and read footing geometry
from block definitions. This drawing has neither: sheet numbers exist only in
an index table, and footings are drawn loose on detail sheets. Same method,
different sources — anchors come from plan/detail TITLE texts, pad geometry
from the rectangles drawn beside each แบบขยายฐานราก title.

Label scoping is per package (the chedi F1 lesson, reconfirmed here: the spire
package's F1 pad is 1.2x1.2, the main F1 is 1.5x1.5). Every label is assigned
to its nearest title anchor, so section annotations and the spire's F1 never
leak into a plan's count.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sheets as S
from count_concrete import polygon_area, polygon_perimeter, size

sys.stdout.reconfigure(encoding="utf-8")

# annotated on the F1/F2 sections (0.20 pad + 0.60 pedestal = 0.80 overall,
# 0.05 lean underneath — all three dimensioned beside the sections)
PAD_THICKNESS = 0.2
PEDESTAL_HEIGHT = 0.6

TITLE_KW = ("ผังฐานราก", "ผังโครงสร้าง", "ผังพื้น", "ผังหลังคา", "ผังตำแหน่ง",
            "แบบขยายฐานราก", "แปลนฐานราก", "รูปตัดฐานราก", "แบบขยาย", "รูปตัด", "รูปด้าน")
LABEL_RE = re.compile(r"^(F|SN)\d+")


def titles(entities):
    """[(title, x, y)] for every plan/detail/section title text."""
    out = []
    for e in entities:
        if e["type"] in ("TEXT", "MTEXT") and "insert" in e:
            c = S.clean_text(e.get("text", ""))
            if any(c.startswith(k) for k in TITLE_KW) and len(c) < 60:
                out.append((c, e["insert"][0], e["insert"][1]))
    return out


def nearest(anchors, x, y):
    return min(range(len(anchors)),
               key=lambda i: (anchors[i][1] - x) ** 2 + (anchors[i][2] - y) ** 2)


def pad_geometry(entities, anchors, radius=4.0):
    """
    {type: {pad_area, pad_perimeter, pad_size, column_area, column_perimeter}}
    from the rectangles drawn around each แบบขยายฐานราก <type> title.
    The pad is the largest plausible rectangle; squares ≤0.6 are the pedestal.
    """
    out = {}
    for c, ax, ay in anchors:
        m = re.match(r"^แบบขยายฐานราก\s+([A-Z]+\d+)", c)
        if not m:
            continue
        ftype = m.group(1)
        anchor_pos = (ax, ay)
        pads, cols = [], []
        for e in entities:
            if e["type"] != "LWPOLYLINE" or not e.get("points"):
                continue
            pos = S.position(e)
            if pos is None or abs(pos[0] - ax) > radius or abs(pos[1] - ay) > radius:
                continue
            w, h = size(e)
            if not (0.2 <= w <= 6 and 0.2 <= h <= 6):
                continue
            if abs(w - h) < 0.1:            # square-ish: pad plan view or pedestal
                (cols if w <= 0.6 else pads).append(e)
        if pads:
            pad = max(pads, key=lambda s: polygon_area(s["points"]))
            rec = {
                "pad_size": tuple(round(d, 2) for d in size(pad)),
                "pad_area": polygon_area(pad["points"]),
                "pad_perimeter": polygon_perimeter(pad["points"]),
                "column_area": 0.0, "column_perimeter": 0.0,
            }
            if cols:
                col = min(cols, key=lambda s: polygon_area(s["points"]))
                rec["column_area"] = polygon_area(col["points"])
                rec["column_perimeter"] = polygon_perimeter(col["points"])
                rec["column_size"] = tuple(round(d, 2) for d in size(col))
            rec["detail_at"] = anchor_pos
            out[ftype] = rec
    return out


def plan_counts(entities, anchors):
    """{plan_anchor_index: Counter(type)} — labels scoped to their nearest title."""
    out = defaultdict(Counter)
    for e in entities:
        if e["type"] not in ("TEXT", "MTEXT") or "insert" not in e:
            continue
        c = S.clean_text(e.get("text", "")).strip()
        m = LABEL_RE.match(c)
        if not m or len(c) > 20:
            continue
        i = nearest(anchors, e["insert"][0], e["insert"][1])
        out[i][m.group(0)] += 1
    return out


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    anchors = titles(entities)
    geo = pad_geometry(entities, anchors)

    print("pad geometry from detail sheets:")
    for t, g in sorted(geo.items()):
        print(f"  {t}: pad {g['pad_size']}, pedestal {g.get('column_size', 'NOT FOUND')}")

    counts = plan_counts(entities, anchors)
    for i, cnt in sorted(counts.items()):
        title, ax, ay = anchors[i]
        if not title.startswith(("ผังฐานราก", "แปลนฐานราก")):
            continue                        # labels on details/sections: scoped out
        print(f"\n=== {title} @ ({round(ax)},{round(ay)}) ===")
        # the chedi pairing rule, generalized: a plan reads geometry from its
        # NEAREST foundation-detail package. The spire plan sits beside its own
        # รูปตัดฐานราก, so the far-away F1 detail is not its nearest package —
        # its 1.2x1.2 pad must be measured there, never borrowed from the main
        # building's 1.5x1.5 F1.
        details = [(c, x, y) for c, x, y in anchors
                   if c.startswith(("แบบขยายฐานราก", "รูปตัดฐานราก"))]
        near_c, near_x, near_y = min(
            details, key=lambda d: (d[1] - ax) ** 2 + (d[2] - ay) ** 2)
        pad = ped = 0.0
        for t, n in sorted(cnt.items()):
            g = geo.get(t)
            if not g:
                print(f"  {t} x{n}: NO DETAIL GEOMETRY — flagged, not counted")
                continue
            dx, dy = g["detail_at"]
            if ((dx - near_x) ** 2 + (dy - near_y) ** 2) ** 0.5 > 30:
                print(f"  {t} x{n}: nearest detail package is '{near_c}' but the"
                      f" {t} geometry lives elsewhere — flagged, not counted")
                continue
            pv = n * g["pad_area"] * PAD_THICKNESS
            cv = n * g["column_area"] * PEDESTAL_HEIGHT
            pad += pv
            ped += cv
            print(f"  {t} x{n}: pad {g['pad_size']} x {PAD_THICKNESS} -> {pv:.2f} m3"
                  f"  + pedestal -> {cv:.2f} m3")
        print(f"  pads {pad:.2f} + pedestals {ped:.2f} (height {PEDESTAL_HEIGHT}, annotated)"
              f" = {pad + ped:.2f} m3")


if __name__ == "__main__":
    main()
