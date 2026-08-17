"""
Score the pipeline's output against the real bill of quantities.

Ground truth is the firm's finished BOQ for this project, chapter 1 (งานโครงสร้าง),
transcribed by hand. Nothing here is derived from the pipeline.

Each line is scored against the ±10% band the firm's head engineer named as the
threshold at which a quantity is useful as an independent check on a purchase order.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import count_concrete
import count_piles
import estimate_structural as ES
import schedules
import sheets as S

sys.stdout.reconfigure(encoding="utf-8")

ACCURACY_TARGET = 0.10  # ±10% per line item (head engineer, 2026-07-31)

# (section, description, quantity, unit)
BOQ = [
    ("1.1", "เสาเข็ม 0.20x0.20x6.00 ม.", 66, "ต้น"),
    ("1.1", "คอนกรีตโครงสร้าง", 53, "ลบ.ม."),
    ("1.1", "ไม้แบบ", 296, "ตร.ม."),
    ("1.2", "คอนกรีตโครงสร้าง", 153, "ลบ.ม."),
    ("1.2", "ไม้แบบ", 1392, "ตร.ม."),
    ("1.3", "คอนกรีตโครงสร้าง", 143, "ลบ.ม."),
    ("1.3", "ไม้แบบ", 1356, "ตร.ม."),
    ("1.4", "คอนกรีตโครงสร้าง", 68, "ลบ.ม."),
    ("1.4", "ไม้แบบ", 645, "ตร.ม."),
]

# Rows with no geometric basis, and why. Reported, never guessed.
OUT_OF_SCOPE = [
    ("rebar RB/DB (kg)", "needs bar-bending schedules; 79-192 kg/m3 varies by role"),
    ("ขุดดิน (excavation)", "site-wide strip, not per-footing pits"),
    ("1.5 องค์เจดีย์", "spire is drawn as details, not a framing plan"),
]


def compute_all(entities, blocks):
    """{(section, item): quantity} for every line the pipeline can produce."""
    anchors = S.sheet_anchors(entities)
    beam_sec, col_sec = schedules.all_schedules(entities, anchors)

    piles, _, _ = count_piles.compute(entities, blocks)
    concrete, _, _, _ = count_concrete.compute(entities, blocks)
    out = {
        ("1.1", "เสาเข็ม 0.20x0.20x6.00 ม."): piles,
        ("1.1", "คอนกรีตโครงสร้าง"): concrete,
    }

    typical_bay = ES.project_bay_span(entities, anchors, ES.FRAMING.values())
    heights = ES.storey_heights(ES.floor_levels(entities), len(ES.FRAMING))

    for i, (section, sheet) in enumerate(ES.FRAMING.items()):
        if sheet not in anchors:
            continue
        beams = ES.element_labels(entities, anchors, sheet, "B")
        cols = ES.element_labels(entities, anchors, sheet, "C")
        slabs = ES.element_labels(entities, anchors, sheet, "S")
        span = ES.bay_span(entities, anchors, sheet, fallback=typical_bay)
        height = heights[i] if i < len(heights) else ES.STOREY_HEIGHT

        bv, bf, _ = ES.estimate_beams(beams, beam_sec, span)
        cv, cf, _ = ES.estimate_columns(cols, col_sec, height)
        sv, sf, _ = ES.estimate_slabs(
            slabs, bound=ES.plan_extent(beams) if beams else None
        )
        out[(section, "คอนกรีตโครงสร้าง")] = bv + cv + sv
        out[(section, "ไม้แบบ")] = bf + cf + sf

    return out


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks = json.loads(src.with_name(src.stem + ".blocks.json").read_text(encoding="utf-8"))
    computed = compute_all(entities, blocks)

    print("=" * 78)
    print("PIPELINE vs BILL OF QUANTITIES — chapter 1, งานโครงสร้าง")
    print("=" * 78)
    print(f"\n{'sec':5}{'item':28}{'BOQ':>9}{'pipeline':>10}{'error':>8}  status")
    print("-" * 78)

    passed = scored = 0
    for section, item, truth, unit in BOQ:
        actual = computed.get((section, item))
        if actual is None:
            print(f"{section:5}{item[:27]:28}{truth:>9}{'—':>10}{'—':>8}  not produced")
            continue
        err = abs(actual - truth) / truth
        scored += 1
        ok = err <= ACCURACY_TARGET
        passed += ok
        print(f"{section:5}{item[:27]:28}{truth:>9}{actual:>10.1f}{err:>7.0%}  "
              f"{'PASS' if ok else 'FLAG'}")

    print("-" * 78)
    print(f"{passed}/{scored} line items within ±{ACCURACY_TARGET:.0%}")

    print("\nout of scope — reported, not guessed:")
    for item, why in OUT_OF_SCOPE:
        print(f"  {item:22} {why}")


if __name__ == "__main__":
    main()
