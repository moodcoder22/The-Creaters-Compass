# The Creator's Compass — Design Notes

Notes on why the dashboard looks and behaves the way it does: the questions it answers, how the data was built, the encoding choices (and the ones I rejected), and what I'd do next.

- **Dataset:** Synthetic creator economy data + a CSO Creative Industries proxy
- **Built with:** an interactive HTML dashboard on Vega-Lite v5, with a Python ETL

# 1. Why — Problem Framing & Task Definition

GenZ creators are told "post more to grow" — but what if that advice is
burning them out? This project visualises the tension between
conventional growth metrics (followers, posting frequency) and creator
wellbeing, drawing on real-world distribution patterns (TidyTuesday,
OWID) anchored to Irish regional economic data (CSO HVD proxy).

## 1.1 Target Users & Tasks

| **User Persona**   | **Core Task**                                          | **Success Metric**                                     |
|--------------------|--------------------------------------------------------|--------------------------------------------------------|
| GenZ Creator       | "Am I posting too much for my engagement return?"      | Identify sustainable frequency band in &lt;15 sec      |
| CSO Policy Analyst | "Which Irish regions need creator support programmes?" | Compare IE-East vs. EU benchmarks on earnings + export |

# 2. What — Data & Transformations

## 2.1 Data Sources

-   Creator Economy Metrics (n=500 synthetic, 477 post-filter):
    > Distributions grounded in TidyTuesday social media datasets and
    > OWID creator economy reports. Privacy-preserving: all records are
    > synthetic; no real individuals profiled.

-   CSO Creative Industries HVD Proxy: Regional employment, average
    > earnings (€), and digital export intensity for 5 regions (IE-East,
    > IE-South, EU-West, EU-East, US). Mirrors schema of data.cso.ie
    > High Value Datasets.

## 2.2 Transformation Log

| **Step** | **Transformation**                                | **Rationale**                                                                |
|----------|---------------------------------------------------|------------------------------------------------------------------------------|
| 1        | Lognormal follower generation (μ=10, σ=2)         | Power-law social media distribution (Barabási-Albert model)                  |
| 2        | Wellbeing = rnorm(7.5, 1.5) − (freq/eng × 0.6)    | Burnout inversely correlated with frequency÷engagement ratio (academic lit.) |
| 3        | sustainability\_score = (eng×2) − (freq×0.5)      | Domain-informed composite: rewards quality over volume                       |
| 4        | followers\_log = log₁₀(followers)                 | Log-scaling for size channel — prevents large creators dominating            |
| 5        | Filter: followers ≥ 1,000 (−23 rows)              | Removes bot/noise accounts below meaningful engagement threshold             |
| 6        | freq\_band: ordinal binning (1–3, 4–6, 7–10, 11+) | Enables heatmap aggregation by posting rhythm category                       |
| 7        | Left join on region key                           | Attaches CSO earnings + export data to each creator record                   |

# 3. How — Encoding Rationale

## 3.1 Chart-by-Chart Encoding Decisions

**Chart ①: Success Matrix (Scatter Plot)**

| **Visual Channel** | **Data Field**        | **Justification (Cleveland & McGill hierarchy)**                                                             |
|--------------------|-----------------------|--------------------------------------------------------------------------------------------------------------|
| X-position         | posting\_freq\_weekly | Most accurate perceptual channel for quantitative comparison — enables burnout threshold reading             |
| Y-position         | engagement\_rate      | Secondary quantitative axis — reveals the engagement sweet spot                                              |
| Hue (colour)       | platform              | Nominal categorical — platform is the creator's primary identity anchor                                      |
| Area (size)        | followers (log₁₀)     | Log-scaled quantitative — handles power-law distribution without outlier dominance                           |
| Opacity (value)    | wellbeing\_score      | NOVEL: surfaces 'hidden' burnout risk without adding a 5th spatial dimension — low opacity = at-risk creator |

**Chart ②: Niche Comparison (Horizontal Bar)**

-   X = mean engagement rate (quantitative length — perceptually
    > accurate for comparison)

-   Y = niche sorted descending — enables instant ranking
    > (pre-attentive)

-   Colour = niche (redundant encoding — aids scanning when brush dims
    > non-selected bars)

**Chart ③: Wellbeing Heatmap (Platform × Frequency Band)**

-   Sequential diverging colour scale (red→green) maps mean wellbeing —
    > the single most important perceptual task here is 'is this cell
    > healthy or not?'

-   Ordinal X axis (frequency bands) enables pattern detection across
    > posting rhythm categories — not possible in scatter format

**Chart ④: Regional CSO Dual-Axis Layer (Bar + Line)**

-   Bars = earnings (quantitative magnitude) — the primary economic
    > context metric

-   Stroke-dash line overlay = export intensity — dual-encoding for
    > policy insight (high earnings + high export = strategic
    > opportunity region)

-   Independent Y-axis scales to allow comparison of differently-scaled
    > metrics on same X axis

# 4. Alternative Encodings Considered

| **Alternative**                                       | **Why Rejected**                                                                                                        | **What We Chose Instead**                                                               |
|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| 3D Scatter Plot (x, y, z for 3 quantitative vars)     | 3D distorts quantitative perception; fails WCAG accessibility standards; 'gimmick over clarity'                         | 2D scatter with opacity as 5th channel — no perceptual distortion                       |
| Heatmap grid instead of scatter for Chart ①           | Aggregation hides individual outliers; a creator at risk of burnout is an individual story, not a bin average           | Scatter preserves individual agency; heatmap used only for platform×frequency aggregate |
| Color for wellbeing + hue for platform (dual nominal) | Double-encoding of the colour channel creates ambiguity — which legend applies to which visual element?                 | Colour = platform (nominal); opacity = wellbeing (quantitative value channel)           |
| Parallel Coordinates for multi-attribute view         | Requires user training; task is correlation exploration not pattern-across-all-attributes; poor for non-expert audience | Linked scatter+bar with brush selection — immediate mental model for all user types     |
| Pie/donut charts for platform distribution            | Pie charts are poor for comparison of &gt;3 slices; no support for continuous variable mapping                          | Colour-coded scatter — platform distribution emerges naturally from visual density      |

# 5. Interaction Design

The dashboard implements coordinated multiple views (CMV) — a
best-practice interaction paradigm for exploratory data analysis. All
interactions serve a specific analytical task rather than being
decorative.

| **Interaction**                        | **Mechanism**                                                              | **Task It Supports**                                                       |
|----------------------------------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------|
| Platform Filter Buttons                | JavaScript state → Vega-Lite re-render with filtered data                  | "Show me only TikTok creators" — isolates platform-specific patterns       |
| Wellbeing / Sustainability Lens Toggle | Switches opacity encoding field (wellbeing\_score ↔ sustainability\_score) | Allows analyst to compare two different risk lenses on same scatter layout |
| Brush Selection (Scatter → Bar)        | Vega-Lite interval param dims non-selected bars in niche chart             | "What niches do high-engagement, low-frequency creators cluster in?"       |
| Rich Tooltips                          | All 8 key attributes surfaced on hover without cluttering the main view    | Supports detail-on-demand (Shneiderman's Information Seeking Mantra)       |
| Hover highlight on KPI cards           | CSS micro-animation draws attention to insight callouts                    | Contextualises statistical insights for non-technical users                |

# 6. Insights Discovered

## 6.1 Insight-to-Encoding Mapping

| **Insight**                     | **Visual Evidence**                                                                                      | **User Action to Discover**                                                  |
|---------------------------------|----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| Burnout Threshold (&gt;10×/wk)  | Faded (low opacity) points cluster in high X region of scatter; heatmap shows red cells in 11+/wk column | Brush the 11+/wk region of scatter → observe opacity pattern + check heatmap |
| Micro-Community Advantage       | Education and Art bars lead in Chart ② despite smaller total audiences                                   | Sort niche bar → compare Education/Art vs. Lifestyle engagement means        |
| Irish Export Edge (CSO insight) | IE-East shows highest export intensity line point in Chart ④ despite mid-tier earnings                   | Read dual-axis Chart ④ → note IE-East line peak vs. earnings bar             |
| Platform Migration Path         | Pro-tier creators (large, high-opacity points) cluster in YouTube colour with high sustainability scores | Filter to YouTube only → observe Pro-tier concentration in safe quadrant     |

# 7. Evaluation & Limitations

## 7.1 User Testing

-   Method: 3-user think-aloud protocol (15-minute
    > sessions)

-   Task: "Find a high-performing creator who appears to be at risk of
    > burnout"

-   Result: 100% task success within 15 seconds using the opacity
    > encoding in Chart ①

-   Feedback incorporated: Added platform filter buttons (users wanted
    > to isolate TikTok vs. YouTube); added KPI callout cards for
    > non-expert users

## 7.2 Limitations & Future Work

-   Synthetic data limits causal claims — wellbeing correlations are
    > modelled, not measured. Real-world API integration (Creator.co,
    > Social Blade) is planned for V2.

-   CSO proxy uses assumed values — actual CSO HVD ingestion would
    > strengthen the regional economic layer. The schema and merge logic
    > are production-ready for real data.

-   Temporal dimension absent — a longitudinal view showing creator
    > trajectories over 12 months would add significant predictive
    > insight.

-   Mobile responsiveness — the dashboard is responsive via CSS grid but
    > the multi-chart layout favours desktop; a mobile-first
    > single-scroll version is a V2 deliverable.

# 8. Accessibility & Ethical Considerations

| **Consideration**   | **Implementation**                                                                                                                                            |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Colour blindness    | Platform scheme uses Category10 subset tested with Color Oracle simulator; heatmap uses redyellowgreen perceptually-uniform diverging scale                   |
| Dark mode           | Default dark theme reduces eye strain (target demographic: GenZ, primarily screens post-9pm)                                                                  |
| Privacy by design   | No real creator data; synthetic IDs (CR\_0001) ensure zero re-identification risk                                                                             |
| Burnout framing     | Deliberately surfaces creator wellbeing as a first-class metric — not an afterthought — to challenge 'hustle culture' narratives in creator economy discourse |
| Accessible tooltips | All data points expose full attribute context on hover — supports screen reader-compatible data access patterns                                               |
