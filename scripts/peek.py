import json, sys
from pathlib import Path
entities = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

layers = {}


for e in entities:
    if e["type"] != "INSERT":
        continue
    x, y = e["insert"][0], e["insert"][1]
    if 990 < x < 1010 and 180 < y < 200:   # rough F1 footing box — adjust to a real one
        print(e["layer"], e["name"], round(x), round(y))