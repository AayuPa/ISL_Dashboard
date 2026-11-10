"""
Documentation of Tech Stack and Mathematics for Indian Super League (ISL) Player Analytics.
Details the analytical pipeline, statistical methodologies, and complete mathematical formulations.
"""

import streamlit as st
import pandas as pd
from src.config import PALETTE, POSITION_KPIS, PILLAR_CONFIG
from src.ui_helpers import load_custom_css, render_hero_banner, render_sidebar_brand

st.set_page_config(
    page_title="Tech Stack & Math • ISL Analytics",
    page_icon="📐",
    layout="wide"
)

load_custom_css()
render_sidebar_brand()

render_hero_banner(
    title="Technical Stack & Mathematical Methodologies",
    subtitle="In-depth architectural documentation, statistical formulation, and analytical definitions.",
    badge="DOCUMENTATION & METHODOLOGY"
)

doc_tab1, doc_tab2, doc_tab3 = st.tabs([
    "🛠️ Tech Stack Architecture",
    "📐 Mathematical Calculations & Formulas",
    "📚 Complete KPI Data Dictionary"
])

with doc_tab1:
    st.markdown(
        f"""
        <div style="background:{PALETTE['white']}; border:1px solid {PALETTE['border']}; border-radius:12px; padding:22px; margin-bottom:20px;">
            <h3 style="color:{PALETTE['primary']}; margin-top:0;">Platform Architectural Overview</h3>
            <p style="color:{PALETTE['text_muted']}; font-size:0.9rem; line-height:1.6;">
                The platform is engineered as an enterprise-grade football intelligence suite designed for Indian Super League (ISL) sporting directors, chief analysts, and recruitment scouts. It combines local columnar OLAP storage with interactive vector visualization and advanced spatial pitch rendering.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown(
            f"""
            <div class="pillar-card">
                <div style="font-size:1.1rem; font-weight:700; color:{PALETTE['primary']};">
                    💾 Analytical Storage & Core Compute
                </div>
                <div style="font-size:0.85rem; color:{PALETTE['text_dark']}; margin-top:8px; line-height:1.6;">
                    • <b>DuckDB 2.0.0:</b> Embeddable columnar analytical engine providing sub-millisecond SQL queries, zero-copy Apache Arrow integration, and parquet-like vectorized query execution directly on disk.<br>
                    • <b>Pandas 3.1.1 & NumPy 2.5.4:</b> High-performance vectorized DataFrame manipulations, window aggregations, and tabular restructuring.<br>
                    • <b>SciPy 1.18.1:</b> Statistical distribution transformations, empirical cumulative distribution functions, and z-score standardizations.<br>
                    • <b>Sofascore ISL Feed:</b> Granular event data feed covering all 13 franchises, 179 active squad members for the 2026/2027 season, and spatial coordinate feeds.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_t2:
        st.markdown(
            f"""
            <div class="pillar-card">
                <div style="font-size:1.1rem; font-weight:700; color:{PALETTE['secondary']};">
                    🎨 Visualization & Reactive Frontend
                </div>
                <div style="font-size:0.85rem; color:{PALETTE['text_dark']}; margin-top:8px; line-height:1.6;">
                    • <b>Streamlit 1.67.0:</b> Dynamic, multi-page application state management with reactive caching (<code>@st.cache_data</code>).<br>
                    • <b>mplsoccer 1.8.1 & Matplotlib 3.11.2:</b> Generates authentic <code>PyPizza</code> radar charts and vertical/horizontal <code>Pitch</code> KDE touch heatmaps and shot maps.<br>
                    • <b>Plotly 7.1.0:</b> Interactive 2D quadrant scatter plots with responsive tooltips and cohort median benchmark lines.<br>
                    • <b>Palette Integrity:</b> Adheres strictly to the user-specified warm earth/mocha palette (<code>#815337</code>, <code>#926a52</code>, <code>#ab8a76</code>, <code>#d2b7a7</code>, <code>#f7e5da</code>) with high-contrast dark fonts (<code>#231812</code>) and light aesthetics.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with doc_tab2:
    st.markdown(
        f"""
        <div style="background:{PALETTE['white']}; border:1px solid {PALETTE['border']}; border-radius:12px; padding:22px; margin-bottom:20px;">
            <h3 style="color:{PALETTE['primary']}; margin-top:0;">Statistical & Mathematical Formulations</h3>
            <p style="color:{PALETTE['text_muted']}; font-size:0.9rem; line-height:1.6;">
                Every analytical metric in this platform is normalized and standardized using rigorous mathematical models to eliminate tactical bias and minutes-played distortions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 1. Per-90 Normalization
    st.markdown(f"#### 1. Per-90 Minute Normalization ($M_{{p90}}$)")
    st.write("To benchmark players with varying match volume on an equitable basis, all counting metrics are normalized to a standard 90-minute regulation match length:")
    st.latex(r"M_{p90} = \left(\frac{M_{\text{raw}}}{\text{Minutes}}\right) \times 90")
    st.caption("Where $M_{\\text{raw}}$ is the raw event count (e.g. goals, pressures, progressive passes) and $\\text{Minutes}$ is total pitch time.")
    
    st.divider()
    
    # 2. Possession Adjustment (PAdj)
    st.markdown(f"#### 2. Possession-Adjusted Defensive Metrics (PAdj)")
    st.write("Defenders and central midfielders playing for dominant, high-possession clubs (e.g. Mumbai City FC at 61.2% possession) have far fewer defensive opportunities than players in low-possession counter-attacking systems. We implement both the classic Colin Trainor linear formulation and our robust sigmoidal logistic model:")
    
    col_p_lin, col_p_sig = st.columns(2)
    with col_p_lin:
        st.markdown("**Colin Trainor Linear Formula:**")
        st.latex(r"\text{PAdj}_{\text{linear}} = M_{\text{raw}} \times \left( \frac{50}{100 - \text{Possession}_{\text{team}}} \right)")
        st.caption("Scales defensive intervention rate relative to an exact 50% possession league baseline.")
        
    with col_p_sig:
        st.markdown("**Sigmoidal Logistic Model (Anti-Asymptote):**")
        st.latex(r"\text{PAdj}_{\text{sigmoid}} = M_{\text{raw}} \times \frac{2}{1 + e^{-k \cdot (50 - \text{Possession}_{\text{opp}})}}")
        st.caption("Where $k = 0.08$. Dampens extreme distortions at possession extremes (< 35% or > 65%).")

    st.divider()

    # 3. Positional Percentile Rank
    st.markdown(f"#### 3. Empirical Cumulative Distribution Function (CDF) Percentile Ranking")
    st.write("To prevent distributional assumptions (such as normality) from skewing skewed football stats, percentiles are calculated via the empirical mid-point rank within the player's specific position cohort:")
    st.latex(r"\text{Percentile}(x) = \left( \frac{\sum_{i=1}^N \mathbb{I}(X_i < x) + 0.5 \sum_{i=1}^N \mathbb{I}(X_i = x)}{N} \right) \times 100")
    st.write("For inverse metrics where lower values represent superior performance (e.g. Turnovers/90, Dispossessed/90, Errors Leading to Shot, Offsides/90), the percentile is inverted:")
    st.latex(r"\text{Percentile}_{\text{inverted}}(x) = 100 - \text{Percentile}(x)")

    st.divider()

    # 4. Standard Score (Z-Score)
    st.markdown(f"#### 4. Standard Score (Z-Score)")
    st.write("Quantifies the number of standard deviations a player's performance sits above or below the positional mean:")
    st.latex(r"z = \frac{x - \mu}{\sigma}, \quad \mu = \frac{1}{N}\sum_{i=1}^N x_i, \quad \sigma = \sqrt{\frac{1}{N-1}\sum_{i=1}^N (x_i - \mu)^2}")

    st.divider()

    # 5. Advanced Expected Metrics (PSxG +/- and Shot Quality)
    st.markdown("#### 5. Shot-Stopping Post-Shot Expected Goals Delta ($\\text{PSxG}+/-$)")
    st.write("Measures the true shot-stopping ability of a goalkeeper by calculating the difference between the post-shot quality of attempts on target and the actual goals conceded:")
    st.latex(r"\text{PSxG}+/-_{p90} = \text{PSxG Faced}_{p90} - \text{Goals Conceded}_{p90}")
    st.caption("A positive $\\text{PSxG}+/-$ indicates the goalkeeper prevented more goals than an average goalkeeper would have conceded from identical trajectory strikes.")

    st.markdown("#### 6. Shot Quality ($\\text{npxG per Shot}$) & Conversion Rate")
    st.latex(r"\text{Shot Quality} = \frac{\text{npxG}}{\text{Non-Penalty Shots}}, \quad \text{Conversion Rate \%} = \left(\frac{\text{Goals}}{\text{Total Shots}}\right) \times 100")

    st.markdown("#### 7. Press Resistance & Under-Pressure Pass Completion")
    st.latex(r"\text{Press Resistance \%} = \left( \frac{\text{Successful Possessions Under Pressure}}{\text{Total Pressured Involvements}} \right) \times 100")

with doc_tab3:
    st.markdown(
        f"""
        <div style="background:{PALETTE['white']}; border:1px solid {PALETTE['border']}; border-radius:12px; padding:18px; margin-bottom:16px;">
            <h4 style="color:{PALETTE['primary']}; margin-top:0;">Complete Data Dictionary (65 KPIs)</h4>
            <p style="color:{PALETTE['text_muted']}; font-size:0.85rem; margin-bottom:0;">
                Full catalogue of all key performance indicators across the 6 ISL position groups and 4 analytical pillars.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    dict_rows = []
    for pos, pillars in POSITION_KPIS.items():
        for pillar, kpis in pillars.items():
            for k in kpis:
                dict_rows.append({
                    "Position Group": pos,
                    "Pillar": pillar,
                    "KPI Metric": k["label"],
                    "Column Name": k["col"],
                    "Unit": k["unit"],
                    "Direction": "Higher is Better" if k["higher_better"] else "Lower is Better (Inverted)",
                    "Analytical Definition": k["desc"]
                })
                
    df_dict = pd.DataFrame(dict_rows)
    st.dataframe(df_dict, use_container_width=True, hide_index=True)
    
    csv_dict = df_dict.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data Dictionary (CSV)",
        data=csv_dict,
        file_name="isl_kpi_data_dictionary.csv",
        mime="text/csv"
    )
