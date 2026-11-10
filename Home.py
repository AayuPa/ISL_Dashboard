"""
Indian Super League (ISL) Player Analytics Platform
Main Entrypoint and Executive League Dashboard.
"""

import streamlit as st
import pandas as pd
from src.config import PALETTE, ISL_CLUBS, POSITION_KPIS, PILLAR_CONFIG
from src.ui_helpers import load_custom_css, render_hero_banner, render_sidebar_brand
from src.db_service import get_all_players, get_teams

st.set_page_config(
    page_title="ISL Player Intelligence Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_custom_css()
selected_season = render_sidebar_brand()

# Hero Banner
render_hero_banner(
    title=f"Indian Super League • {selected_season} Season Intelligence",
    subtitle=f"Dynamic scouting, tactical evaluation, possession-adjusted metrics (PAdj), and positional percentiles powered by DuckDB, mplsoccer, and Sofascore ISL data.",
    badge=f"ISL {selected_season} OFFICIAL FEED"
)

# Load data for selected season
df_players = get_all_players(selected_season)
df_teams = get_teams(selected_season)

# Top Executive KPI Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Active Players Tracked</div>
            <div class="metric-value">{len(df_players)}</div>
            <div class="metric-subtext">All 13 ISL Franchises</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with c2:
    top_scorer = df_players.sort_values(by="goals", ascending=False).iloc[0]
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Golden Boot Leader</div>
            <div class="metric-value" style="font-size:1.35rem;">{top_scorer['name']}</div>
            <div class="metric-subtext">{int(top_scorer['goals'])} Goals • {top_scorer['team_short']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with c3:
    top_rating = df_players.sort_values(by="sofascore_rating", ascending=False).iloc[0]
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Highest Sofascore Rating</div>
            <div class="metric-value">{top_rating['sofascore_rating']:.2f}</div>
            <div class="metric-subtext">{top_rating['name']} • {top_rating['team_short']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with c4:
    total_mins = int(df_players["minutes"].sum())
    max_played = int(df_teams["played"].max())
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Minutes Analyzed</div>
            <div class="metric-value">{total_mins:,}</div>
            <div class="metric-subtext">{max_played} Matchweeks ({selected_season})</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# Navigation & Positional Architecture Tabs
tab_overview, tab_standings, tab_pillars = st.tabs([
    "🎯 Positional Groups & Pillars",
    "📊 League Standings & Possession",
    "⭐ Top Performers by Pillar"
])

with tab_overview:
    st.markdown(
        f"""
        <div style="margin-bottom: 16px;">
            <h3 style="color:{PALETTE['primary']}; margin-bottom:4px; font-weight:700;">
                Position Group Analytics Matrix
            </h3>
            <p style="color:{PALETTE['text_muted']}; font-size:0.9rem; margin-top:0;">
                Every position group is evaluated against tailored, role-specific metrics grouped into 4 football pillars.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_left, col_right = st.columns(2)
    positions = list(POSITION_KPIS.keys())
    
    for idx, pos in enumerate(positions):
        col = col_left if idx % 2 == 0 else col_right
        p_count = len(df_players[df_players["pos_group"] == pos])
        
        with col:
            st.markdown(
                f"""
                <div class="pillar-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:1.05rem; font-weight:700; color:{PALETTE['primary']};">{pos}</span>
                        <span class="badge-pill badge-primary">{p_count} Players</span>
                    </div>
                    <div style="font-size:0.82rem; color:{PALETTE['text_dark']}; line-height:1.5;">
                        <span style="font-weight:700; color:{PALETTE['primary']};">⚡ Attacking:</span> {', '.join([k['label'] for k in POSITION_KPIS[pos]['Attacking & Threat']]) if POSITION_KPIS[pos]['Attacking & Threat'] else '—'}<br>
                        <span style="font-weight:700; color:{PALETTE['secondary']};">🪄 Creativity:</span> {', '.join([k['label'] for k in POSITION_KPIS[pos]['Creativity & Progression']])}<br>
                        <span style="font-weight:700; color:{PALETTE['tertiary']};">🛡️ Defensive:</span> {', '.join([k['label'] for k in POSITION_KPIS[pos]['Defensive & Duels']])}<br>
                        <span style="font-weight:700; color:{PALETTE['primary']};">🎯 Possession:</span> {', '.join([k['label'] for k in POSITION_KPIS[pos]['Possession & Efficiency']])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

with tab_standings:
    st.markdown(
        f"""
        <h4 style="color:{PALETTE['primary']}; margin-bottom:8px;">
            ISL Table & Tactical Possession Benchmarks
        </h4>
        <p style="color:{PALETTE['text_muted']}; font-size:0.85rem; margin-top:0;">
            Team average possession percentage is utilized for all Possession-Adjusted (PAdj) defensive metrics.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # Format standings
    standings_display = df_teams[[
        "team", "played", "won", "draw", "lost", "gf", "ga", "pts", "poss_pct"
    ]].copy()
    standings_display.columns = [
        "Club", "Pld", "W", "D", "L", "GF", "GA", "Pts", "Possession %"
    ]
    standings_display["GD"] = standings_display["GF"] - standings_display["GA"]
    standings_display = standings_display[[
        "Club", "Pld", "W", "D", "L", "GF", "GA", "GD", "Pts", "Possession %"
    ]]
    
    st.dataframe(
        standings_display,
        use_container_width=True,
        hide_index=True
    )

with tab_pillars:
    p_c1, p_c2, p_c3, p_c4 = st.columns(4)
    
    with p_c1:
        st.markdown(f"**⚡ Attacking & Threat**")
        top_np = df_players.dropna(subset=["npxg_p90"]).sort_values(by="npxg_p90", ascending=False).head(5)
        for _, r in top_np.iterrows():
            st.markdown(f"- **{r['name']}** ({r['team_short']}): `{r['npxg_p90']:.2f}` npxG/90")
            
    with p_c2:
        st.markdown(f"**🪄 Creativity & Progression**")
        top_sca = df_players.dropna(subset=["key_passes_p90"]).sort_values(by="key_passes_p90", ascending=False).head(5)
        for _, r in top_sca.iterrows():
            st.markdown(f"- **{r['name']}** ({r['team_short']}): `{r['key_passes_p90']:.2f}` Key Pass/90")
            
    with p_c3:
        st.markdown(f"**🛡️ Defensive & Duels**")
        top_rec = df_players.dropna(subset=["padj_tackles_interceptions_p90"]).sort_values(by="padj_tackles_interceptions_p90", ascending=False).head(5)
        for _, r in top_rec.iterrows():
            st.markdown(f"- **{r['name']}** ({r['team_short']}): `{r['padj_tackles_interceptions_p90']:.2f}` PAdj T+I/90")
            
    with p_c4:
        st.markdown(f"**🎯 Possession & Efficiency**")
        top_press = df_players.dropna(subset=["press_resistance_pct"]).sort_values(by="press_resistance_pct", ascending=False).head(5)
        for _, r in top_press.iterrows():
            st.markdown(f"- **{r['name']}** ({r['team_short']}): `{r['press_resistance_pct']:.1f}%` Retention")

st.divider()

# Footer quick guide
st.markdown(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:center; color:{PALETTE['text_muted']}; font-size:0.8rem; padding:8px 0;">
        <div><b>Indian Super League Player Analytics Platform</b> • DuckDB + mplsoccer + Plotly + Streamlit</div>
        <div>Data source: Sofascore Official Stats Feed • Warm Mocha Palette Aesthetics</div>
    </div>
    """,
    unsafe_allow_html=True
)
