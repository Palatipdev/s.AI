
from collections import Counter
from pathlib import Path
import sys
import ezdxf


DXF = Path(sys.argv[1])
doc = ezdxf.readfile(DXF)

counts = Counter()
for data in doc.modelspace():
    counts[(data.dxf.layer, data.dxftype())] += 1

print("There are " + str(counts.total()) + " entities")
for (layer, etype), n in counts.most_common():
    print(f"{n:>7}  {layer: <20} {etype}")