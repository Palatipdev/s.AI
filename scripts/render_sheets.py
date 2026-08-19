"""
Render each structural sheet the demo refers to as its own SVG.

The demo page shows what the pipeline read for the item being computed, so a
foundation item must show the footing plan and a level-2 item must show level 2.
One shared picture would misrepresent what the pipeline is doing.
"""
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sheets as S

sys.stdout.reconfigure(encoding="utf-8")

WIDTH = 900
PILE_SIZE = 0.2


def transform(point, insert):
    """Place a block's geometry at its insertion point, honouring rotation/mirror."""
    x = point[0] * insert.get("xscale", 1)
    y = point[1] * insert.get("yscale", 1)
    r = math.radians(insert.get("rotation", 0) or 0)
    c, s = math.cos(r), math.sin(r)
    return (x * c - y * s + insert["insert"][0],
            x * s + y * c + insert["insert"][1])


def footing_paths(entities, blocks, anchors, sheet):
    """Footing blocks expanded in place, with pile marks tagged separately."""
    out = []
    for e in S.entities_on_sheet(entities, anchors, sheet):
        if e["type"] != "INSERT" or not re.match(r"^F\d", e.get("name", "")):
            continue
        for shape in blocks.get(e["name"], []):
            if shape["type"] == "LWPOLYLINE":
                pts = shape["points"]
                w, h = S.bbox_size(pts)
                kind = ("pile" if abs(w - PILE_SIZE) < 0.05 and abs(h - PILE_SIZE) < 0.05
                        else "line")
                ring = [transform(p, e) for p in pts]
                out.append((kind, ring + [ring[0]]))
            elif shape["type"] == "LINE":
                out.append(("line", [transform(shape["start"], e),
                                     transform(shape["end"], e)]))
    return out


def framing_paths(entities, anchors, sheet):
    """
    The framing grid a floor is measured from.

    Beam labels mark where beams run; drawing them as a grid of ticks shows the
    structure the estimate is built on without reproducing the sheet itself.
    """
    out = []
    labels = []
    for e in S.entities_on_sheet(entities, anchors, sheet):
        if e["type"] in ("TEXT", "MTEXT") and "insert" in e:
            text = S.clean_text(e.get("text", ""))
            m = re.fullmatch(r"([BCS])\d+", text)
            if m:
                labels.append((m.group(1), e["insert"][0], e["insert"][1]))

    kinds = {"B": "beam", "C": "col", "S": "slab"}
    for kind, x, y in labels:
        r = {"B": 0.30, "C": 0.34, "S": 0.16}[kind]
        cls = kinds[kind]
        if kind == "C":
            out.append((cls, [(x - r, y - r), (x + r, y - r),
                              (x + r, y + r), (x - r, y + r), (x - r, y - r)]))
        elif kind == "B":
            out.append((cls, [(x - r, y), (x + r, y)]))
            out.append((cls, [(x, y - r * 0.5), (x, y + r * 0.5)]))
        else:
            out.append((cls, [(x - r, y - r), (x + r, y + r)]))
            out.append((cls, [(x - r, y + r), (x + r, y - r)]))
    return out


def to_svg(paths, width=WIDTH):
    if not paths:
        return ""
    xs = [p[0] for _, ring in paths for p in ring]
    ys = [p[1] for _, ring in paths for p in ring]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span_x, span_y = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
    scale = width / span_x
    height = span_y * scale

    body = []
    for kind, ring in paths:
        pts = " ".join(
            f"{(p[0] - x0) * scale:.1f},{height - (p[1] - y0) * scale:.1f}"
            for p in ring
        )
        body.append(f'<polyline class="{kind}" points="{pts}"/>')
    return (f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg" class="plan">'
            + "".join(body) + "</svg>")


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks = json.loads(src.with_name(src.stem + ".blocks.json").read_text(encoding="utf-8"))
    anchors = S.sheet_anchors(entities)

    drawings = {"S2.01": to_svg(footing_paths(entities, blocks, anchors, "S2.01"))}
    for sheet in ("S2.02", "S2.03", "S2.04"):
        drawings[sheet] = to_svg(framing_paths(entities, anchors, sheet))

    out = src.parent / "sheets.json"
    out.write_text(json.dumps(drawings, ensure_ascii=False), encoding="utf-8")
    for name, svg in drawings.items():
        print(f"  {name}: {len(svg) // 1024} KB")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
