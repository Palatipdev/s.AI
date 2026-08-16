"""
Score the pipeline's output against the real bill of quantities.

BOQ ground truth is section 1.1 (งานโครงสร้าง ค.ส.ล. ฐานราก ตอม่อ) of the firm's
finished BOQ for this project — transcribed by hand, not derived from the pipeline.
"""
import json
import sys
from pathlib import Path

import count_concrete
import count_piles

sys.stdout.reconfigure(encoding="utf-8")

# Ground truth: (description, quantity, unit) — section 1.1 of the real BOQ.
BOQ = [
    ("เสาเข็มหกเหลี่ยมกลวง 0.20x0.20x6.00 ม.", 66, "ต้น"),
    ("คอนกรีตโครงสร้าง", 53, "ลบ.ม."),
]

ACCURACY_TARGET = 0.10  # ±10% per line item (head engineer, 2026-07-31)


def pct_error(actual, expected):
    return abs(actual - expected) / expected


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks = json.loads(src.with_name(src.stem + ".blocks.json").read_text(encoding="utf-8"))

    piles, _, _ = count_piles.compute(entities, blocks)
    concrete, _, _, _ = count_concrete.compute(entities, blocks)
    pipeline_output = [piles, round(concrete, 1)]

    print(f"{'BOQ line':40} {'ground truth':>14} {'pipeline':>10} {'error':>8}  status")
    print("-" * 90)

    within_target = 0
    for (desc, qty, unit), actual in zip(BOQ, pipeline_output):
        err = pct_error(actual, qty)
        ok = err <= ACCURACY_TARGET
        within_target += ok
        status = "PASS" if ok else "FLAG"
        print(f"{desc[:40]:40} {qty:>10} {unit:<3} {actual:>10} {err:>7.1%}  {status}")

    print("-" * 90)
    print(f"{within_target}/{len(BOQ)} line items within ±{ACCURACY_TARGET:.0%}")


if __name__ == "__main__":
    main()
