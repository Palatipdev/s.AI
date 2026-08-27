"""
Score the pipeline against the second project's estimate (ทับเกษตร + ทิม).

Ground truth is the contractor's ปร.4 workbook, transcribed by hand — one tab
per building. Same ±10% band as the first project's eval.

This BOQ carries a known internal inconsistency the pipeline itself surfaced:
for flat pads, concrete/formwork = pad area/perimeter no matter the thickness
(t cancels). The drawing's F1 implies 0.375. The ทับเกษตร tab's rows sit at
12/31.68 = 0.379 — consistent. The ทิม tab's rows sit at 5/18 = 0.278 — its own
concrete and formwork rows cannot both match any flat pad. The formwork row
agrees with the drawing; the concrete row matches an 11-footing count where the
plan draws (and labels) 14, and all six ทิม tabs repeat the same copied numbers.
Scored as FLAG with the evidence, not treated as pipeline error.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import count_foundation_titled as CF

sys.stdout.reconfigure(encoding="utf-8")

ACCURACY_TARGET = 0.10

# which drawn plan is which building: the y=1671 plan sits beside the six
# tiered roof plans (+8.10 .. +14.85) and the ฉัตรทับเกษตร detail set — the
# tall spired building. The y=1525 plan pairs with the ทิม pavilion roofs.
PLAN_OF = {"ทับเกษตร": (5990, 1671), "ทิม (per building)": (5978, 1525)}

# (building, item, quantity, unit) from the ปร.4 tabs, foundation section
BOQ = [
    ("ทับเกษตร", "คอนกรีตผสมเสร็จ 240 ksc", 12.0, "ลบ.ม.", "pads_m3"),
    ("ทับเกษตร", "ไม้แบบทั่วไป", 31.68, "ตร.ม.", "formwork_m2"),
    ("ทับเกษตร", "ทรายหยาบรองพื้น", 3.0, "ลบ.ม.", "bedding_m3"),
    ("ทิม (per building)", "คอนกรีตผสมเสร็จ 240 ksc", 5.0, "ลบ.ม.", "pads_m3"),
    ("ทิม (per building)", "ไม้แบบทั่วไป", 18.0, "ตร.ม.", "formwork_m2"),
]

# the ทิม concrete row fails the ratio test against its own formwork row —
# the drawing cannot satisfy both, and the formwork row is the one it supports
GROUND_TRUTH_DISPUTED = {("ทิม (per building)", "คอนกรีตผสมเสร็จ 240 ksc")}

OUT_OF_SCOPE = [
    ("pedestal stubs (1.60 ลบ.ม.)", "superstructure is steel; no BOQ row holds them"),
    ("ฐานรากเสาฉัตร (spire)", "priced per ฐาน (6 x 5,500), not by volume; its F1 is "
                              "a different 1.2 m footing — excluded by package scoping"),
    ("ทิม ทรายหยาบ 126 ลบ.ม.", "ground fill, not pad bedding — different material role"),
    ("ตะปู", "factor row: 0.24-0.25 kg/m2 here vs 0.30 on project 1 — "
             "estimator-specific, no geometric basis"),
]


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    plans, _ = CF.compute(entities)

    by_building = {}
    for name, (px, py) in PLAN_OF.items():
        by_building[name] = min(
            plans, key=lambda p: (p["pos"][0] - px) ** 2 + (p["pos"][1] - py) ** 2)

    print("=" * 78)
    print("PIPELINE vs ESTIMATE — project 2 (ทับเกษตร + ทิม), foundation section")
    print("=" * 78)
    print(f"\n{'building':22}{'item':26}{'BOQ':>8}{'pipeline':>10}{'error':>8}  status")
    print("-" * 78)

    passed = scored = 0
    for building, item, truth, unit, key in BOQ:
        actual = by_building[building][key]
        err = abs(actual - truth) / truth
        if (building, item) in GROUND_TRUTH_DISPUTED:
            note = "FLAG (BOQ fails its own ratio test)"
        else:
            ok = err <= ACCURACY_TARGET
            scored += 1
            passed += ok
            note = "PASS" if ok else "FLAG"
        print(f"{building:22}{item[:25]:26}{truth:>8}{actual:>10.2f}{err:>7.0%}  {note}")

    print("-" * 78)
    print(f"{passed}/{scored} undisputed line items within ±{ACCURACY_TARGET:.0%}, "
          f"measured from the drawing")
    print("1 line scored against ground truth that contradicts itself — "
          "see module docstring")

    print("\nout of scope — reported, not guessed:")
    for item, why in OUT_OF_SCOPE:
        print(f"  {item:28} {why}")


if __name__ == "__main__":
    main()
