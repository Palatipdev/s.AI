from pathlib import Path
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

JSON = Path(sys.argv[1])
entities = json.loads(JSON.read_text(encoding="utf-8"))
fig, ax = plt.subplots()

for e in entities:
    if e["layer"] not in ("PILE", "FOOTING"):
        continue
    if e["type"] == "LINE":
        xs = [e["start"][0], e["end"][0]]
        ys = [e["start"][1], e["end"][1]]
    elif e["type"] == "LWPOLYLINE":
        xs = [p[0] for p in e["points"]]
        ys = [p[1] for p in e["points"]]
    else:
        continue
    ax.plot(xs, ys, linewidth=0.3, color="black")

ax.set_aspect("equal")
fig.savefig("render.png", dpi=200)

