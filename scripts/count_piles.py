import json
import re
import sys
from collections import Counter
from pathlib import Path

TARGET_SHEET = "S2.01"
pile_value = {"F1": 5, "F2": 3, "F3": 1, "F4": 1}  # TODO: read from paired S3 detail

entities = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

# 1. sheet anchors: every drawing-number label and its position
pat = re.compile(r"^[A-Z]{1,2}\d\.\d")
anchors = [
    (e["text"], e["insert"][0], e["insert"][1])
    for e in entities
    if e["type"] == "TEXT" and pat.match(e.get("text", ""))
]

# 2. assign each footing label to its nearest sheet anchor
def nearest_sheet(x, y):
    return min(anchors, key=lambda a: (a[1] - x) ** 2 + (a[2] - y) ** 2)[0]

footings = [
    e["text"]
    for e in entities
    if e["layer"] == "FOOTING" and e["type"] == "TEXT"
    and nearest_sheet(e["insert"][0], e["insert"][1]) == TARGET_SHEET
]

# 3. count per type x piles-per-type
counts = Counter(t.split()[0] for t in footings)
total = sum(counts[t] * pile_value[t] for t in counts)

print(f"sheet {TARGET_SHEET}: {len(footings)} footing labels")
print(counts)
print("total piles:", total)
