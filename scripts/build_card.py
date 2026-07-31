"""Build the shareable takeoff result card (source drawing -> extraction -> BOQ check)."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(__file__).parent.parent / "data" / "parsed"
svg = (SRC / "plan.svg").read_text(encoding="utf-8")
viewer = (SRC / "viewer_crop.b64").read_text()
boq = (SRC / "boq_crop.b64").read_text()

HEAD = """<title>Foundation takeoff - pipeline vs. bill of quantities</title>
<style>
  :root{
    --paper:#F7F5F0; --ink:#0F1416; --ink-soft:#5A6467; --rule:#D8D4CB;
    --pile:#B4472A; --pass:#1F6F5C; --partial:#A8761E; --panel:#FFFFFF; --well:#EFEDE7;
  }
  @media (prefers-color-scheme:dark){
    :root{ --paper:#0E1213; --ink:#ECE9E3; --ink-soft:#8E9A9D; --rule:#242B2D;
           --pile:#E0705A; --pass:#4FBFA0; --partial:#D5A445; --panel:#151A1C; --well:#0B0F10; }
  }
  :root[data-theme=dark]{ --paper:#0E1213; --ink:#ECE9E3; --ink-soft:#8E9A9D; --rule:#242B2D;
    --pile:#E0705A; --pass:#4FBFA0; --partial:#D5A445; --panel:#151A1C; --well:#0B0F10; }
  :root[data-theme=light]{ --paper:#F7F5F0; --ink:#0F1416; --ink-soft:#5A6467; --rule:#D8D4CB;
    --pile:#B4472A; --pass:#1F6F5C; --partial:#A8761E; --panel:#FFFFFF; --well:#EFEDE7; }

  *{box-sizing:border-box}
  body{ margin:0; padding:clamp(14px,2.5vw,34px); background:var(--paper); color:var(--ink);
    font-family:ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif;
    font-variant-numeric:tabular-nums; line-height:1.5; }
  .mono{ font-family:ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,monospace; }
  .card{ max-width:1240px; margin:0 auto; background:var(--panel); border:1px solid var(--rule); }

  .head{ padding:clamp(18px,2.2vw,28px); border-bottom:1px solid var(--rule); }
  .eyebrow{ font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--ink-soft); }
  h1{ font-size:clamp(20px,2.3vw,28px); line-height:1.22; margin:8px 0 0; font-weight:600;
      letter-spacing:-.015em; text-wrap:balance; max-width:34ch; }
  .sub{ font-size:13.5px; color:var(--ink-soft); margin:9px 0 0; max-width:70ch; }

  .flow{ display:grid; grid-template-columns:1fr 1fr 1fr; }
  @media (max-width:900px){ .flow{ grid-template-columns:1fr } }
  .step{ padding:clamp(14px,1.8vw,22px); border-right:1px solid var(--rule);
         display:flex; flex-direction:column; gap:11px; min-width:0; }
  .step:last-child{ border-right:0 }
  @media (max-width:900px){ .step{ border-right:0; border-bottom:1px solid var(--rule) } }
  .stepname{ display:flex; align-items:baseline; gap:9px; }
  .stepnum{ font-size:11px; color:var(--pile); letter-spacing:.1em; }
  .steptitle{ font-size:13px; font-weight:600; letter-spacing:-.005em; }
  .stepnote{ font-size:12.5px; color:var(--ink-soft); margin:0; }
  .well{ background:var(--well); border:1px solid var(--rule); padding:9px;
         display:flex; align-items:center; justify-content:center; min-height:0; }
  .well img{ display:block; width:100%; height:auto; }
  .plan{ width:100%; height:auto; display:block; }
  .plan .o{ fill:none; stroke:var(--ink); stroke-width:1.5; vector-effect:non-scaling-stroke }
  .plan .p{ fill:var(--pile); stroke:var(--pile); stroke-width:1.1; vector-effect:non-scaling-stroke }

  .rows{ display:flex; flex-direction:column; }
  .row{ display:grid; grid-template-columns:1fr auto; gap:4px 12px; padding:11px 0;
        border-top:1px solid var(--rule); align-items:baseline; }
  .row:last-of-type{ border-bottom:1px solid var(--rule) }
  .item{ font-size:12.5px; line-height:1.35 }
  .item .th{ color:var(--ink-soft); font-size:11.5px; display:block; margin-top:3px }
  .nums{ text-align:right; white-space:nowrap }
  .big{ font-size:21px; font-weight:600; letter-spacing:-.02em }
  .vs{ color:var(--ink-soft); font-size:12.5px }
  .tag{ font-size:10.5px; letter-spacing:.06em; text-transform:uppercase; display:block; margin-top:3px }
  .ok{ color:var(--pass) } .part{ color:var(--partial) }
  .legend{ display:flex; gap:15px; font-size:11.5px; color:var(--ink-soft); flex-wrap:wrap }
  .legend span{ display:inline-flex; align-items:center; gap:6px }
  .sw{ width:9px; height:9px; background:var(--pile); display:inline-block }
  .sw.f{ background:transparent; border:1.5px solid var(--ink) }

  .foot{ padding:clamp(14px,1.8vw,22px); border-top:1px solid var(--rule);
         font-size:12.5px; color:var(--ink-soft); display:grid; grid-template-columns:1fr 1fr; gap:22px }
  @media (max-width:900px){ .foot{ grid-template-columns:1fr } }
  .foot b{ color:var(--ink); font-weight:600 }
</style>"""

BODY = """<div class="card">
  <div class="head">
    <div class="eyebrow mono">Foundation takeoff &mdash; sheet S2.01</div>
    <h1>Two quantities, reconstructed from raw CAD geometry.</h1>
    <p class="sub">Neither number below is written anywhere in the drawing. Each is computed from parsed
    geometry, then checked against the bill of quantities the engineers produced by hand.</p>
  </div>

  <div class="flow">
    <div class="step">
      <div class="stepname"><span class="stepnum mono">01</span><span class="steptitle">The drawing as delivered</span></div>
      <div class="well"><img src="data:image/jpeg;base64,__VIEWER__" alt="Footing plan in a CAD viewer"></div>
      <p class="stepnote">One sheet among fifteen sharing a single coordinate space. 51,356 entities,
      with load-bearing geometry sitting on layers named <span class="mono">1</span>,
      <span class="mono">3</span>, <span class="mono">10</span>.</p>
    </div>

    <div class="step">
      <div class="stepname"><span class="stepnum mono">02</span><span class="steptitle">What the pipeline reads</span></div>
      <div class="well">__SVG__</div>
      <div class="legend mono">
        <span><i class="sw f"></i> footing outline</span>
        <span><i class="sw"></i> pile &mdash; 0.20 &times; 0.20 m</span>
      </div>
      <p class="stepnote">42 footings scoped to this sheet across four types, each pile located inside
      the block definition behind the symbol.</p>
    </div>

    <div class="step">
      <div class="stepname"><span class="stepnum mono">03</span><span class="steptitle">Checked against the BOQ</span></div>
      <div class="well"><img src="data:image/jpeg;base64,__BOQ__" alt="Bill of quantities, section 1.1"></div>
      <div class="rows mono">
        <div class="row">
          <div class="item">&#3648;&#3626;&#3634;&#3648;&#3586;&#3655;&#3617; 0.20&times;0.20&times;6.00 m
            <span class="th">Precast piles</span></div>
          <div class="nums"><span class="big">66</span> <span class="vs">/ 66</span>
            <span class="tag ok">exact</span></div>
        </div>
        <div class="row">
          <div class="item">&#3588;&#3629;&#3609;&#3585;&#3619;&#3637;&#3605;&#3650;&#3588;&#3619;&#3591;&#3626;&#3619;&#3657;&#3634;&#3591;
            <span class="th">Structural concrete, m&sup3;</span></div>
          <div class="nums"><span class="big">46.4</span> <span class="vs">/ 53</span>
            <span class="tag part">88%</span></div>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div><b>How the numbers are built.</b> Footing symbols are CAD blocks. Each definition holds the pile
    marks as 0.20&nbsp;m squares and the pad outline as a polygon &mdash; so counting squares per type and
    placements per sheet gives the pile count, while the polygons plus the dimensioned 0.5&nbsp;m thickness
    give the concrete volume.</div>
    <div><b>Where the 6.6&nbsp;m&sup3; goes.</b> Pads are stepped in section rather than flat slabs, ground
    beams are not yet counted, and pedestal height is measured from geometry rather than read from an
    annotation &mdash; flagged for review, not silently assumed.</div>
  </div>
</div>"""

body = BODY.replace("__VIEWER__", viewer).replace("__BOQ__", boq).replace("__SVG__", svg)
out = Path(sys.argv[1])
out.write_text(HEAD + body, encoding="utf-8")
print(f"written {len(HEAD + body) // 1024} KB -> {out}")
