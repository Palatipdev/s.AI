import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import ezdxf

DXF = Path(sys.argv[1])
doc = ezdxf.readfile(DXF)

entities = []
for e in doc.modelspace():
    etype = e.dxftype()
    rec = {"handle": e.dxf.handle, "layer": e.dxf.layer, "type": etype}

    if etype == "LINE":
        rec["start"] = list(e.dxf.start)
        rec["end"] = list(e.dxf.end)
    elif etype == "INSERT":
        rec["name"] = e.dxf.name
        rec["insert"] = list(e.dxf.insert)
        rec["rotation"] = e.dxf.rotation      # degrees
        rec["xscale"] = e.dxf.xscale          # negative = mirrored
        rec["yscale"] = e.dxf.yscale
    elif etype == "LWPOLYLINE":
        rec["points"] = [(p[0], p[1]) for p in e.get_points()]
    elif etype == "TEXT":
        rec["text"] = e.dxf.text
        rec["insert"] = list(e.dxf.insert)
    elif etype == "MTEXT":
        rec["text"] = e.text          # note: property, not e.dxf.text
        rec["insert"] = list(e.dxf.insert)
    elif etype == "DIMENSION":
        rec["measurement"] = e.get_measurement()   # the actual number
        rec["insert"] = list(e.dxf.text_midpoint)   # where the number sits
    else:
        continue

    entities.append(rec)

OUT = Path(__file__).parent.parent / "data" / "parsed" / (DXF.stem + ".json")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(entities, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"{len(entities)} entities -> {OUT}")

# block definitions: the geometry inside each reusable symbol (piles per footing etc.)
blocks = {}
for block in doc.blocks:
    if block.name.startswith(("*", "$")):  # skip anonymous/system blocks
        continue
    shapes = []
    for e in block:
        etype = e.dxftype()
        if etype == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
            shapes.append({"type": etype, "layer": e.dxf.layer, "points": pts})
        elif etype == "LINE":
            shapes.append({"type": etype, "layer": e.dxf.layer,
                           "start": list(e.dxf.start), "end": list(e.dxf.end)})
    if shapes:
        blocks[block.name] = shapes

BLK = OUT.with_name(DXF.stem + ".blocks.json")
BLK.write_text(json.dumps(blocks, ensure_ascii=False), encoding="utf-8")
print(f"{len(blocks)} block definitions -> {BLK}")
