"""
Deep Individual Player Profile and Scouting Report for Indian Super League (ISL) Players.
Includes mplsoccer PyPizza radar, spatial touch heatmaps, shot maps, and 4-pillar percentile evaluations.
"""

import streamlit as st
import pandas as pd
from src.config import PALETTE, POSITION_KPIS, PILLAR_CONFIG
from src.ui_helpers import load_custom_css, render_hero_banner, render_sidebar_brand
from src.db_service import get_all_players, get_player_events
from src.math_engine import get_player_percentiles_for_position, compute_pillar_scores
from src.viz_pizza import create_pizza_chart
from src.viz_pitch import plot_touch_heatmap, plot_shot_map

st.set_page_config(
    page_title="Player Profile • ISL Analytics",
    page_icon="👤",
    layout="wide"
)

load_custom_css()
selected_season = render_sidebar_brand()

df_all = get_all_players(selected_season)

# Sidebar: Player Selector
st.sidebar.markdown("### 🔍 Player Selection")
all_clubs = ["All Clubs"] + sorted(df_all["team"].unique())
sel_club = st.sidebar.selectbox("Filter by Club", all_clubs, index=0)

filtered_df = df_all if sel_club == "All Clubs" else df_all[df_all["team"] == sel_club]

# Search or select player
player_names = sorted(filtered_df["name"].unique())
sel_player_name = st.sidebar.selectbox("Select Player", player_names, index=0)

# Retrieve player data
player_row = df_all[df_all["name"] == sel_player_name].iloc[0]
pos_group = player_row["pos_group"]
sofascore_id = int(player_row["sofascore_id"])
minutes_played = int(player_row["minutes"])

# Cohort peer group for percentile calculations
cohort_df = df_all[df_all["pos_group"] == pos_group].copy()

# Compute percentiles & pillar composite scores
player_percentiles = get_player_percentiles_for_position(player_row, cohort_df, pos_group)
pillar_scores = compute_pillar_scores(player_percentiles)

# Player Hero Banner
render_hero_banner(
    title=f"{player_row['name']} • {player_row['team_short']}",
    subtitle=f"{pos_group} • {player_row['secondary_pos']} | {player_row['age']} yrs | {player_row['nationality']} | Preferred Foot: {player_row['preferred_foot']}",
    badge=f"SOFASCORE ID: {sofascore_id}"
)

# Bio & Match Volume Metrics
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Sofascore Rating</div>
            <div class="metric-value">{player_row['sofascore_rating']:.2f}</div>
            <div class="metric-subtext">Season Average</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with b2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Minutes Played</div>
            <div class="metric-value">{minutes_played:,}</div>
            <div class="metric-subtext">{int(player_row['appearances'])} Apps ({int(player_row['starts'])} Starts)</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with b3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Market Valuation</div>
            <div class="metric-value" style="font-size:1.35rem;">{player_row['market_value']}</div>
            <div class="metric-subtext">Estimated Value</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with b4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Distance / 90</div>
            <div class="metric-value">{player_row['distance_covered_p90']:.1f} <span style="font-size:0.9rem;">km</span></div>
            <div class="metric-subtext">Top Speed: {player_row['peak_velocity_kmh']:.1f} km/h</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with b5:
    disc_text = f"{int(player_row['yellow_cards'])} Yellow | {int(player_row['red_cards'])} Red"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Discipline & Fouls</div>
            <div class="metric-value" style="font-size:1.25rem;">{disc_text}</div>
            <div class="metric-subtext">{player_row['fouls_committed_p90']:.2f} Fouls Committed/90</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 4 Pillars Executive Summary
st.markdown(f"#### 🏆 4-Pillar Positional Evaluation (Percentile Index vs {pos_group})")
p1, p2, p3, p4 = st.columns(4)

pillar_list = ["Attacking & Threat", "Creativity & Progression", "Defensive & Duels", "Possession & Efficiency"]
pillar_cols = [p1, p2, p3, p4]

for col, pillar in zip(pillar_cols, pillar_list):
    p_info = PILLAR_CONFIG[pillar]
    score = pillar_scores.get(pillar, 50.0)
    with col:
        st.markdown(
            f"""
            <div class="pillar-card" style="border-top-color:{p_info['color']};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:{p_info['color']};">{p_info['icon']} {pillar}</span>
                    <span style="font-size:1.35rem; font-weight:800; color:{p_info['color']};">{score:.0f}<span style="font-size:0.8rem; font-weight:400;">/100</span></span>
                </div>
                <div style="font-size:0.75rem; color:{PALETTE['text_muted']}; margin-top:4px;">
                    {p_info['desc']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.write("")

# Main Scouting Visualization Tabs
tab_radar, tab_pitch, tab_metrics = st.tabs([
    "🍕 mplsoccer PyPizza Radar",
    "🏟️ Pitch Touch & Shot Maps",
    "📋 Complete KPI Metrics Table"
])

with tab_radar:
    col_rad_left, col_rad_right = st.columns([5, 3])
    
    with col_rad_left:
        fig_pizza = create_pizza_chart(
            player_name=player_row["name"],
            team_name=player_row["team_short"],
            pos_group=pos_group,
            player_percentiles=player_percentiles,
            minutes=minutes_played,
            sofascore_rating=player_row["sofascore_rating"]
        )
        st.pyplot(fig_pizza, use_container_width=True)
        
    with col_rad_right:
        st.markdown(
            f"""
            <div style="background:{PALETTE['white']}; border:1px solid {PALETTE['border']}; border-radius:12px; padding:18px; margin-top:10px;">
                <h4 style="color:{PALETTE['primary']}; margin-top:0; margin-bottom:8px;">
                    Positional Percentile Index
                </h4>
                <p style="font-size:0.85rem; color:{PALETTE['text_muted']}; line-height:1.45;">
                    Values represent the player's empirical percentile rank (1-99) benchmarked against all <b>{len(cohort_df)} {pos_group}</b> in the Indian Super League.
                </p>
            """,
            unsafe_allow_html=True
        )
        
        # Highlight top 3 and bottom 3 strengths/weaknesses
        all_metrics_flat = []
        for pil, kpis in player_percentiles.items():
            for k_col, k_data in kpis.items():
                all_metrics_flat.append((k_data["label"], k_data["pct"], k_data["raw"], k_data["unit"], pil))
                
        sorted_by_pct = sorted(all_metrics_flat, key=lambda x: x[1], reverse=True)
        
        st.markdown(f"<span style='font-weight:700; color:{PALETTE['primary']};'>🌟 Elite Strengths (>= 75th %ile):</span>", unsafe_allow_html=True)
        top_strengths = [m for m in sorted_by_pct if m[1] >= 75][:4]
        if top_strengths:
            for lbl, pct, raw, unit, _ in top_strengths:
                st.markdown(f"- **{lbl}**: `{raw:.2f} {unit}` (**{pct:.0f}th** percentile)")
        else:
            st.markdown(f"- *Balanced output across standard metrics.*")
            
        st.markdown(f"<span style='font-weight:700; color:{PALETTE['secondary']}; margin-top:10px; display:inline-block;'>⚠️ Development Areas (< 40th %ile):</span>", unsafe_allow_html=True)
        bottom_areas = [m for m in sorted_by_pct if m[1] < 40][-4:]
        if bottom_areas:
            for lbl, pct, raw, unit, _ in bottom_areas:
                st.markdown(f"- **{lbl}**: `{raw:.2f} {unit}` (**{pct:.0f}th** percentile)")
        else:
            st.markdown(f"- *Above-average across positional requirements.*")
            
        st.markdown("</div>", unsafe_allow_html=True)

with tab_pitch:
    # Fetch player spatial events from DuckDB
    events_data = get_player_events(sofascore_id)
    touches_x = events_data.get("touches_x", [])
    touches_y = events_data.get("touches_y", [])
    shots = events_data.get("shots", [])
    
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.markdown(f"**Spatial Touch Density Heatmap (Kernel Density Estimate)**")
        fig_heat = plot_touch_heatmap(
            touches_x=touches_x,
            touches_y=touches_y,
            player_name=player_row["name"],
            pos_group=pos_group
        )
        st.pyplot(fig_heat, use_container_width=True)
        st.caption(f"Spatial coordinates aggregated from {len(touches_x)} match touches across open-play actions.")
        
    with col_p2:
        st.markdown(f"**Shot Trajectory & Location Map**")
        fig_shots = plot_shot_map(
            shots=shots,
            player_name=player_row["name"],
            goals=player_row.get("goals", None),
            npxg=player_row.get("npxg", None)
        )
        st.pyplot(fig_shots, use_container_width=True)
        st.caption("Shot circle size corresponds to expected goal (xG) probability from the attempt location.")

with tab_metrics:
    st.markdown(f"#### Complete Positional KPI Breakdown")
    
    # Render table of all KPIs with raw value, unit, percentile, and cohort median
    rows = []
    for pillar, kpis in player_percentiles.items():
        for k_col, data in kpis.items():
            median_val = cohort_df[k_col].median() if k_col in cohort_df.columns else np.nan
            rows.append({
                "Pillar": pillar,
                "KPI Label": data["label"],
                "Player Value": f"{data['raw']:.2f} {data['unit']}" if not pd.isna(data['raw']) else "—",
                "ISL Cohort Median": f"{median_val:.2f} {data['unit']}" if not pd.isna(median_val) else "—",
                "Percentile Rank": f"{data['pct']:.0f}%",
                "Z-Score": f"{data['z']:+.2f}",
                "Description": data["desc"]
            })
            
    df_profile_kpis = pd.DataFrame(rows)
    st.dataframe(df_profile_kpis, use_container_width=True, hide_index=True)
