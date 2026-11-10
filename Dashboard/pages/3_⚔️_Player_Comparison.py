"""
Head-to-Head Player Comparison for Indian Super League (ISL) Players.
Visualizes overlaid PyPizza radars, 4-pillar score comparisons, and delta tables.
"""

import streamlit as st
import pandas as pd
import numpy as np
from src.config import PALETTE, POSITION_KPIS, PILLAR_CONFIG
from src.ui_helpers import load_custom_css, render_hero_banner, render_sidebar_brand
from src.db_service import get_all_players
from src.math_engine import get_player_percentiles_for_position, compute_pillar_scores
from src.viz_pizza import create_comparison_radar
from src.viz_interactive import plot_comparison_pillars_bar

st.set_page_config(
    page_title="Player Comparison • ISL Analytics",
    page_icon="⚔️",
    layout="wide"
)

load_custom_css()
selected_season = render_sidebar_brand()

render_hero_banner(
    title=f"Head-to-Head Player Comparison ({selected_season})",
    subtitle="Direct statistical benchmark, overlaid radar profiles, and analytical delta evaluation.",
    badge=f"ISL {selected_season} SCOUT BENCHMARK"
)

df_all = get_all_players(selected_season)

# Select Position first to compare within the same KPI domain
st.sidebar.markdown("### ⚙️ Comparison Setup")
pos_options = list(POSITION_KPIS.keys())
sel_pos = st.sidebar.selectbox("Position Cohort", pos_options, index=0)

cohort_df = df_all[df_all["pos_group"] == sel_pos].copy()
player_list = sorted(cohort_df["name"].unique())

c_sel1, c_sel2 = st.columns(2)
with c_sel1:
    p1_name = st.selectbox("Select Player 1 (Primary - Roasted Chestnut)", player_list, index=0)
with c_sel2:
    def_idx2 = 1 if len(player_list) > 1 else 0
    p2_name = st.selectbox("Select Player 2 (Benchmark - Warm Tan)", player_list, index=def_idx2)

if p1_name == p2_name:
    st.info("Select two different players to generate a comparative analysis.")

p1_row = cohort_df[cohort_df["name"] == p1_name].iloc[0]
p2_row = cohort_df[cohort_df["name"] == p2_name].iloc[0]

# Calculate percentiles and pillar scores
p1_pcts = get_player_percentiles_for_position(p1_row, cohort_df, sel_pos)
p2_pcts = get_player_percentiles_for_position(p2_row, cohort_df, sel_pos)

p1_pillars = compute_pillar_scores(p1_pcts)
p2_pillars = compute_pillar_scores(p2_pcts)

# Side-by-Side Bio Summary Cards
b1, b2 = st.columns(2)
with b1:
    st.markdown(
        f"""
        <div class="pillar-card" style="border-top-color:{PALETTE['primary']};">
            <div style="font-size:1.25rem; font-weight:800; color:{PALETTE['primary']};">{p1_row['name']}</div>
            <div style="font-size:0.85rem; color:{PALETTE['text_muted']};">{p1_row['team']} • {p1_row['secondary_pos']}</div>
            <div style="margin-top:10px; font-size:0.85rem;">
                <b>Sofascore Rating:</b> {p1_row['sofascore_rating']:.2f} | <b>Minutes:</b> {int(p1_row['minutes']):,} | <b>Age:</b> {int(p1_row['age'])} yrs
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
with b2:
    st.markdown(
        f"""
        <div class="pillar-card" style="border-top-color:{PALETTE['tertiary']};">
            <div style="font-size:1.25rem; font-weight:800; color:{PALETTE['secondary']};">{p2_row['name']}</div>
            <div style="font-size:0.85rem; color:{PALETTE['text_muted']};">{p2_row['team']} • {p2_row['secondary_pos']}</div>
            <div style="margin-top:10px; font-size:0.85rem;">
                <b>Sofascore Rating:</b> {p2_row['sofascore_rating']:.2f} | <b>Minutes:</b> {int(p2_row['minutes']):,} | <b>Age:</b> {int(p2_row['age'])} yrs
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Visual Comparison Tabs
tab_radar, tab_pillars_chart, tab_delta_table = st.tabs([
    "🍕 Overlaid PyPizza Radar",
    "📊 4-Pillar Score Bar Chart",
    "📋 KPI Metric Delta Matrix"
])

with tab_radar:
    # Prepare parameter lists and percentile values
    params = []
    p1_vals = []
    p2_vals = []
    
    for pillar in ["Attacking & Threat", "Creativity & Progression", "Defensive & Duels", "Possession & Efficiency"]:
        kpis1 = p1_pcts.get(pillar, {})
        kpis2 = p2_pcts.get(pillar, {})
        for col, data1 in kpis1.items():
            data2 = kpis2.get(col, {"pct": 50.0})
            clean_lbl = data1["label"].replace(" / 90", "").replace(" (Shot Quality)", "").replace(" (Shot-Stopping)", "")
            clean_lbl = clean_lbl.replace("Pass Comp % under Pressure", "Pass % vs Press").replace("Pass Comp % under High Press", "Press Pass %")
            params.append(clean_lbl)
            p1_vals.append(int(round(data1["pct"])))
            p2_vals.append(int(round(data2["pct"])))
            
    fig_comp = create_comparison_radar(
        p1_name=p1_name,
        p1_vals=p1_vals,
        p2_name=p2_name,
        p2_vals=p2_vals,
        params=params,
        pos_group=sel_pos
    )
    st.pyplot(fig_comp, use_container_width=True)

with tab_pillars_chart:
    fig_bar = plot_comparison_pillars_bar(
        p1_name=p1_name,
        p1_scores=p1_pillars,
        p2_name=p2_name,
        p2_scores=p2_pillars
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_delta_table:
    st.markdown(f"#### Complete KPI Delta Evaluation")
    
    delta_rows = []
    for pillar in ["Attacking & Threat", "Creativity & Progression", "Defensive & Duels", "Possession & Efficiency"]:
        kpis1 = p1_pcts.get(pillar, {})
        kpis2 = p2_pcts.get(pillar, {})
        for col, data1 in kpis1.items():
            data2 = kpis2.get(col, {"raw": np.nan, "pct": 50.0})
            
            raw1 = data1["raw"]
            raw2 = data2["raw"]
            delta_raw = raw1 - raw2 if (not pd.isna(raw1) and not pd.isna(raw2)) else np.nan
            pct1 = data1["pct"]
            pct2 = data2["pct"]
            delta_pct = pct1 - pct2
            
            edge = p1_name if delta_pct > 0 else (p2_name if delta_pct < 0 else "Tied")
            
            delta_rows.append({
                "Pillar": pillar,
                "KPI": data1["label"],
                f"{p1_name} (Raw)": f"{raw1:.2f} {data1['unit']}" if not pd.isna(raw1) else "—",
                f"{p1_name} (%ile)": f"{pct1:.0f}%",
                f"{p2_name} (Raw)": f"{raw2:.2f} {data1['unit']}" if not pd.isna(raw2) else "—",
                f"{p2_name} (%ile)": f"{pct2:.0f}%",
                "Delta (%ile)": f"{delta_pct:+.0f}%",
                "Statistical Edge": edge
            })
            
    df_delta = pd.DataFrame(delta_rows)
    st.dataframe(df_delta, use_container_width=True, hide_index=True)
