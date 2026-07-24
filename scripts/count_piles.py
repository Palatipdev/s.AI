import json
import sys
from pathlib import Path
from collections import Counter

pile_value = {"F1":5, "F2":3, "F3":1, "F4":1}
# loading
entities = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

# counting piles
pile_counts = Counter(e["type"] for e in entities if e["layer"] == "PILE")

# footing labels
footing_texts = Counter(e["text"] for e in entities if e["layer"] == "FOOTING" and e["type"] == "TEXT")

# print a Counter
X_MIN, X_MAX = 983.142, 1026.213    # your S2.01 region
Y_MIN, Y_MAX = 177.665, 207.595

footings = []
for e in entities:
    if e["layer"] != "FOOTING" or e["type"] != "TEXT":
        continue
    x, y = e["insert"][0], e["insert"][1]
    if X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX:
        footings.append(e["text"])
        
counts = Counter(t.split()[0] for t in footings)
total = sum(counts[t] * pile_value[t] for t in counts)
print(counts)
print("total piles:", total)

