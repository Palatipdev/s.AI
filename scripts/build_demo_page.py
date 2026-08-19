"""
Build the shareable demo page: pick a material, compute it, see it scored.

The page is static. It replays results exported by export_demo.py rather than
running the pipeline in a browser, so the numbers are the real ones from the
last run and there is no backend to keep alive.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(__file__).parent.parent / "data" / "parsed"
data = json.loads((SRC / "demo.json").read_text(encoding="utf-8"))
plan_svg = (SRC / "plan.svg").read_text(encoding="utf-8")
viewer_b64 = (SRC / "viewer_crop.b64").read_text()

HEAD = """<title>Reading quantities out of a CAD drawing</title>
<style>
  :root{
    --paper:#F7F5F0; --ink:#0F1416; --soft:#5A6467; --rule:#D8D4CB;
    --accent:#B4472A; --pass:#1F6F5C; --flag:#A8761E;
    --panel:#FFFFFF; --well:#EFEDE7;
  }
  @media (prefers-color-scheme:dark){
    :root{ --paper:#0E1213; --ink:#ECE9E3; --soft:#8E9A9D; --rule:#242B2D;
           --accent:#E0705A; --pass:#4FBFA0; --flag:#D5A445;
           --panel:#151A1C; --well:#0B0F10; }
  }
  :root[data-theme=dark]{ --paper:#0E1213; --ink:#ECE9E3; --soft:#8E9A9D; --rule:#242B2D;
    --accent:#E0705A; --pass:#4FBFA0; --flag:#D5A445; --panel:#151A1C; --well:#0B0F10; }
  :root[data-theme=light]{ --paper:#F7F5F0; --ink:#0F1416; --soft:#5A6467; --rule:#D8D4CB;
    --accent:#B4472A; --pass:#1F6F5C; --flag:#A8761E; --panel:#FFFFFF; --well:#EFEDE7; }

  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{ margin:0; background:var(--paper); color:var(--ink); line-height:1.55;
    font-family:ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif;
    font-variant-numeric:tabular-nums; }
  .mono{ font-family:ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,monospace }
  .wrap{ max-width:1080px; margin:0 auto; padding:clamp(20px,4vw,54px) clamp(16px,4vw,32px) }

  .eyebrow{ font-size:11px; letter-spacing:.15em; text-transform:uppercase; color:var(--soft) }
  h1{ font-size:clamp(28px,4.6vw,48px); line-height:1.08; letter-spacing:-.025em;
      margin:14px 0 0; font-weight:650; text-wrap:balance; max-width:19ch }
  .lede{ font-size:clamp(15px,1.6vw,17.5px); color:var(--soft); margin:18px 0 0; max-width:62ch }
  .lede strong{ color:var(--ink); font-weight:600 }

  .stats{ display:flex; flex-wrap:wrap; gap:0; margin:34px 0 0;
          border-top:1px solid var(--rule); border-bottom:1px solid var(--rule) }
  .stat{ flex:1 1 150px; padding:16px 20px 16px 0 }
  .stat b{ display:block; font-size:clamp(22px,3vw,30px); font-weight:650; letter-spacing:-.02em }
  .stat span{ font-size:12px; color:var(--soft) }

  h2{ font-size:clamp(19px,2.2vw,24px); letter-spacing:-.015em; margin:0; font-weight:620 }
  .section{ margin-top:clamp(46px,6vw,76px) }
  .note{ color:var(--soft); font-size:14.5px; margin:10px 0 0; max-width:62ch }

  /* --- the interactive strip --- */
  .demo{ margin-top:26px; border:1px solid var(--rule); background:var(--panel) }
  .bar{ display:flex; flex-wrap:wrap; gap:14px; align-items:flex-end;
        padding:20px clamp(16px,2.4vw,26px); border-bottom:1px solid var(--rule) }
  .field{ flex:1 1 300px; min-width:0 }
  .field label{ display:block; font-size:11px; letter-spacing:.12em;
                text-transform:uppercase; color:var(--soft); margin-bottom:7px }
  select{ width:100%; padding:11px 12px; background:var(--well); color:var(--ink);
    border:1px solid var(--rule); border-radius:0; font:inherit; font-size:14.5px;
    font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace; }
  select:focus-visible{ outline:2px solid var(--accent); outline-offset:1px }
  button{ padding:11px 22px; background:var(--ink); color:var(--paper); border:0;
    font:inherit; font-size:14.5px; font-weight:600; cursor:pointer; letter-spacing:.01em }
  button:hover{ background:var(--accent) }
  button:focus-visible{ outline:2px solid var(--accent); outline-offset:2px }
  button[disabled]{ opacity:.55; cursor:default }

  .stage{ display:grid; grid-template-columns:1fr 1fr }
  @media (max-width:800px){ .stage{ grid-template-columns:1fr } }
  .pane{ padding:clamp(16px,2.4vw,26px); min-width:0 }
  .pane + .pane{ border-left:1px solid var(--rule) }
  @media (max-width:800px){ .pane + .pane{ border-left:0; border-top:1px solid var(--rule) } }
  .panehead{ font-size:11px; letter-spacing:.12em; text-transform:uppercase;
             color:var(--soft); margin-bottom:12px }
  .well{ background:var(--well); border:1px solid var(--rule); padding:10px }
  .well img,.well svg{ display:block; width:100%; height:auto }
  .plan .o{ fill:none; stroke:var(--ink); stroke-width:1.4; vector-effect:non-scaling-stroke }
  .plan .p{ fill:var(--accent); stroke:var(--accent); stroke-width:1; vector-effect:non-scaling-stroke }
  .method{ font-size:13.5px; color:var(--soft); margin:13px 0 0 }

  .idle{ color:var(--soft); font-size:14px; padding:26px 0; text-align:center }
  .result{ display:none }
  .result.on{ display:block }
  .big{ font-size:clamp(38px,6.5vw,60px); font-weight:650; letter-spacing:-.03em; line-height:1 }
  .unit{ font-size:15px; color:var(--soft); font-weight:400; margin-left:8px }
  .cmp{ margin-top:20px; border-top:1px solid var(--rule) }
  .cmp div{ display:flex; justify-content:space-between; gap:16px;
            padding:11px 0; border-bottom:1px solid var(--rule); font-size:14px }
  .cmp span:first-child{ color:var(--soft) }
  .verdict{ margin-top:18px; padding:12px 14px; font-size:13.5px; border:1px solid }
  .verdict.ok{ color:var(--pass); border-color:var(--pass) }
  .verdict.no{ color:var(--flag); border-color:var(--flag) }

  table{ width:100%; border-collapse:collapse; margin-top:20px; font-size:14px }
  th{ text-align:left; font-size:11px; letter-spacing:.1em; text-transform:uppercase;
      color:var(--soft); font-weight:500; padding:0 10px 9px 0; border-bottom:1px solid var(--rule) }
  th:not(:first-child),td:not(:first-child){ text-align:right }
  td{ padding:11px 10px 11px 0; border-bottom:1px solid var(--rule) }
  .tag{ font-size:11px; letter-spacing:.05em; text-transform:uppercase }
  .tag.ok{ color:var(--pass) } .tag.no{ color:var(--flag) }
  .src{ font-size:12px; color:var(--soft); opacity:.75 }
  .scroll{ overflow-x:auto }

  .cols{ display:grid; grid-template-columns:1fr 1fr; gap:clamp(20px,3vw,38px); margin-top:22px }
  @media (max-width:760px){ .cols{ grid-template-columns:1fr } }
  .cols h3{ font-size:15px; margin:0 0 8px; font-weight:600 }
  .cols p{ margin:0; font-size:14px; color:var(--soft) }
  .cols li{ font-size:14px; color:var(--soft); margin-bottom:7px }
  ul{ padding-left:18px; margin:0 }

  footer{ margin-top:clamp(46px,6vw,76px); padding-top:22px; border-top:1px solid var(--rule);
          font-size:13.5px; color:var(--soft); display:flex; flex-wrap:wrap; gap:18px;
          justify-content:space-between }
  a{ color:var(--ink); text-decoration:underline; text-underline-offset:3px;
     text-decoration-color:var(--rule) }
  a:hover{ text-decoration-color:var(--accent) }
  @media (prefers-reduced-motion:reduce){ *{ transition:none !important } }
</style>"""


def build_options(items):
    rows = []
    for i in items:
        rows.append(
            f'<option value="{i["id"]}">{i["en"]} &mdash; BOQ {i["section"]}</option>'
        )
    return "\n        ".join(rows)


def build_table(items):
    rows = []
    for i in items:
        cls = "ok" if i["pass"] else "no"
        label = "pass" if i["pass"] else "flag"
        if i["calibrated"]:
            label = "pass*"
        rows.append(
            f'<tr><td>{i["en"]}<br>'
            f'<span class="src" title="as written in the bill of quantities">{i["th"]}</span></td>'
            f'<td class="mono">{i["boq"]} {i["unit"]}</td>'
            f'<td class="mono">{i["pipeline"]}</td>'
            f'<td class="mono">{i["error"]}%</td>'
            f'<td class="tag {cls}">{label}</td></tr>'
        )
    return "\n          ".join(rows)


BODY = """<div class="wrap">

  <div class="eyebrow mono">Applied extraction &mdash; CAD to bill of quantities</div>
  <h1>Reading construction quantities out of a drawing.</h1>
  <p class="lede">A bill of quantities lists every material a building needs, and an engineer
  spends weeks producing one by hand from CAD drawings. Almost none of those numbers are written
  in the drawing &mdash; they are counted, measured and computed from it. This pipeline does that
  automatically, then <strong>scores itself against the bill of quantities the engineers actually
  produced</strong> for the same project.</p>

  <div class="stats mono">
    <div class="stat"><b>__PASSED__/__SCORED__</b><span>line items within &plusmn;10%</span></div>
    <div class="stat"><b>__ENTITIES__</b><span>CAD entities parsed</span></div>
    <div class="stat"><b>__SHEETS__</b><span>drawing sheets</span></div>
    <div class="stat"><b>0%</b><span>error on pile count</span></div>
  </div>

  <div class="section">
    <h2>Try it</h2>
    <p class="note">Pick a material and compute it. Each figure below is a real result from the
    pipeline, checked against the same line in the firm's finished bill of quantities.</p>

    <div class="demo">
      <div class="bar">
        <div class="field">
          <label for="pick">Material</label>
          <select id="pick">
        __OPTIONS__
          </select>
        </div>
        <button id="go">Compute quantity</button>
      </div>

      <div class="stage">
        <div class="pane">
          <div class="panehead mono">What the pipeline reads</div>
          <div class="well" id="art">__PLAN__</div>
          <p class="method" id="method">Footing plan S2.01, extracted from the drawing.
          Pile marks in red are the 0.20&nbsp;m squares counted inside each footing block.</p>
        </div>

        <div class="pane">
          <div class="panehead mono">Result</div>
          <div class="idle" id="idle">Choose a material and press compute.</div>
          <div class="result" id="out">
            <div><span class="big mono" id="value">0</span><span class="unit mono" id="unit"></span></div>
            <div class="cmp mono">
              <div><span>Pipeline</span><span id="r-pipe"></span></div>
              <div><span>Bill of quantities</span><span id="r-boq"></span></div>
              <div><span>Difference</span><span id="r-err"></span></div>
            </div>
            <div class="verdict" id="verdict"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Every line, scored</h2>
    <p class="note">The full scorecard. Nothing is hidden: the lines that miss are shown with
    the same weight as the ones that land. Each row carries the item as it appears in the original
    Thai document underneath the translation.</p>
    <div class="scroll">
      <table>
        <thead><tr><th>Item</th><th>BOQ</th><th>Pipeline</th><th>Error</th><th></th></tr></thead>
        <tbody>
          __TABLE__
        </tbody>
      </table>
    </div>
    <p class="note" style="margin-top:14px">* Sand and lean concrete use bedding depths calibrated
    on this bill of quantities rather than read from the drawing. They show the calculation works;
    they are not evidence it generalises, so they sit outside the headline score.</p>
  </div>

  <div class="section">
    <h2>How a quantity gets built</h2>
    <div class="cols">
      <div>
        <h3>The number is never in the drawing</h3>
        <p>&ldquo;66 piles&rdquo; appears nowhere. Footings are placed as CAD blocks, and each block
        definition holds its pile marks as 0.20&nbsp;m squares &mdash; the size named in the BOQ line
        itself. Counting squares per footing type and placements per sheet gives the total. Finding
        that the answer lived inside the block definitions, not the visible drawing, was the
        breakthrough the rest is built on.</p>
      </div>
      <div>
        <h3>Cross-referencing sheets</h3>
        <p>A drawing set splits the answer across sheets: schedules give element sizes, plans give
        their locations, and the elevation gives floor levels. A beam's volume needs its section from
        one sheet, its run length from another, and the storey height from a third. The pipeline
        reads all fifteen sheets and joins them.</p>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>What it does not do</h2>
    <div class="cols">
      <div>
        <ul>
          <li><strong>Reinforcement.</strong> Bar weights need bending schedules the drawing does not
          carry, and they vary from 79 to 192&nbsp;kg per m&sup3; by structural role &mdash; no
          constant would be honest.</li>
          <li><strong>Excavation.</strong> A site-wide strip, not the per-footing pits the geometry
          describes.</li>
        </ul>
      </div>
      <div>
        <ul>
          <li><strong>The spire.</strong> Drawn as details rather than a framing plan, so the method
          the other sections use does not apply.</li>
          <li><strong>Formwork</strong> currently reads 15&ndash;17% low across every section. The
          consistency points at one unmodelled surface rather than scattered error.</li>
        </ul>
      </div>
    </div>
    <p class="note" style="margin-top:18px">Each of these is reported as out of scope with its reason,
    never filled in with a plausible-looking guess. A quantity a reviewer cannot trust costs more to
    check than to redo &mdash; which is the whole point of scoring every line against ground truth.</p>
  </div>

  <footer>
    <span>Drawings and quantities used with the firm's permission; project details withheld.</span>
    <span><a href="https://github.com/Palatipdev/s.AI">Source on GitHub</a></span>
  </footer>
</div>

<script>
  const DATA = __DATA__;
  const byId = Object.fromEntries(DATA.items.map(i => [i.id, i]));
  const pick = document.getElementById('pick');
  const go = document.getElementById('go');
  const out = document.getElementById('out');
  const idle = document.getElementById('idle');
  const method = document.getElementById('method');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const fmt = n => Number.isInteger(n) ? n.toString() : n.toFixed(1);

  function show(item) {
    document.getElementById('unit').textContent = item.unit;
    document.getElementById('r-pipe').textContent = fmt(item.pipeline) + ' ' + item.unit;
    document.getElementById('r-boq').textContent = item.boq + ' ' + item.unit;
    document.getElementById('r-err').textContent = item.error + '%';

    const v = document.getElementById('verdict');
    v.className = 'verdict ' + (item.pass ? 'ok' : 'no');
    v.textContent = item.pass
      ? 'Within the ±10% band the firm\\'s head engineer named as useful — close enough for purchasing to check an order against.'
      : 'Outside ±10%. Reported as a flagged line rather than presented as reliable.';

    idle.style.display = 'none';
    out.classList.add('on');

    const target = item.pipeline;
    const el = document.getElementById('value');
    if (reduce) { el.textContent = fmt(target); return; }
    const start = performance.now(), dur = 620;
    function step(now) {
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = fmt(Math.round(target * eased * 10) / 10);
      if (t < 1) requestAnimationFrame(step);
      else el.textContent = fmt(target);
    }
    requestAnimationFrame(step);
  }

  function reset() {
    out.classList.remove('on');
    idle.style.display = '';
    const item = byId[pick.value];
    if (item) method.textContent = item.method;
  }

  pick.addEventListener('change', reset);
  go.addEventListener('click', () => show(byId[pick.value]));
  reset();
</script>"""


DESCRIPTION = (
    "A pipeline that reads construction quantities out of CAD drawings and scores "
    "itself against the bill of quantities engineers produced by hand."
)

# Artifacts supply their own document shell, so publishing there wants a fragment.
# A standalone page needs the whole document.
DOCUMENT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<meta property="og:title" content="Reading quantities out of a CAD drawing">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='14' font-size='14'>&#128207;</text></svg>">
{head}
</head>
<body>
{body}
</body>
</html>
"""


def main():
    body = (BODY
            .replace("__PASSED__", str(data["passed"]))
            .replace("__SCORED__", str(data["scored"]))
            .replace("__ENTITIES__", f"{data['entities']:,}")
            .replace("__SHEETS__", str(data["sheets"]))
            .replace("__OPTIONS__", build_options(data["items"]))
            .replace("__TABLE__", build_table(data["items"]))
            .replace("__PLAN__", plan_svg)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))

    out = Path(sys.argv[1])
    standalone = "--fragment" not in sys.argv[2:]
    page = (DOCUMENT.format(description=DESCRIPTION, head=HEAD, body=body)
            if standalone else HEAD + body)
    out.write_text(page, encoding="utf-8")
    kind = "standalone page" if standalone else "artifact fragment"
    print(f"{len(page) // 1024} KB {kind} -> {out}")


if __name__ == "__main__":
    main()
