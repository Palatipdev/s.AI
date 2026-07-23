import sys
from pathlib import Path

import pandas as pd

XLS = Path(sys.argv[1])
OUT = Path(__file__).parent.parent / "data" / "parsed"
OUT.mkdir(parents=True, exist_ok=True)

xls = pd.ExcelFile(XLS)
print("sheets:", xls.sheet_names)

# flatten one sheet (default: structural) into readable pipe-joined rows
sheet = sys.argv[2] if len(sys.argv) > 2 else "1.งานโครงสร้าง"
df = pd.read_excel(XLS, sheet_name=sheet, header=None)

lines = []
for _, row in df.iterrows():
    vals = [str(v) for v in row.tolist() if pd.notna(v) and str(v).strip()]
    if vals:
        lines.append(" | ".join(vals))

dest = OUT / f"boq_{sheet}.txt"
dest.write_text("\n".join(lines), encoding="utf-8")
print(f"{len(lines)} rows -> {dest}")
