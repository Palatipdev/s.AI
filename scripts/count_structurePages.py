import json
import re
import sys
from collections import defaultdict
from pathlib import Path

entities = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

pat = re.compile(r"^[A-Z]\d\.\d")

# drawing_no -> list of (x, y) positions
sheets = defaultdict(list)
for e in entities:
    if e["type"] == "TEXT" and pat.match(e.get("text", "")):
        name = e["text"]
        if name.startswith("S"):
            sheets[name].append((round(e["insert"][0]), round(e["insert"][1])))

for name in sorted(sheets):
    positions = sheets[name]
    dup = " [DUPLICATE]" if len(positions) > 1 else ""
    print(f"{name}{dup}  x{len(positions)}  {positions}")
