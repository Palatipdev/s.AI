"""
Build the demo page from the exported run.

Nothing here computes a quantity. It reads data/parsed/demo.json and
data/parsed/sheets.json and lays them out, so the page can only ever show what
the pipeline actually produced.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "parsed"
REPO = "https://github.com/palatipdev/s.AI"

SHEET_LABEL = {
    "S2.01": "S2.01 — footing plan",
    "S2.02": "S2.02 — level 1 framing",
    "S2.03": "S2.03 — level 2 framing",
    "S2.04": "S2.04 — level 3 framing",
}

CSS = """
:root{
  --bg:#000; --panel:#0B0B0C; --line:#1E1F22; --ink:#F2F2F0; --mut:#76787D;
  --acc:#FF4D2E; --pass:#4ADE80; --flag:#FBBF24;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased;
  padding:0 24px 96px}
.wrap{max-width:880px;margin:0 auto}

header{display:flex;justify-content:space-between;align-items:baseline;
  padding:40px 0 0;gap:24px}
.mark{font-family:var(--mono);font-size:15px;letter-spacing:-.02em}
.mark b{color:var(--acc);font-weight:600}
header a{font-family:var(--mono);font-size:12px;color:var(--mut);
  text-decoration:none;border-bottom:1px solid var(--line);padding-bottom:2px}
header a:hover{color:var(--ink);border-color:var(--acc)}

h1{font-size:clamp(26px,4.4vw,40px);line-height:1.15;font-weight:500;
  letter-spacing:-.03em;margin:56px 0 14px;max-width:19ch}
.sub{color:var(--mut);max-width:56ch}
.sub strong{color:var(--ink);font-weight:500}

.demo{border:1px solid var(--line);background:var(--panel);margin:40px 0 0}
.bar{display:flex;gap:10px;padding:14px;border-bottom:1px solid var(--line);
  flex-wrap:wrap}
select,button{font-family:var(--mono);font-size:13px;border:1px solid var(--line);
  border-radius:0;padding:11px 13px;background:#000;color:var(--ink);
  appearance:none;cursor:pointer}
select{flex:1;min-width:210px;
  background-image:linear-gradient(45deg,transparent 50%,var(--mut) 50%),
    linear-gradient(135deg,var(--mut) 50%,transparent 50%);
  background-position:calc(100% - 17px) 50%,calc(100% - 12px) 50%;
  background-size:5px 5px,5px 5px;background-repeat:no-repeat;padding-right:34px}
select:focus,button:focus{outline:1px solid var(--acc);outline-offset:-1px}
button{background:var(--acc);border-color:var(--acc);color:#000;font-weight:600;
  letter-spacing:.02em;padding-left:22px;padding-right:22px}
button:hover{background:#ff6647;border-color:#ff6647}

.out{display:grid;grid-template-columns:1fr 1fr 1fr;
  border-bottom:1px solid var(--line)}
.cell{padding:22px 18px;border-right:1px solid var(--line)}
.cell:last-child{border-right:0}
.k{font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--mut);margin-bottom:9px}
.v{font-family:var(--mono);font-size:clamp(24px,4.6vw,34px);letter-spacing:-.02em;
  line-height:1;font-variant-numeric:tabular-nums}
.u{font-family:var(--mono);font-size:11px;color:var(--mut);margin-left:5px}
.v.ok{color:var(--pass)} .v.no{color:var(--flag)}
.tag{font-family:var(--mono);font-size:10.5px;margin-top:9px;color:var(--mut)}

figure{background:#000;padding:20px 18px 14px;border-bottom:1px solid var(--line)}
figure svg{display:block;width:100%;height:auto;max-height:320px}
svg .line{fill:none;stroke:#3B3E44;stroke-width:.9}
svg .pile{fill:rgba(255,77,46,.28);stroke:var(--acc);stroke-width:1.1}
svg .beam{fill:none;stroke:#5FA8FF;stroke-width:1.3}
svg .col{fill:rgba(255,77,46,.22);stroke:var(--acc);stroke-width:1.2}
svg .slab{fill:none;stroke:#3B3E44;stroke-width:.9}
figcaption{font-family:var(--mono);font-size:11px;color:var(--mut);padding-top:12px}
.method{padding:16px 18px;font-size:13.5px;color:var(--mut);max-width:74ch}
.idle{font-family:var(--mono);font-size:12.5px;color:var(--mut);padding:44px 18px;
  text-align:center}
.hide{display:none}

h2{font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--mut);font-weight:400;margin:64px 0 14px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{font-family:var(--mono);font-size:10px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--mut);font-weight:400;text-align:right;
  padding:0 0 10px;border-bottom:1px solid var(--line)}
th:first-child{text-align:left}
tbody tr{cursor:pointer}
tbody tr:hover td{color:var(--ink)}
td{padding:11px 0;border-bottom:1px solid var(--line);text-align:right;
  font-family:var(--mono);font-variant-numeric:tabular-nums}
td:first-child{text-align:left;font-family:var(--sans)}
tr.sel td{color:var(--acc)}
td .ok{color:var(--pass)} td .no{color:var(--flag)}

footer{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);
  display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;
  font-family:var(--mono);font-size:11.5px;color:var(--mut)}

@media(max-width:620px){
  .out{grid-template-columns:1fr 1fr}
  .cell:nth-child(2){border-right:0}
  .cell:nth-child(3){grid-column:1/-1;border-top:1px solid var(--line)}
  table td:nth-child(2),table th:nth-child(2){display:none}
}
"""

JS = """
const D = %(data)s, SHEETS = %(sheets)s, LABELS = %(labels)s;
const $ = s => document.querySelector(s);
const sel = $('#pick'), idle = $('#idle'), res = $('#res');
const rows = [...document.querySelectorAll('tbody tr')];

D.items.forEach((it, i) => sel.add(new Option(it.en + '  \\u00b7  ' + it.unit, i)));

function count(el, to, dp){
  if (matchMedia('(prefers-reduced-motion: reduce)').matches){
    el.textContent = to.toFixed(dp);
    return;
  }
  const t0 = performance.now(), ms = 460;
  requestAnimationFrame(function step(t){
    const p = Math.min((t - t0) / ms, 1);
    el.textContent = (to * (1 - Math.pow(1 - p, 3))).toFixed(dp);
    if (p < 1) requestAnimationFrame(step);
  });
}

function show(){
  const it = D.items[sel.value], dp = it.unit === 'no.' ? 0 : 1;
  idle.classList.add('hide');
  res.classList.remove('hide');

  count($('#pv'), it.pipeline, dp);
  count($('#bv'), it.boq, dp);
  $('#pu').textContent = $('#bu').textContent = it.unit;

  const ev = $('#ev');
  ev.className = 'v ' + (it.pass ? 'ok' : 'no');
  count(ev, it.error, 1);
  $('#et').textContent = (it.pass ? 'within' : 'outside') + ' the \\u00b110%% target';
  $('#src').textContent = it.source === 'spec'
    ? 'depth from the specification'
    : 'measured from geometry';

  $('#fig').innerHTML = SHEETS[it.sheet] || '';
  $('#cap').textContent = LABELS[it.sheet] + '  \\u2014  what the pipeline read';
  $('#how').textContent = it.method;
  rows.forEach((tr, i) => tr.classList.toggle('sel', i === +sel.value));
}

$('#go').addEventListener('click', show);
sel.addEventListener('change', () => {
  idle.classList.remove('hide');
  res.classList.add('hide');
  rows.forEach(tr => tr.classList.remove('sel'));
});
rows.forEach((tr, i) => tr.addEventListener('click', () => {
  sel.value = i;
  show();
}));
"""

BODY = """
<div class="wrap">
<header>
  <div class="mark"><b>s</b>.AI</div>
  <a href="%(repo)s">source &#8599;</a>
</header>

<h1>Construction quantities, read straight out of CAD drawings.</h1>
<p class="sub">A bill of quantities takes an engineer weeks by hand. This reads the
drawing file and computes the same numbers, then scores itself against the one a real
firm produced. <strong>%(passed)s of %(scored)s line items land within &#177;10%%.</strong></p>

<section class="demo">
  <div class="bar">
    <select id="pick" aria-label="Material"></select>
    <button id="go">Compute</button>
  </div>

  <div id="idle" class="idle">pick a material, then compute</div>

  <div id="res" class="hide">
    <div class="out">
      <div class="cell"><div class="k">Pipeline</div>
        <div><span class="v" id="pv">0</span><span class="u" id="pu"></span></div>
        <div class="tag" id="src"></div></div>
      <div class="cell"><div class="k">Engineer&#8217;s BOQ</div>
        <div><span class="v" id="bv">0</span><span class="u" id="bu"></span></div>
        <div class="tag">ground truth</div></div>
      <div class="cell"><div class="k">Error</div>
        <div><span class="v" id="ev">0</span><span class="u">%%</span></div>
        <div class="tag" id="et"></div></div>
    </div>
    <figure><div id="fig"></div><figcaption id="cap"></figcaption></figure>
    <p class="method" id="how"></p>
  </div>
</section>

<h2>Every line, scored</h2>
<table>
  <thead><tr><th>Item</th><th>Sheet</th><th>Pipeline</th><th>BOQ</th><th>Error</th></tr></thead>
  <tbody>%(rows)s</tbody>
</table>

<footer>
  <span>%(entities)s entities &#183; %(blocks)s block definitions &#183; %(sheets)s sheets</span>
  <span>reinforcement, excavation and the spire are reported out of scope, not guessed</span>
</footer>
</div>
"""

DOC = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>s.AI &#8212; CAD to bill of quantities</title>
<meta name="description" content="Reads a CAD drawing and computes construction quantities, scored against the bill of quantities a real engineering firm produced.">
<style>%(css)s</style>
</head><body>%(body)s<script>%(js)s</script></body></html>
"""


def table_rows(items):
    out = []
    for it in items:
        cls = "ok" if it["pass"] else "no"
        dp = 0 if it["unit"] == "no." else 1
        out.append(
            f'<tr><td>{it["en"]}</td><td>{it["sheet"]}</td>'
            f'<td>{it["pipeline"]:.{dp}f}</td><td>{it["boq"]:.{dp}f}</td>'
            f'<td><span class="{cls}">{it["error"]:.1f}%</span></td></tr>'
        )
    return "".join(out)


def main():
    data = json.loads((DATA / "demo.json").read_text(encoding="utf-8"))
    drawings = json.loads((DATA / "sheets.json").read_text(encoding="utf-8"))

    # the page reads in English; the Thai BOQ wording stays in the repo's data
    for item in data["items"]:
        item.pop("th", None)

    body = BODY % {
        "repo": REPO,
        "passed": data["passed"],
        "scored": data["scored"],
        "rows": table_rows(data["items"]),
        "entities": f'{data["entities"]:,}',
        "blocks": data["blocks"],
        "sheets": data["sheets"],
    }
    js = JS % {
        "data": json.dumps(data, ensure_ascii=False),
        "sheets": json.dumps(drawings, ensure_ascii=False),
        "labels": json.dumps(SHEET_LABEL, ensure_ascii=False),
    }

    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "index.html"
    if "--fragment" in sys.argv:
        page = f"<style>{CSS}</style>{body}<script>{js}</script>"
    else:
        page = DOC % {"css": CSS, "body": body, "js": js}
    dest.write_text(page, encoding="utf-8")
    print(f"{len(page) // 1024} KB -> {dest}")


if __name__ == "__main__":
    main()
