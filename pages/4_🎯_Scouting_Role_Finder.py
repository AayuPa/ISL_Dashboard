"""
Tactical Scouting & Role Finder for Indian Super League (ISL) Players.
Ranks players against tactical archetypes using customizable weighted KPI models.
"""

import streamlit as st
import pandas as pd
from src.config import PALETTE, TACTICAL_ARCHETYPES, POSITION_KPIS
from src.ui_helpers import load_custom_css, render_hero_banner, render_sidebar_brand
from src.db_service import get_all_players
from src.math_engine import compute_archetype_fit

st.set_page_config(
    page_title="Scouting Role Finder • ISL Analytics",
    page_icon="🎯",
    layout="wide"
)

load_custom_css()
selected_season = render_sidebar_brand()

render_hero_banner(
    title=f"Tactical Scouting & Role Finder ({selected_season})",
    subtitle="Identify recruitment targets and tactical fits using multi-criteria weighted percentile models.",
    badge=f"ISL {selected_season} SCOUT ENGINE"
)

df_all = get_all_players(selected_season)

# Archetype selection
st.sidebar.markdown("### 🎯 Tactical Archetype")
archetype_names = list(TACTICAL_ARCHETYPES.keys())
sel_arch_name = st.sidebar.selectbox("Choose Archetype Profile", archetype_names, index=0)
arch_info = TACTICAL_ARCHETYPES[sel_arch_name]
target_pos = arch_info["pos"]

st.sidebar.markdown(f"**Target Position:** `{target_pos}`")
st.sidebar.markdown(f"*{arch_info['desc']}*")

max_avail = int(df_all["minutes"].max()) if not df_all.empty else 540
def_mins = 150 if selected_season == "2026-27" else 300
min_mins = st.sidebar.slider("Minimum Minutes", 0, max_avail, def_mins, step=25)

# Cohort
cohort_df = df_all[
    (df_all["pos_group"] == target_pos) &
    (df_all["minutes"] >= min_mins)
].copy()

# Weights customization
st.markdown(
    f"""
    <div style="background:{PALETTE['white']}; border:1px solid {PALETTE['border']}; border-radius:12px; padding:18px; margin-bottom:18px;">
        <h4 style="color:{PALETTE['primary']}; margin-top:0; margin-bottom:6px;">
            Target Profile: {sel_arch_name}
        </h4>
        <p style="color:{PALETTE['text_muted']}; font-size:0.85rem; margin-bottom:12px;">
            {arch_info['desc']} Adjust metric weights below to tailor the model to your tactical system.
        </p>
    """,
    unsafe_allow_html=True
)

weights = {}
weight_cols = st.columns(len(arch_info["weights"]))

for idx, (col_name, def_w) in enumerate(arch_info["weights"].items()):
    with weight_cols[idx]:
        # Find clean label
        label = col_name.replace("_p90", "/90").replace("_pct", " %").replace("_", " ").title()
        weights[col_name] = st.slider(label, 0.0, 1.0, float(def_w), step=0.05)

st.markdown("</div>", unsafe_allow_html=True)

# Compute fit scores
if not cohort_df.empty:
    fit_scores = []
    for _, row in cohort_df.iterrows():
        score = compute_archetype_fit(row, cohort_df, weights)
        fit_scores.append(score)
    cohort_df["archetype_fit_score"] = fit_scores
    ranked_df = cohort_df.sort_values(by="archetype_fit_score", ascending=False).reset_index(drop=True)
else:
    ranked_df = pd.DataFrame()

# Display Top Candidate Cards
st.markdown(f"#### 🏆 Top Ranked Targets ({len(ranked_df)} Eligible Candidates)")

if not ranked_df.empty:
    top_3 = ranked_df.head(3)
    top_cols = st.columns(3)
    
    for idx, (_, row) in enumerate(top_3.iterrows()):
        with top_cols[idx]:
            medals = ["🥇 Best Fit", "🥈 Second Choice", "🥉 Third Choice"]
            st.markdown(
                f"""
                <div class="pillar-card" style="border-top-color:{PALETTE['primary']};">
                    <span class="badge-pill badge-primary">{medals[idx]}</span>
                    <div style="font-size:1.35rem; font-weight:800; color:{PALETTE['primary']}; margin-top:6px;">{row['name']}</div>
                    <div style="font-size:0.85rem; color:{PALETTE['text_muted']};">{row['team']} • {row['secondary_pos']}</div>
                    <div style="margin:12px 0 6px 0; display:flex; justify-content:space-between; align-items:flex-end;">
                        <div>
                            <div style="font-size:0.75rem; color:{PALETTE['text_muted']};">ROLE FIT SCORE</div>
                            <div style="font-size:1.8rem; font-weight:800; color:{PALETTE['primary']};">{row['archetype_fit_score']:.1f}<span style="font-size:0.9rem;">/100</span></div>
                        </div>
                        <div style="text-align:right; font-size:0.82rem; color:{PALETTE['text_dark']};">
                            <b>Rating:</b> {row['sofascore_rating']:.2f}<br>
                            <b>Mins:</b> {int(row['minutes']):,}<br>
                            <b>Value:</b> {row['market_value']}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    # Full Ranked Table
    st.markdown("#### Complete Scouting Shortlist")
    
    disp_cols = ["archetype_fit_score", "name", "team_short", "age", "minutes", "market_value", "sofascore_rating"] + list(weights.keys())
    shortlist_table = ranked_df[disp_cols].copy()
    shortlist_table.columns = ["Fit Score", "Player", "Team", "Age", "Minutes", "Market Value", "Sofascore"] + [c.replace("_p90", "/90").replace("_", " ").title() for c in weights.keys()]
    
    st.dataframe(
        shortlist_table,
        use_container_width=True,
        hide_index=True
    )
    
    # Export shortlist
    csv_data = shortlist_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Tactical Shortlist (CSV)",
        data=csv_data,
        file_name=f"isl_scout_{sel_arch_name.lower().replace(' ', '_').replace('/', '_')}.csv",
        mime="text/csv"
    )
else:
    st.warning("No players meet the minimum minutes threshold for this position.")
