"""
Foundation concrete for drawings anchored by Thai plan titles (ทับเกษตร set).

The chedi pipeline scoped labels by sheet-number TEXT and read footing geometry
from block definitions. This drawing has neither: sheet numbers exist only in
an index table, and footings are drawn loose on detail sheets. Same method,
different sources — anchors come from plan/detail TITLE texts, pad geometry
from the rectangles drawn beside each แบบขยายฐานราก title.

Label scoping is per package (the chedi F1 lesson, reconfirmed here: the spire
package's F1 pad is 1.2x1.2, the main F1 is 1.5x1.5). Every label is assigned
to its nearest title anchor, and a plan reads geometry only from its nearest
foundation-detail package, so the spire's F1 never borrows the main F1.
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
# 0.05 bedding underneath — all dimensioned beside the sections)
PAD_THICKNESS = 0.2
PEDESTAL_HEIGHT = 0.6
BEDDING_THICKNESS = 0.05

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
    {type: geometry} from the rectangles drawn around each แบบขยายฐานราก title.
    The pad is the largest plausible rectangle; squares ≤0.6 are the pedestal.
    """
    out = {}
    for c, ax, ay in anchors:
        m = re.match(r"^แบบขยายฐานราก\s+([A-Z]+\d+)", c)
        if not m:
            continue
        ftype = m.group(1)
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
                "detail_at": (ax, ay),
            }
            if cols:
                col = min(cols, key=lambda s: polygon_area(s["points"]))
                rec["column_area"] = polygon_area(col["points"])
                rec["column_size"] = tuple(round(d, 2) for d in size(col))
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


def compute(entities):
    """
    One result dict per foundation plan:
    {title, pos, counts, pads_m3, pedestals_m3, formwork_m2, bedding_m3, flagged}
    """
    anchors = titles(entities)
    geo = pad_geometry(entities, anchors)
    details = [(c, x, y) for c, x, y in anchors
               if c.startswith(("แบบขยายฐานราก", "รูปตัดฐานราก"))]

    plans = []
    for i, cnt in sorted(plan_counts(entities, anchors).items()):
        title, ax, ay = anchors[i]
        if not title.startswith(("ผังฐานราก", "แปลนฐานราก")):
            continue                        # labels on details/sections: scoped out
        # the chedi pairing rule, generalized: a plan reads geometry from its
        # NEAREST foundation-detail package. The spire plan sits beside its own
        # รูปตัดฐานราก, so the far-away F1 detail is not its nearest package —
        # its 1.2x1.2 pad must be measured there, never borrowed.
        near_c, near_x, near_y = min(
            details, key=lambda d: (d[1] - ax) ** 2 + (d[2] - ay) ** 2)
        rec = {"title": title, "pos": (round(ax), round(ay)), "counts": dict(cnt),
               "pads_m3": 0.0, "pedestals_m3": 0.0, "formwork_m2": 0.0,
               "bedding_m3": 0.0, "flagged": {}}
        for t, n in sorted(cnt.items()):
            g = geo.get(t)
            if not g:
                rec["flagged"][t] = "no detail geometry"
                continue
            dx, dy = g["detail_at"]
            if ((dx - near_x) ** 2 + (dy - near_y) ** 2) ** 0.5 > 30:
                rec["flagged"][t] = f"nearest detail package is '{near_c}', geometry lives elsewhere"
                continue
            rec["pads_m3"] += n * g["pad_area"] * PAD_THICKNESS
            rec["pedestals_m3"] += n * g["column_area"] * PEDESTAL_HEIGHT
            rec["formwork_m2"] += n * g["pad_perimeter"] * PAD_THICKNESS
            rec["bedding_m3"] += n * g["pad_area"] * BEDDING_THICKNESS
        plans.append(rec)
    return plans, geo


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    plans, geo = compute(entities)

    print("pad geometry from detail sheets:")
    for t, g in sorted(geo.items()):
        print(f"  {t}: pad {g['pad_size']}, pedestal {g.get('column_size', 'NOT FOUND')}")

    for p in plans:
        print(f"\n=== {p['title']} @ {p['pos']} ===")
        for t, n in sorted(p["counts"].items()):
            note = f"  [{p['flagged'][t]}]" if t in p["flagged"] else ""
            print(f"  {t} x{n}{note}")
        print(f"  pads {p['pads_m3']:.2f} + pedestals {p['pedestals_m3']:.2f} "
              f"(height {PEDESTAL_HEIGHT}, annotated) = "
              f"{p['pads_m3'] + p['pedestals_m3']:.2f} m3; "
              f"formwork {p['formwork_m2']:.2f} m2; bedding {p['bedding_m3']:.2f} m3")


if __name__ == "__main__":
    main()
