# The Creator's Compass

**Navigating success, sustainability and wellbeing in the GenZ attention economy.**

Creators are told to "post more to grow", but what if that advice is burning them out? The Creator's Compass is an interactive dashboard I built to explore that tension. It compares the usual growth metrics (followers, posting frequency, engagement) with creator wellbeing across platforms, content niches and regions, with extra context from Irish creative-industry economics.

## What you can explore

| # | View | Question it answers |
|---|------|---------------------|
| ① | **Success Matrix**: engagement vs. posting frequency scatter | Where is the sweet spot, and where does burnout begin? Points fade as wellbeing drops. |
| ② | **Niche Comparison**: average engagement by content type | Do focused niches like Education and Art outperform broad ones? |
| ③ | **Wellbeing Heatmap**: platform × posting-frequency band | Which platforms hold up best under a heavy posting schedule? |
| ④ | **Regional Context**: earnings vs. digital export intensity | How do Irish regions compare with EU and US creative economies? |
| ⑤ | **Sustainability Distribution** by monetisation tier | Are pro creators more sustainable or just bigger? |
| ⑥ | **Safe Zone Quadrant**: wellbeing vs. sustainability | Who is both thriving and sustainable? |

**Interactions:** platform filter buttons, a *Wellbeing ↔ Sustainability* lens toggle for the scatter, a brush selection that links the scatter to the niche chart, and detailed tooltips on every point.

## Running it

The dashboard is a single static page:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

(You can also open `index.html` directly in a browser.)

To regenerate the dataset:

```bash
pip install -r requirements.txt
python pipeline/data_processing.py   # writes data/processed/creator_compass_clean.csv
```

## Project structure

```
.
├── index.html                    # Interactive dashboard (Vega-Lite v5 + vanilla JS)
├── pipeline/
│   └── data_processing.py        # Python ETL: generate → merge → derive metrics → filter → export
├── specs/
│   └── visualization.vl.json     # Standalone Vega-Lite spec (open in the Vega Editor)
├── data/processed/
│   └── creator_compass_clean.csv # Pipeline output (477 creators × 14 columns)
└── docs/
    └── design.md                 # Design notes: tasks, encodings, rejected alternatives, evaluation
```

## Data and method

- **Creator metrics (n = 500, 477 after filtering)** are **synthetic**. They are generated from published distribution patterns: log-normal follower counts, realistic posting and engagement ranges, and wellbeing modelled to fall as posting pressure rises compared with engagement.
- **Regional economics** follow the schema of the CSO Creative Industries High Value Dataset (employment, average earnings, digital export intensity) for IE-East, IE-South, EU-West, EU-East and the US. The values are illustrative proxies.
- **Derived metrics:**
  - `sustainability_score = (engagement_rate × 2) − (posting_freq × 0.5)` rewards quality over volume.
  - `followers_log` keeps very large accounts from dominating the size channel.
- For portability, the dashboard generates a matching dataset in the browser. The CSV is the pipeline output, and the standalone Vega-Lite spec uses it.

See [docs/design.md](docs/design.md) for the full reasoning behind each encoding and interaction.

## Ethics

No real creators are profiled. All records are synthetic, with anonymised IDs (`CR_XXXX`). Wellbeing is shown as a first-class metric on purpose, to push back on "hustle culture" stories about the creator economy. Because the data is synthetic, the patterns are illustrations, not causal findings.

## What's next

- Use real creator data (e.g. Social Blade-style APIs) and real CSO HVD data
- Add a time dimension to follow creators' paths over months
- Build a mobile-first, single-scroll layout

## Tech

Python (pandas, NumPy) · Vega-Lite v5 / Vega-Embed · HTML/CSS/JS
