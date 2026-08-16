import json
import re
import sys
from collections import Counter
from pathlib import Path

TARGET_SHEET = "S2.01"
PAD_THICKNESS = 0.5      # annotated on the footing sections (0.500, consistent across sheets)
PEDESTAL_HEIGHT = 0.86   # FLAGGED: not annotated, measured from section geometry (siblings show 0.85)
COLUMN_MAX = 0.6         # squares this size or smaller inside a footing block are columns, not pads


def polygon_area(points):
    """Shoelace formula — handles L-shapes, not just rectangles."""
    a = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


def size(shape):
    xs = [p[0] for p in shape["points"]]
    ys = [p[1] for p in shape["points"]]
    return max(xs) - min(xs), max(ys) - min(ys)


def nearest_sheet(anchors, x, y):
    return min(anchors, key=lambda a: (a[1] - x) ** 2 + (a[2] - y) ** 2)[0]


def compute(entities, blocks, target_sheet=TARGET_SHEET, verbose=False):
    """Returns (total_m3, pad_m3, ped_m3, per_type_dict)."""
    geometry = {}
    for name, shapes in blocks.items():
        m = re.match(r"^(F\d)", name)
        if not m:
            continue
        polys = [s for s in shapes if s["type"] == "LWPOLYLINE"]
        if not polys:
            continue

        pad = max(polys, key=lambda s: polygon_area(s["points"]))
        columns = [
            s for s in polys
            if s is not pad
            and all(d <= COLUMN_MAX for d in size(s))
            and not all(abs(d - 0.2) < 0.05 for d in size(s))  # 0.2x0.2 squares are piles
        ]

        geometry[m.group(1)] = {
            "pad_area": polygon_area(pad["points"]),
            "column_area": sum(polygon_area(c["points"]) for c in columns),
        }

    pat = re.compile(r"^[A-Z]{1,2}\d\.\d")
    anchors = [
        (e["text"], e["insert"][0], e["insert"][1])
        for e in entities
        if e["type"] == "TEXT" and pat.match(e.get("text", ""))
    ]

    counts = Counter(
        e["text"].split()[0]
        for e in entities
        if e["layer"] == "FOOTING" and e["type"] == "TEXT"
        and nearest_sheet(anchors, e["insert"][0], e["insert"][1]) == target_sheet
    )

    pad_total = 0.0
    ped_total = 0.0
    per_type = {}
    for t in sorted(counts):
        g = geometry.get(t)
        if not g:
            continue
        pad_v = g["pad_area"] * PAD_THICKNESS * counts[t]
        ped_v = g["column_area"] * PEDESTAL_HEIGHT * counts[t]
        pad_total += pad_v
        ped_total += ped_v
        per_type[t] = {"count": counts[t], "pad_m3": pad_v, "ped_m3": ped_v}

    if verbose:
        print(f"{'type':6} {'n':>3} {'pad m3':>8} {'ped m3':>8}")
        for t, v in per_type.items():
            print(f"{t:6} {v['count']:>3} {v['pad_m3']:>8.2f} {v['ped_m3']:>8.2f}")
        print(f"\npads      {pad_total:.1f} m3   (thickness {PAD_THICKNESS}, from dimensions)")
        print(f"pedestals {ped_total:.1f} m3   (height {PEDESTAL_HEIGHT}, FLAGGED - not annotated)")
        print(f"total     {pad_total + ped_total:.1f} m3   vs BOQ 53 m3")

    return pad_total + ped_total, pad_total, ped_total, per_type


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks = json.loads(src.with_name(src.stem + ".blocks.json").read_text(encoding="utf-8"))
    compute(entities, blocks, verbose=True)
