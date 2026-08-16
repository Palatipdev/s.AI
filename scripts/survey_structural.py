"""
Sweep every structural sheet and report what is measurable from geometry.

Exploratory: prints an inventory of elements found per sheet so we can judge
which BOQ rows are reachable, rather than guessing.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sheets as S

sys.stdout.reconfigure(encoding="utf-8")

LABEL_RE = re.compile(r"^(B|C|S|ST|F)(\d+)$")


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks = json.loads(src.with_name(src.stem + ".blocks.json").read_text(encoding="utf-8"))
    anchors = S.sheet_anchors(entities)

    s_sheets = sorted(k for k in anchors if k.startswith("S"))
    print(f"structural sheets found: {', '.join(s_sheets)}\n")

    for sheet in s_sheets:
        ents = S.entities_on_sheet(entities, anchors, sheet)
        if len(ents) < 20:
            continue

        labels = Counter()
        for e in ents:
            if e["type"] in ("TEXT", "MTEXT"):
                c = S.clean_text(e.get("text", ""))
                m = LABEL_RE.match(c)
                if m:
                    labels[c] += 1

        # geometry inventory
        polys = [e for e in ents if e["type"] == "LWPOLYLINE" and e.get("points")]
        lines = [e for e in ents if e["type"] == "LINE"]
        dims = [e for e in ents if e["type"] == "DIMENSION"]

        kinds = defaultdict(set)
        for lab in labels:
            kinds[lab[0] if not lab.startswith("ST") else "ST"].add(lab)

        print(f"--- {sheet}  ({len(ents)} entities)")
        for k, name in (("F", "footings"), ("C", "columns"), ("B", "beams"),
                        ("S", "slabs"), ("ST", "stairs")):
            if kinds.get(k):
                types = sorted(kinds[k], key=lambda s: (len(s), s))
                n = sum(labels[t] for t in types)
                print(f"    {name:9} {len(types):>2} types, {n:>3} labels: {', '.join(types[:12])}")
        print(f"    geometry: {len(polys)} polylines, {len(lines)} lines, {len(dims)} dimensions")

        if dims:
            vals = sorted({round(d["measurement"], 3) for d in dims if d["measurement"] > 0.01})
            print(f"    dimension values: {vals[:14]}")
        print()


if __name__ == "__main__":
    main()
