"""
Survey a newly parsed drawing for the conventions the pipeline depends on.

Every project so far names sheets, layers and footing types differently, so
before any extraction runs the file gets a convention report: how sheets are
titled, where structural content sits, which footing labels exist, and whether
the same label appears in more than one context (the chedi's F1 lesson).
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sheets as S

sys.stdout.reconfigure(encoding="utf-8")

DOT_RE = re.compile(r"^[A-Z]{1,2}\d\.\d+$")        # A2.01 (chedi)
HYPHEN_RE = re.compile(r"^[A-Z]{1,2}-\d{1,3}$")    # S-01 (thap kaset index)
LABEL_RE = re.compile(r"^(F|SN)-?\d")
PLAN_KW = ("ผังฐานราก", "แปลนฐานราก", "แบบขยายฐานราก", "รูปตัดฐานราก",
           "ผังโครงสร้าง", "ผังพื้น", "ผังหลังคา")
PILE_KW = ("เสาเข็ม", "PILE")


def anchor_report(name, hits):
    """Anchors sharing one x column are an index table, not title blocks."""
    if not hits:
        return f"  {name}: none"
    xs = sorted({round(p[0]) for ps in hits.values() for p in ps})
    spread = xs[-1] - xs[0]
    kind = "INDEX TABLE (one column — not sheet anchors)" if spread < 400 else "title blocks"
    return f"  {name}: {len(hits)} unique ({kind}), x-spread {spread}"


def main():
    src = Path(sys.argv[1])
    entities = json.loads(src.read_text(encoding="utf-8"))
    blocks_path = src.with_name(src.stem + ".blocks.json")
    blocks = json.loads(blocks_path.read_text(encoding="utf-8")) if blocks_path.exists() else {}

    print(f"=== {src.stem} ===")
    print(f"{len(entities)} entities, {len(blocks)} block definitions")
    layers = Counter(e["layer"] for e in entities)
    print("top layers:", ", ".join(f"{l}({n})" for l, n in layers.most_common(10)))

    # sheet-title conventions
    dot, hyphen = defaultdict(list), defaultdict(list)
    for e in entities:
        if e["type"] != "TEXT":
            continue
        t = e.get("text", "").strip()
        p = (e["insert"][0], e["insert"][1])
        if DOT_RE.match(t):
            dot[t].append(p)
        elif HYPHEN_RE.match(t):
            hyphen[t].append(p)
    print("sheet-number formats:")
    print(anchor_report("dot (A2.01)", dot))
    print(anchor_report("hyphen (A-01)", hyphen))

    # thai plan/detail titles — the fallback anchors when numbers are absent
    print("plan/detail titles:")
    for e in entities:
        if e["type"] in ("TEXT", "MTEXT"):
            c = S.clean_text(e.get("text", ""))
            if any(c.startswith(k) for k in PLAN_KW) and len(c) < 60:
                x, y = e["insert"][0], e["insert"][1]
                print(f"  ({round(x)},{round(y)}) [{e['layer']}] {c}")

    # footing labels and their spatial clusters
    labs = defaultdict(list)
    for e in entities:
        if e["type"] in ("TEXT", "MTEXT"):
            c = S.clean_text(e.get("text", "")).strip()
            if LABEL_RE.match(c) and len(c) < 20:
                labs[c.split()[0].rstrip(",")].append(
                    (round(e["insert"][0]), round(e["insert"][1])))
    print("footing-ish labels:")
    for t in sorted(labs):
        pts = labs[t]
        ys = sorted({p[1] for p in pts})
        # >200 drawing units between clusters = separate packages using one name
        gaps = [b - a for a, b in zip(ys, ys[1:]) if b - a > 200]
        flag = "  <-- MULTIPLE CONTEXTS, verify meaning per package" if gaps else ""
        print(f"  {t} x{len(pts)}  y-range [{ys[0]}..{ys[-1]}]{flag}")

    fblocks = sorted(n for n in blocks if LABEL_RE.match(n))
    print(f"footing-named blocks: {fblocks if fblocks else 'none'}")

    # a pile line item needs pile marks on a plan, not just boilerplate notes —
    # report the mentions so short labels vs long spec text are distinguishable
    mentions = []
    for e in entities:
        if e["type"] in ("TEXT", "MTEXT"):
            c = S.clean_text(e.get("text", ""))
            if any(k in c for k in PILE_KW):
                mentions.append(f"[{e['layer']}] {c[:60]}")
    print(f"pile mentions: {len(mentions)}")
    for m in mentions[:8]:
        print(f"  {m}")


if __name__ == "__main__":
    main()
