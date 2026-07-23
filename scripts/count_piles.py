import json
import sys
from pathlib import Path
from collections import Counter

# loading
entities = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

# counting piles
pile_counts = Counter(e["type"] for e in entities if e["layer"] == "PILE")

# footing labels
footing_texts = Counter(e["text"] for e in entities if e["layer"] == "FOOTING" and e["type"] == "TEXT")

# print a Counter
for e in entities:
    t = e.get("text", "")
    if any(k in t for k in ["ต้น", "เข็ม", "จำนวน", "F1", "F2"]):
        print(repr(t))