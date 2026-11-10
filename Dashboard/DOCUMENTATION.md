# Indian Super League (ISL) Player Analytics Platform
## System Architecture, Tech Stack & Mathematical Formulations

This document provides complete technical and mathematical documentation for the **Indian Super League (ISL) Player Analytics Platform**. The platform provides dynamic tactical scouting, possession-adjusted metrics (PAdj), positional percentiles, interactive quadrant exploration, and spatial pitch visualizations for 189 registered players across all 13 ISL franchises.

---

## 1. Visual & Aesthetic Design System

The application strictly adheres to the requested earth/mocha palette, paired with dark typography and light surfaces:

| Hex Code | Color Name | Platform Usage Role |
| :--- | :--- | :--- |
| `[#815337]` | Deep Roasted Chestnut | Primary brand accent, top percentile rank, **Pillar 1 (Attacking & Threat)** |
| `[#926a52]` | Warm Mocha / Walnut | Secondary accent, **Pillar 2 (Creativity & Progression)** |
| `[#ab8a76]` | Muted Caramel / Latte | Tertiary accent, **Pillar 3 (Defensive & Duels)**, pitch line markings |
| `[#d2b7a7]` | Soft Sand / Tan | Card borders, quadrant dividing gridlines, subtle separators |
| `[#f7e5da]` | Warm Biscuit Cream | Light surface fills, pill badges, card backgrounds |
| `[#63422d]` | Dark Walnut / Espresso | **Pillar 4 (Possession & Efficiency)** |
| `[#FDFBF9]` / `[#FAF6F3]` | Off-White & Cream | Main viewport background, light canvas aesthetics |
| `[#231812]` | Deep Espresso | Dark font color for high contrast and readability |

---

## 2. Multi-Page Application Architecture

The platform is designed to avoid clutter by utilizing structured pages and interactive tabs:

```
Dashboard/
├── .streamlit/
│   └── config.toml                  # Theme definition (palette, fonts, background)
├── Home.py                          # Executive Overview & League Standings
├── pages/
│   ├── 1_🏆_Positional_Matrix.py    # Quadrant exploration & positional leaderboards
│   ├── 2_👤_Player_Profile.py       # Deep scout report: PyPizza, Touch KDE & Shot Maps
│   ├── 3_⚔️_Player_Comparison.py    # Head-to-Head benchmark & delta matrix
│   ├── 4_🎯_Scouting_Role_Finder.py # Tactical archetypes with custom weighted sliders
│   ├── 5_📐_TechStack_&_Math.py     # In-app interactive mathematical documentation
│   └── 6_💾_DuckDB_Analytical_Store.py # SQL workbench & schema explorer
├── src/
│   ├── config.py                    # Palette, 65 KPIs, 4 pillars, club metadata
│   ├── db_service.py                # DuckDB read-only connection with @st.cache_data
│   ├── math_engine.py               # PAdj, empirical CDF, Z-scores, pillar scoring
│   ├── viz_pizza.py                 # mplsoccer PyPizza radar charts
│   ├── viz_pitch.py                 # mplsoccer Pitch: KDE touch heatmaps & shot maps
│   ├── viz_interactive.py           # Plotly interactive 2D quadrant scatter & leaderboards
│   └── ui_helpers.py                # Custom CSS injection, metric cards, hero banners
└── data/
    └── isl_analytics.duckdb         # Local analytical storage (189 players, 13 teams, events)
```

---

## 3. Technology Stack

| Layer | Library & Version | Purpose & Rationale |
| :--- | :--- | :--- |
| **Reactive Web Framework** | `Streamlit 1.67.0` | High-performance multi-page interactive web application with reactive caching (`@st.cache_data`). |
| **Pitch & Radar Plots** | `mplsoccer 1.8.1` & `matplotlib 3.11.2` | Authentic football visualizations including `PyPizza` percentile radars and `Pitch` (StatsBomb coordinate system) for Kernel Density Estimate (KDE) touch heatmaps and half-pitch shot trajectory maps. |
| **Interactive Charts** | `plotly 7.1.0` | Client-side interactive 2D quadrant scatter plots with cohort medians, responsive tooltips, and dynamic KPI selection. |
| **Data Manipulation & Math** | `pandas 3.1.1` & `scipy 1.18.1` | Vectorized DataFrame operations, percentile ranking (`scipy.stats`), Z-score normalization, and possession scaling. |
| **Local Analytical Storage** | `duckdb 2.0.0` | Embeddable columnar OLAP analytical storage engine providing sub-millisecond SQL queries and zero-copy Apache Arrow integration. |
| **Data Source Feed** | `Sofascore ISL Feed` | Official statistics covering the **2026/2027 Indian Super League Campaign** (Matchweeks 1–6, defending champions East Bengal FC) across all 13 franchises (179 active squad members). |

---

## 4. Key Performance Indicators (KPIs) by Position Group

Every player is assessed within their designated position group across the **4 Analytical Pillars**:

### 1. Forwards / Strikers
- **Attacking & Threat:** Goals/90, Non-Penalty xG (npxG)/90, Post-Shot xG (PSxG), Shots on Target %
- **Creativity & Progression:** xG Assisted (xGA)/90, Shot-Creating Actions (SCA)/90, Touches in Box/90
- **Defensive & Duels:** Final-Third Tackles, High-Intensity Pressures/90, Aerial Win %
- **Possession & Efficiency:** Goal Conversion %, npxG per Shot (Shot Quality), Offsides/90 *(inverted)*

### 2. Wingers / Attacking Mids
- **Attacking & Threat:** npxG + xGA/90, Goal-Creating Actions (GCA)/90, Box Entries (Carries + Passes)/90
- **Creativity & Progression:** Key Passes/90, Progressive Carries/90, Successful Take-On %, Cross Completion %
- **Defensive & Duels:** Counter-Pressures/90, Recoveries in Attacking Third/90
- **Possession & Efficiency:** Pass Completion % in Final Third, Dispossessed/90 *(inverted)*, Progressive Pass Received/90

### 3. Central / Holding Mids
- **Attacking & Threat:** Late Box Arrivals/90, Long-Range Shot xG
- **Creativity & Progression:** Progressive Passes/90, Passes into Final Third/90, Deep Completions, Through Balls/90
- **Defensive & Duels:** Possession-Adjusted Tackles + Interceptions (PAdj T+I)/90, Ball Recoveries/90, Duel Win %
- **Possession & Efficiency:** Pass Completion % under Pressure, Press Resistance (Retention %), Turnovers/90 *(inverted)*

### 4. Fullbacks / Wingbacks
- **Attacking & Threat:** xGA/90, Open-Play Crosses Completed/90, Overlapping Runs into Final Third
- **Creativity & Progression:** Progressive Carries/90, Progressive Passes/90, Final-Third Entries/90
- **Defensive & Duels:** 1v1 Dribble Tackle % (Dribbled Past %), PAdj Interceptions/90, Back-Post Aerial Win %
- **Possession & Efficiency:** Pass Completion %, Progressive Distance Carried/90

### 5. Center Backs
- **Attacking & Threat:** Set-Piece xG/90, Set-Piece Aerial Contacts
- **Creativity & Progression:** Line-Breaking Passes/90, Progressive Pass Distance/90, Switches of Play/90
- **Defensive & Duels:** Aerial Duel Win %, Ground Tackle Win %, Shots Blocked/90, Clearances/90, Errors Leading to Shot *(inverted)*
- **Possession & Efficiency:** Build-up Pass Completion %, Long Pass Accuracy %

### 6. Goalkeepers
- **Attacking & Threat:** *N/A (Specialist Position)*
- **Creativity & Progression:** Passes > 40 Yards Completed %, Launch %, Goal Kick Length
- **Defensive & Duels:** PSxG minus Goals Allowed (PSxG+/-)/90 (Shot-Stopping), Crosses Stopped %, Sweeper Actions Outside Box/90
- **Possession & Efficiency:** Save %, Pass Completion % under High Press, Clean Sheet %

---

## 5. Mathematical Formulations & Methodologies

### 5.1 Per-90 Normalization
All counting statistics (goals, pressures, progressive passes, tackles) are normalized per 90 regulation minutes to account for variation in playing time:
$$\text{Metric}_{p90} = \left(\frac{\text{Metric}_{\text{raw}}}{\text{Minutes}}\right) \times 90$$

---

### 5.2 Possession-Adjusted Defensive Metrics (PAdj)
Players in high-possession teams (e.g. Mumbai City FC at 61.2% possession) have significantly fewer opportunities to perform defensive actions (tackles, interceptions) than players in low-possession teams (e.g. Hyderabad FC at 41.5%). 

#### A. Colin Trainor Linear Formulation
$$\text{PAdj}_{\text{linear}} = \text{Metric}_{\text{raw}} \times \left( \frac{50}{100 - \text{Possession}_{\text{team}}} \right)$$
This scales defensive actions relative to an exact 50% possession league baseline.

#### B. Sigmoidal Logistic Possession Adjustment
To avoid extreme asymptotic distortions at possession extremes (< 35% or > 65%), the platform implements a logistic sigmoid adjustment curve:
$$\text{PAdj}_{\text{sigmoid}} = \text{Metric}_{\text{raw}} \times \frac{2}{1 + e^{-k \cdot (50 - \text{Possession}_{\text{opp}})}}$$
where $k = 0.08$ is the steepness coefficient and $\text{Possession}_{\text{opp}} = 100 - \text{Possession}_{\text{team}}$.

---

### 5.3 Positional Percentile Ranking (Empirical CDF)
Percentiles are computed strictly within each player's positional peer cohort using the empirical Cumulative Distribution Function (CDF) with mid-point continuity correction:
$$\text{Percentile}(x) = \left( \frac{\sum_{i=1}^N \mathbb{I}(X_i < x) + 0.5 \sum_{i=1}^N \mathbb{I}(X_i = x)}{N} \right) \times 100$$
where $\mathbb{I}(\cdot)$ is the indicator function and $N$ is the total cohort size.

#### Inverted Cost Metrics:
For metrics where lower counts indicate superior performance (Turnovers/90, Dispossessed/90, Errors Leading to Shot, Offsides/90):
$$\text{Percentile}_{\text{inverted}}(x) = 100 - \text{Percentile}(x)$$

Percentiles are bounded in the range $[1.0, 99.0]$ to maintain visual stability in radial radar plots.

---

### 5.4 Standard Score (Z-Score)
Quantifies statistical divergence from the positional peer mean:
$$z = \frac{x - \mu}{\sigma}$$
$$\mu = \frac{1}{N}\sum_{i=1}^N x_i, \quad \sigma = \sqrt{\frac{1}{N-1}\sum_{i=1}^N (x_i - \mu)^2}$$

---

### 5.5 Post-Shot Expected Goals Delta (PSxG +/-)
Quantifies goalkeeper shot-stopping ability by isolating the post-strike shot trajectory quality from defensive concessions:
$$\text{PSxG}+/-_{p90} = \text{PSxG Faced}_{p90} - \text{Goals Allowed}_{p90}$$
- $\text{PSxG}+/- > 0$: Goalkeeper prevented more goals than expected from the quality of shots faced on target (elite shot-stopper).
- $\text{PSxG}+/- < 0$: Goalkeeper conceded more goals than predicted by the post-shot model.

---

### 5.6 Shot Quality & Conversion Rate
$$\text{Shot Quality} = \frac{\text{npxG}}{\text{Total Non-Penalty Shots}}$$
$$\text{Goal Conversion Rate \%} = \left(\frac{\text{Goals}}{\text{Total Shots}}\right) \times 100$$

---

### 5.7 Press Resistance & Retention Rate
Measures the ability of midfielders and deep ball progressors to retain possession when actively pressed:
$$\text{Press Resistance \%} = \left(\frac{\text{Successful Possessions Retained Under Pressure}}{\text{Total Actions Received Under Active Pressure}}\right) \times 100$$

---

### 5.8 4-Pillar Composite Scores
For each of the four pillars, an aggregate rating $S_{\text{pillar}} \in [0, 100]$ is computed:
$$S_{\text{pillar}} = \frac{1}{K}\sum_{j=1}^K \text{Percentile}(x_j)$$
where $K$ is the number of active KPIs assigned to that pillar for the position group.

---

### 5.9 Tactical Archetype Weighted Fit Model
Recruitment target fit scores are computed using weighted linear combinations of normalized percentiles:
$$\text{Fit Score} = \sum_{m=1}^M w_m \cdot \text{Percentile}(x_m), \quad \sum_{m=1}^M w_m = 1.0$$
where $w_m$ represents user-customizable slider weights.

---

## 6. How to Run the Application

The application is fully pre-configured in the repository:

```bash
# 1. Activate the Python virtual environment
source .venv/bin/activate

# 2. Launch the Streamlit application
streamlit run Home.py --server.port=8501
```

Once started, navigate to `http://localhost:8501` to access the full platform.
