"""Shared helpers: sheet regions, text cleaning, geometry."""
import re

# Sheets are laid out on a regular grid in modelspace. A title-block label sits at
# the bottom-right of its sheet; the drawing occupies the space up and to the left.
SHEET_W = 44.5
SHEET_H = 31.0

TITLE_RE = re.compile(r"^[A-Z]{1,2}\d\.\d")
MTEXT_FMT = re.compile(r"\\[A-Za-z][^;]*;|[{}]")


def clean_text(t):
    """Strip MTEXT formatting codes (\\A1;, {\\fCordia New|...;X}) down to plain text."""
    return MTEXT_FMT.sub("", t or "").strip()


def sheet_anchors(entities):
    """{drawing_number: (x, y)} for every title-block label, first occurrence wins."""
    out = {}
    for e in entities:
        if e["type"] == "TEXT" and TITLE_RE.match(e.get("text", "")):
            out.setdefault(e["text"], (e["insert"][0], e["insert"][1]))
    return out


def position(e):
    """A representative (x, y) for any entity type."""
    for k in ("insert", "start", "center"):
        if k in e:
            return e[k][0], e[k][1]
    if e.get("points"):
        return e["points"][0][0], e["points"][0][1]
    if e.get("paths"):
        return e["paths"][0][0][0], e["paths"][0][0][1]
    return None


def in_sheet(pos, anchor, w=SHEET_W, h=SHEET_H):
    """Is this point inside the sheet whose title block sits at `anchor`?"""
    if pos is None:
        return False
    x0, y0 = anchor
    return (x0 - w <= pos[0] <= x0 + 1.0) and (y0 - 1.5 <= pos[1] <= y0 + h)


def frame_size(anchors, sheet, default_w=SHEET_W, default_h=SHEET_H):
    """
    Frame width for a sheet, from the spacing to its neighbour on the same row.

    Sheets are laid out on a grid, but the pitch differs by series: full plans
    sit ~44.5 apart while detail sheets are packed ~8.9 apart. A fixed width
    would let a big frame swallow its neighbours' content.
    """
    if sheet not in anchors:
        return default_w, default_h
    x0, y0 = anchors[sheet]
    same_row = [
        v[0] for k, v in anchors.items()
        if k != sheet and abs(v[1] - y0) < 1.0 and v[0] < x0
    ]
    if not same_row:
        return default_w, default_h
    gap = x0 - max(same_row)
    return (gap if 1.0 < gap < default_w else default_w), default_h


def entities_on_sheet(entities, anchors, sheet, adaptive=True):
    """
    Every entity falling inside the given sheet's frame.

    `adaptive` sizes the frame from neighbouring sheets so tightly-packed detail
    sheets don't swallow each other. Pass False for a full-size frame.
    """
    if sheet not in anchors:
        return []
    a = anchors[sheet]
    w, h = frame_size(anchors, sheet) if adaptive else (SHEET_W, SHEET_H)
    return [e for e in entities if in_sheet(position(e), a, w, h)]


def entities_near(entities, anchors, sheets):
    """
    Entities belonging to any of a group of sheets, deduplicated.

    Schedules for one element type can be split across several adjacent detail
    sheets, so reading them means treating the group as one region.
    """
    seen = set()
    out = []
    for sh in sheets:
        for e in entities_on_sheet(entities, anchors, sh):
            key = e.get("handle") or id(e)
            if key not in seen:
                seen.add(key)
                out.append(e)
    return out


def polygon_area(points):
    """Shoelace — handles L-shapes and any simple polygon."""
    a = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


def bbox_size(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return max(xs) - min(xs), max(ys) - min(ys)
