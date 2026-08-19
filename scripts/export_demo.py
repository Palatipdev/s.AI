"""
Export the pipeline's results as JSON for the demo page.

The page is static — it replays a real run rather than executing the pipeline in
the browser — so this is what keeps the two honest with each other. Re-run it
after any change to the estimator and the page updates with it.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import count_concrete
import count_piles
import estimate_structural as ES
import eval as evaluation
import schedules
import sheets as S

sys.stdout.reconfigure(encoding="utf-8")

# What a visitor can pick from, in the order they appear in the BOQ.
ITEMS = [
    {
        "id": "piles",
        "sheet": "S2.01",
        "section": "1.1",
        "th": "เสาเข็มหกเหลี่ยมกลวง 0.20 x 0.20 x 6.00 ม.",
        "en": "Precast piles",
        "unit": "no.",
        "method": "Count the 0.20 m squares inside each footing block, multiply by "
                  "how many footings of that type sit on the plan.",
        "source": "geometry",
    },
    {
        "id": "foundation-concrete",
        "sheet": "S2.01",
        "section": "1.1",
        "th": "คอนกรีตโครงสร้าง (ฐานราก)",
        "en": "Structural concrete — foundation",
        "unit": "m3",
        "method": "Pad area by its dimensioned 0.5 m thickness, plus each pedestal "
                  "run up to the ground floor level read off the elevation.",
        "source": "geometry",
    },
    {
        "id": "foundation-formwork",
        "sheet": "S2.01",
        "section": "1.1",
        "th": "ไม้แบบ (ฐานราก)",
        "en": "Formwork — foundation",
        "unit": "m2",
        "method": "The vertical face of every pour: pad edges and pedestal sides.",
        "source": "geometry",
    },
    {
        "id": "sand",
        "sheet": "S2.01",
        "section": "1.1",
        "th": "ทรายหยาบ",
        "en": "Sand blinding",
        "unit": "m3",
        "method": "Footing footprint by the specified bedding depth.",
        "source": "spec",
    },
    {
        "id": "lean-concrete",
        "sheet": "S2.01",
        "section": "1.1",
        "th": "คอนกรีตหยาบ",
        "en": "Lean concrete",
        "unit": "m3",
        "method": "Footing footprint by the specified blinding depth.",
        "source": "spec",
    },
    {
        "id": "l1-concrete",
        "sheet": "S2.02",
        "section": "1.2",
        "th": "คอนกรีตโครงสร้าง (ชั้น 1)",
        "en": "Structural concrete — level 1",
        "unit": "m3",
        "method": "Beams by their scheduled section along each labelled run, columns "
                  "by storey height, and a floor cast on grade over the building outline.",
        "source": "geometry",
    },
    {
        "id": "l2-concrete",
        "sheet": "S2.03",
        "section": "1.3",
        "th": "คอนกรีตโครงสร้าง (ชั้น 2)",
        "en": "Structural concrete — level 2",
        "unit": "m3",
        "method": "Beams, columns and a suspended slab bounded by its framing.",
        "source": "geometry",
    },
    {
        "id": "l3-concrete",
        "sheet": "S2.04",
        "section": "1.4",
        "th": "คอนกรีตโครงสร้าง (ชั้น 3)",
        "en": "Structural concrete — level 3",
        "unit": "m3",
        "method": "Beams, columns and a suspended slab bounded by its framing.",
        "source": "geometry",
    },
    {
        "id": "l2-formwork",
        "sheet": "S2.03",
        "section": "1.3",
        "th": "ไม้แบบ (ชั้น 2)",
        "en": "Formwork — level 2",
        "unit": "m2",
        "method": "Beam sides and soffits, column faces, and the slab soffit.",
        "source": "geometry",
    },
    {
        "id": "l3-formwork",
        "sheet": "S2.04",
        "section": "1.4",
        "th": "ไม้แบบ (ชั้น 3)",
        "en": "Formwork — level 3",
        "unit": "m2",
        "method": "Beam sides and soffits, column faces, and the slab soffit.",
        "source": "geometry",
    },
]

# (section, BOQ item) each demo entry scores against
LOOKUP = {
    "piles": ("1.1", "เสาเข็ม 0.20x0.20x6.00 ม."),
    "foundation-concrete": ("1.1", "คอนกรีตโครงสร้าง"),
    "foundation-formwork": ("1.1", "ไม้แบบ"),
    "sand": ("1.1", "ทรายหยาบ"),
    "lean-concrete": ("1.1", "คอนกรีตหยาบ"),
    "l1-concrete": ("1.2", "คอนกรีตโครงสร้าง"),
    "l2-concrete": ("1.3", "คอนกรีตโครงสร้าง"),
    "l3-concrete": ("1.4", "คอนกรีตโครงสร้าง"),
    "l2-formwork": ("1.3", "ไม้แบบ"),
    "l3-formwork": ("1.4", "ไม้แบบ"),
}

TRUTH = {(s, i): q for s, i, q, _ in evaluation.BOQ}


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks = json.loads(src.with_name(src.stem + ".blocks.json").read_text(encoding="utf-8"))

    computed = evaluation.compute_all(entities, blocks)
    anchors = S.sheet_anchors(entities)

    items = []
    for spec in ITEMS:
        key = LOOKUP[spec["id"]]
        value = computed.get(key)
        truth = TRUTH.get(key)
        if value is None or truth is None:
            continue
        err = abs(value - truth) / truth
        items.append({
            **spec,
            "pipeline": round(value, 1),
            "boq": truth,
            "error": round(err * 100, 1),
            "pass": err <= evaluation.ACCURACY_TARGET,
            "calibrated": key in evaluation.CALIBRATED,
        })

    scored = [i for i in items if not i["calibrated"]]
    payload = {
        # the client and project are withheld from anything published
        "project": "religious building, structural chapter",
        "entities": len(entities),
        "blocks": len(blocks),
        "sheets": len(anchors),
        "passed": sum(1 for i in scored if i["pass"]),
        "scored": len(scored),
        "items": items,
    }

    out = Path(__file__).parent.parent / "data" / "parsed" / "demo.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(items)} items -> {out}")
    print(f"{payload['passed']}/{payload['scored']} within ±10%")


if __name__ == "__main__":
    main()
