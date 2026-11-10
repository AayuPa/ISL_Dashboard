"""
Positional Matrix and Quadrant Analytics for Indian Super League (ISL) Players.
Visualizes role-specific KPIs, cohort scatter quadrants, and positional leaderboards.
"""

import streamlit as st
import pandas as pd
from src.config import PALETTE, POSITION_KPIS, PILLAR_CONFIG
from src.ui_helpers import load_custom_css, render_hero_banner, render_sidebar_brand
from src.db_service import get_all_players
from src.viz_interactive import plot_quadrant_scatter, plot_leaderboard_bar

st.set_page_config(
    page_title="Positional Matrix • ISL Analytics",
    page_icon="🏆",
    layout="wide"
)

load_custom_css()
selected_season = render_sidebar_brand()

render_hero_banner(
    title=f"Positional Matrix & Quadrant Analytics ({selected_season})",
    subtitle="Role-tailored KPI evaluations, quadrant scatter distributions, and positional leaderboards.",
    badge=f"ISL {selected_season} COHORTS"
)

# Load data
df_all = get_all_players(selected_season)

# Sidebar Controls
st.sidebar.markdown(f"### ⚙️ Cohort Filters")
pos_options = list(POSITION_KPIS.keys())
selected_pos = st.sidebar.selectbox("Select Position Group", pos_options, index=0)

max_avail_mins = int(df_all["minutes"].max()) if not df_all.empty else 540
default_mins = 150 if selected_season == "2026-27" else 300
min_mins = st.sidebar.slider("Minimum Minutes Played", 0, max_avail_mins, default_mins, step=25)

all_teams = sorted(df_all["team"].unique())
selected_teams = st.sidebar.multiselect("Filter by Clubs", all_teams, default=all_teams)

# Filter cohort
cohort_df = df_all[
    (df_all["pos_group"] == selected_pos) &
    (df_all["minutes"] >= min_mins) &
    (df_all["team"].isin(selected_teams))
].copy()

st.sidebar.markdown(f"**Active Cohort:** `{len(cohort_df)}` players")

# Positional KPIs available
kpis_by_pillar = POSITION_KPIS[selected_pos]
flat_kpis = []
for pillar, kpi_list in kpis_by_pillar.items():
    for k in kpi_list:
        flat_kpis.append((k["label"], k["col"], pillar))

kpi_dict = {f"{lbl} ({pil})": col for lbl, col, pil in flat_kpis}
label_by_col = {col: lbl for lbl, col, pil in flat_kpis}

# Metric Defaults per position
default_pairs = {
    "Forwards / Strikers": ("npxg_p90", "xga_p90"),
    "Wingers / Attacking Mids": ("box_entries_p90", "key_passes_p90"),
    "Central / Holding Mids": ("progressive_passes_p90", "padj_tackles_interceptions_p90"),
    "Fullbacks / Wingbacks": ("open_play_crosses_p90", "progressive_carries_p90"),
    "Center Backs": ("line_breaking_passes_p90", "aerial_win_pct"),
    "Goalkeepers": ("psxg_minus_ga_p90", "crosses_stopped_pct")
}
def_x, def_y = default_pairs.get(selected_pos, (flat_kpis[0][1], flat_kpis[1][1] if len(flat_kpis) > 1 else flat_kpis[0][1]))

# Find labels for defaults
def_x_key = [k for k, v in kpi_dict.items() if v == def_x]
def_y_key = [k for k, v in kpi_dict.items() if v == def_y]
idx_x = list(kpi_dict.keys()).index(def_x_key[0]) if def_x_key else 0
idx_y = list(kpi_dict.keys()).index(def_y_key[0]) if def_y_key else (1 if len(kpi_dict) > 1 else 0)

# Section: Interactive Quadrant Matrix
st.markdown(
    f"""
    <div style="background:{PALETTE['white']}; border:1px solid {PALETTE['border']}; border-radius:12px; padding:20px; margin-bottom:20px;">
        <h4 style="color:{PALETTE['primary']}; margin-top:0; margin-bottom:6px;">
            Quadrant Exploration: {selected_pos}
        </h4>
        <p style="color:{PALETTE['text_muted']}; font-size:0.85rem; margin-bottom:16px;">
            Compare any two positional KPIs against the cohort median to isolate elite outliers and tactical archetypes.
        </p>
    """,
    unsafe_allow_html=True
)

q_col1, q_col2, q_col3 = st.columns([3, 3, 2])
with q_col1:
    x_selection = st.selectbox("X-Axis Metric", list(kpi_dict.keys()), index=idx_x)
    x_col = kpi_dict[x_selection]
with q_col2:
    y_selection = st.selectbox("Y-Axis Metric", list(kpi_dict.keys()), index=idx_y)
    y_col = kpi_dict[y_selection]
with q_col3:
    player_names = ["None"] + sorted(cohort_df["name"].tolist())
    highlight_p = st.selectbox("Highlight Player", player_names, index=0)
    highlight_val = highlight_p if highlight_p != "None" else None

scatter_fig = plot_quadrant_scatter(
    cohort_df,
    x_col=x_col,
    y_col=y_col,
    x_label=label_by_col.get(x_col, x_col),
    y_label=label_by_col.get(y_col, y_col),
    title=f"ISL {selected_pos} • {label_by_col.get(x_col, x_col)} vs {label_by_col.get(y_col, y_col)}",
    highlight_player=highlight_val
)
st.plotly_chart(scatter_fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Section: Positional Leaderboards and Data Explorer
t1, t2 = st.tabs(["📊 Metric Leaderboard", "📋 Positional Cohort Data Table"])

with t1:
    lead_c1, lead_c2 = st.columns([3, 5])
    with lead_c1:
        lead_metric_key = st.selectbox("Choose Leaderboard Metric", list(kpi_dict.keys()), index=0)
        lead_col = kpi_dict[lead_metric_key]
        lead_label = label_by_col.get(lead_col, lead_col)
        top_n = st.slider("Number of Leaders", 5, 20, 10)
        
        # Display top 3 stat cards
        top_cohort = cohort_df.dropna(subset=[lead_col]).sort_values(by=lead_col, ascending=False).head(3)
        if not top_cohort.empty:
            st.markdown(f"**Top Performers:**")
            for rank, (_, row) in enumerate(top_cohort.iterrows(), 1):
                st.markdown(
                    f"""
                    <div class="metric-card" style="padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-weight:700; color:{PALETTE['primary']};">#{rank} {row['name']}</span>
                                <div style="font-size:0.75rem; color:{PALETTE['text_muted']};">{row['team']} • {row['minutes']} mins</div>
                            </div>
                            <div style="font-size:1.2rem; font-weight:800; color:{PALETTE['primary']};">
                                {row[lead_col]:.2f}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    with lead_c2:
        bar_fig = plot_leaderboard_bar(
            cohort_df,
            col=lead_col,
            label=lead_label,
            top_n=top_n,
            highlight_player=highlight_val
        )
        st.plotly_chart(bar_fig, use_container_width=True)

with t2:
    st.markdown(f"**Complete Data Matrix ({len(cohort_df)} Players)**")
    
    # Select display columns
    display_cols = ["name", "team_short", "age", "minutes", "sofascore_rating"] + [k[1] for k in flat_kpis]
    available_cols = [c for c in display_cols if c in cohort_df.columns]
    
    table_df = cohort_df[available_cols].copy()
    
    # Rename columns for presentation
    rename_map = {"name": "Player", "team_short": "Team", "age": "Age", "minutes": "Mins", "sofascore_rating": "Rating"}
    for _, col_name, _ in flat_kpis:
        if col_name in label_by_col:
            rename_map[col_name] = label_by_col[col_name]
    table_df.rename(columns=rename_map, inplace=True)
    
    st.dataframe(
        table_df.sort_values(by="Rating", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # CSV download
    csv = table_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Positional Cohort (CSV)",
        data=csv,
        file_name=f"isl_{selected_pos.replace(' ', '_').replace('/', '_').lower()}_matrix.csv",
        mime="text/csv"
    )
