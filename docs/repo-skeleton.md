

sAI/
├── data/                      # gitignored — proprietary, never committed (Rule 5)
│   ├── raw/                   # the real DWG/DXF/PNG from the aunt
│   ├── ground_truth/          # the finished BOQs = your answer key
│   └── fixtures/              # tiny anonymized samples safe for tests
│
├── src/sai/
│   ├── parse/                 # DXF → structured entities   (NEW: you write, w/ hints)
│   │   ├── loader.py          #   open DXF, walk layers/entities
│   │   └── entities.py        #   the data contract (Pydantic)
│   ├── measure/               # geometry math               (NEW: you write)
│   │   └── lengths.py         #   sum line lengths, areas, counts — deterministic
│   ├── classify/              # LLM stage                   (NEW: first LLM call, you write)
│   │   ├── prompts.py         #   classification / item-code mapping prompts
│   │   └── client.py          #   Claude API call + structured output
│   ├── flag/                  # uncertainty flagging
│   ├── output/                # → Excel (openpyxl)          (REPEATED after #1: I write)
│   └── pipeline.py            # wire the stages: parse→measure→classify→flag→output
│
├── eval/                      # THE CENTER OF GRAVITY       (NEW: you write, w/ hints)
│   ├── harness.py             #   run pipeline on a DWG, score output vs ground_truth
│   ├── metrics.py             #   recall / accuracy per line item
│   └── reports/               #   dated score runs — your before/after story
│
├── scripts/
│   └── render_over_png.py     # week-1 validation: draw parsed JSON on the PNG preview
│
├── notebooks/                 # scratch exploration (parser sanity checks)
└── tests/                     # deterministic stuff only (geometry math), not the LLM