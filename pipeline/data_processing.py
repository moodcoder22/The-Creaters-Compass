"""
The Creator's Compass — Data Processing Pipeline
================================================
Dataset: Synthetic Creator Economy + CSO High Value Dataset Proxy

Transformation Log:
1. Generate synthetic creator data (n=500) based on real-world TidyTuesday/OWID distributions
2. Generate CSO regional economic proxy data (5 regions including IE-East, IE-South)
3. Merge on 'region' key (left join)
4. Compute composite 'sustainability_score' metric: (engagement_rate * 2) - (posting_freq_weekly * 0.5)
5. Add log-scaled 'followers_log' column for Vega-Lite scatter plot sizing
6. Filter out creators with followers < 1000 (noise reduction) — 500 → ~490 rows
7. Clip negative sustainability scores to 0 (interpretability)
8. Anonymize creator IDs as CR_XXXX (privacy-by-design)
9. Export to CSV for Vega-Lite consumption

Data Ethics:
- All creator data is SYNTHETIC — generated from published distribution parameters
- No real individuals are profiled or identifiable
- Wellbeing scores are modeled from academic literature on burnout correlates
- CSO proxy data mirrors the structural schema of the CSO Creative Industries HVD

Author: Ranjitha Kolar Srinivas
Date: 2026
"""

import pandas as pd
import numpy as np
import os

# ─── Reproducibility ─────────────────────────────────────────────────────────
np.random.seed(42)

# ─── Constants ───────────────────────────────────────────────────────────────
PLATFORMS    = ['TikTok', 'YouTube', 'Instagram', 'Twitch']
NICHES       = ['Gaming', 'Education', 'Lifestyle', 'Tech', 'Art', 'Comedy']
REGIONS      = ['IE-East', 'IE-South', 'EU-West', 'EU-East', 'US']
PLATFORM_P   = [0.40, 0.20, 0.30, 0.10]   # Real platform distribution weights
REGION_P     = [0.30, 0.20, 0.20, 0.10, 0.20]   # Heavier IE weighting for CSO relevance
N_CREATORS   = 500
MIN_FOLLOWERS = 1000


# ─── Step 1: Generate Creator Economy Data ───────────────────────────────────
def generate_creator_data(n: int = N_CREATORS) -> pd.DataFrame:
    """
    Generates synthetic creator economy metrics.

    Distributions grounded in:
    - Follower counts: log-normal (power-law tail, consistent with social media literature)
    - Posting frequency: normal, clipped to realistic 1–14 posts/week range
    - Engagement rate: normal, clipped to 0.1–15% (industry benchmarks, Influencer Marketing Hub)
    - Wellbeing score: normal, correlated negatively with high posting frequency (burnout research)
    - Monetization tier: log-normal revenue proxy segmented into 3 tiers

    Transformation applied:
    - sustainability_score = (engagement_rate × 2) − (posting_freq_weekly × 0.5)
      Rationale: High frequency with low engagement = unsustainable growth pattern
    - followers_log = log10(followers) for perceptual uniformity in size channel
    """
    # ── Raw attributes ────────────────────────────────────────────────────────
    followers        = np.random.lognormal(mean=10, sigma=2, size=n).astype(int)
    posting_freq     = np.random.normal(5, 3, n).clip(1, 14).round(1)
    engagement_rate  = np.random.normal(3.5, 1.5, n).clip(0.1, 15).round(2)

    # Wellbeing: modelled as inversely correlated with (posting_freq * inverse_engagement)
    # Creators who post a lot but get poor engagement show lower wellbeing
    burnout_pressure = (posting_freq / engagement_rate).clip(0, 5)
    wellbeing_raw    = np.random.normal(7.5, 1.5, n) - (burnout_pressure * 0.6)
    wellbeing        = wellbeing_raw.clip(1, 10).round(1)

    monetization_raw = np.random.lognormal(8, 3, n)
    monetization_tier = pd.cut(
        monetization_raw,
        bins=[0, 1_000, 10_000, 1_000_000_000],
        labels=['Hobbyist', 'Growing', 'Pro']
    )

    df = pd.DataFrame({
        'creator_id'         : [f"CR_{i:04d}" for i in range(n)],
        'platform'           : np.random.choice(PLATFORMS, n, p=PLATFORM_P),
        'niche'              : np.random.choice(NICHES, n),
        'region'             : np.random.choice(REGIONS, n, p=REGION_P),
        'followers'          : followers,
        'posting_freq_weekly': posting_freq,
        'engagement_rate'    : engagement_rate,
        'wellbeing_score'    : wellbeing,
        'monetization_tier'  : monetization_tier,
    })

    # ── Derived / Composite Metrics ───────────────────────────────────────────
    # Transformation 1: Sustainability Score
    df['sustainability_score'] = (
        (df['engagement_rate'] * 2) - (df['posting_freq_weekly'] * 0.5)
    ).clip(0).round(2)

    # Transformation 2: Log followers for Vega-Lite size channel
    df['followers_log'] = np.log10(df['followers'].clip(1)).round(2)

    return df


# ─── Step 2: Generate CSO Economic Proxy ─────────────────────────────────────
def generate_cso_proxy() -> pd.DataFrame:
    """
    Mimics CSO High Value Dataset structure for Creative Industries.
    Source schema: CSO Creative Industries HVD (data.cso.ie)

    To use real CSO data, replace this function with:
        df = pd.read_csv('data/raw/cso_creative_industries.csv')

    Columns mirror the CSO schema:
    - creative_sector_employment: total headcount in creative digital sectors
    - avg_creative_earnings_eur:  median annual earnings (€)
    - digital_export_intensity:   ratio of digitally-exported creative output (0–1)
    """
    return pd.DataFrame({
        'region'                      : REGIONS,
        'creative_sector_employment'  : [15_000, 8_000, 50_000, 20_000, 200_000],
        'avg_creative_earnings_eur'   : [45_000, 42_000, 55_000, 35_000,  65_000],
        'digital_export_intensity'    : [0.80, 0.60, 0.90, 0.50, 0.95],
    })


# ─── Step 3: Merge and Clean ─────────────────────────────────────────────────
def merge_and_clean(df_creators: pd.DataFrame, df_cso: pd.DataFrame) -> pd.DataFrame:
    """
    Merge creator data with CSO regional data.
    Filtering applied: remove creators with followers < 1000 (noise / bot accounts)
    """
    df = pd.merge(df_creators, df_cso, on='region', how='left')

    # Filter: min follower threshold
    before = len(df)
    df = df[df['followers'] >= MIN_FOLLOWERS].reset_index(drop=True)
    after = len(df)
    print(f"  ✂️  Filtered {before - after} rows (followers < {MIN_FOLLOWERS})")

    # Drop rows with any null values in key columns
    key_cols = ['engagement_rate', 'wellbeing_score', 'sustainability_score']
    df = df.dropna(subset=key_cols)

    return df


# ─── Main Execution ───────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  The Creator's Compass — Data Pipeline")
    print("=" * 60)

    print("\n[1/4] Generating creator economy data...")
    df_creators = generate_creator_data(N_CREATORS)
    print(f"  {len(df_creators)} synthetic creator records generated")

    print("\n[2/4] Generating CSO regional proxy data...")
    df_cso = generate_cso_proxy()
    print(f"  {len(df_cso)} regional records generated")

    print("\n[3/4] Merging and cleaning...")
    df_final = merge_and_clean(df_creators, df_cso)
    print(f"  Final dataset: {df_final.shape[0]} rows × {df_final.shape[1]} columns")

    print("\n[4/4] Saving to CSV...")
    os.makedirs('data/processed', exist_ok=True)
    output_path = 'data/processed/creator_compass_clean.csv'
    df_final.to_csv(output_path, index=False)
    print(f"  Saved → {output_path}")

    print("\n Column Summary:")
    print(df_final.dtypes.to_string())

    print("\n Key Statistics:")
    print(df_final[['engagement_rate', 'wellbeing_score',
                     'posting_freq_weekly', 'sustainability_score']].describe().round(2).to_string())

    print("\n  Platform Distribution:")
    print(df_final['platform'].value_counts().to_string())

    print("\n  Region Distribution:")
    print(df_final['region'].value_counts().to_string())

    print("\n" + "=" * 60)
    print("  Pipeline complete. Run index.html to view visualization.")
    print("=" * 60)


if __name__ == "__main__":
    main()
