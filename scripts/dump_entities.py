import json
import sys
from pathlib import Path

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
    elif etype == "LWPOLYLINE":
        rec["points"] = [(p[0], p[1]) for p in e.get_points()]
    elif etype == "TEXT":
        rec["text"] = e.dxf.text
        rec["insert"] = list(e.dxf.insert)
    elif etype == "MTEXT":
        rec["text"] = e.text          # note: property, not e.dxf.text
        rec["insert"] = list(e.dxf.insert)
    else:
        continue

    entities.append(rec)

OUT = Path(__file__).parent.parent / "data" / "parsed" / (DXF.stem + ".json")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(entities, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"{len(entities)} entities -> {OUT}")
