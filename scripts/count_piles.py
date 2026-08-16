import json
import re
import sys
from collections import Counter
from pathlib import Path

TARGET_SHEET = "S2.01"
PILE_SIZE = 0.2  # เสาเข็ม 0.20x0.20 — a pile mark is a 0.2x0.2 square in the footing block


def square_size(shape):
    xs = [p[0] for p in shape["points"]]
    ys = [p[1] for p in shape["points"]]
    return max(xs) - min(xs), max(ys) - min(ys)


def nearest_sheet(anchors, x, y):
    return min(anchors, key=lambda a: (a[1] - x) ** 2 + (a[2] - y) ** 2)[0]


def compute(entities, blocks, target_sheet=TARGET_SHEET, verbose=False):
    """Returns (total_piles, counts_per_type, pile_value_per_type)."""
    # derive piles-per-footing-type from the footing block definitions:
    # count 0.2x0.2 squares inside each block named F1-*, F2-*, ...
    pile_value = {}
    for name, shapes in blocks.items():
        m = re.match(r"^(F\d)", name)
        if not m:
            continue
        n = sum(
            1 for s in shapes
            if s["type"] == "LWPOLYLINE"
            and all(abs(d - PILE_SIZE) < 0.05 for d in square_size(s))
        )
        if n:
            pile_value[m.group(1)] = n

    pat = re.compile(r"^[A-Z]{1,2}\d\.\d")
    anchors = [
        (e["text"], e["insert"][0], e["insert"][1])
        for e in entities
        if e["type"] == "TEXT" and pat.match(e.get("text", ""))
    ]

    footings = [
        e["text"]
        for e in entities
        if e["layer"] == "FOOTING" and e["type"] == "TEXT"
        and nearest_sheet(anchors, e["insert"][0], e["insert"][1]) == target_sheet
    ]

    counts = Counter(t.split()[0] for t in footings)
    total = sum(counts[t] * pile_value.get(t, 0) for t in counts)

    if verbose:
        print("piles per footing type (from block definitions):", pile_value)
        print(f"sheet {target_sheet}: {len(footings)} footing labels")
        print(counts)
        print("total piles:", total)

    return total, dict(counts), pile_value


if __name__ == "__main__":
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks = json.loads(src.with_name(src.stem + ".blocks.json").read_text(encoding="utf-8"))
    compute(entities, blocks, verbose=True)
