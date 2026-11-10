"""
DuckDB Analytical Storage & Interactive SQL Console for Indian Super League (ISL) Data.
Enables instant SQL querying, schema introspection, and data pipeline verification.
"""

import streamlit as st
import pandas as pd
import time
from src.config import PALETTE
from src.ui_helpers import load_custom_css, render_hero_banner, render_sidebar_brand
from src.db_service import get_db_summary, execute_custom_query, get_connection

st.set_page_config(
    page_title="DuckDB Store • ISL Analytics",
    page_icon="💾",
    layout="wide"
)

load_custom_css()
render_sidebar_brand()

render_hero_banner(
    title="Local Analytical Storage • DuckDB Engine",
    subtitle="Embedded columnar OLAP database providing sub-millisecond query execution on official Sofascore ISL data.",
    badge="DUCKDB OLAP ENGINE"
)

summary = get_db_summary()

# Top Storage Metrics
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">DuckDB Tables</div>
            <div class="metric-value">{len(summary)}</div>
            <div class="metric-subtext">isl_players, isl_teams, isl_player_events</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with s2:
    total_records = sum([info["count"] for info in summary.values()])
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Indexed Entities</div>
            <div class="metric-value">{total_records:,}</div>
            <div class="metric-subtext">Players, Events & Standings</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with s3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Storage Engine Type</div>
            <div class="metric-value" style="font-size:1.35rem;">DuckDB Columnar</div>
            <div class="metric-subtext">Zero-Copy In-Memory Vectorized</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

tab_sql, tab_tables = st.tabs(["⚡ Live SQL Workbench", "📋 Schema & Table Explorer"])

# Pre-packaged SQL Templates
SQL_TEMPLATES = {
    "1. 2026-27 Season: Top Forwards by Goals & npxG": """
SELECT 
    name, 
    team_short, 
    season,
    minutes, 
    goals, 
    goals_p90, 
    npxg,
    npxg_p90, 
    conversion_rate_pct,
    sofascore_rating
FROM isl_players 
WHERE season = '2026-27' AND pos_group = 'Forwards / Strikers'
ORDER BY goals DESC, npxg_p90 DESC 
LIMIT 10;
""",
    "2. 2026-27 Standings: Points & Possession": """
SELECT 
    team, 
    short, 
    season,
    played, 
    won, 
    draw, 
    lost, 
    gf, 
    ga, 
    pts, 
    poss_pct
FROM isl_teams 
WHERE season = '2026-27'
ORDER BY pts DESC, (gf - ga) DESC;
""",
    "3. 2026-27 Midfield PAdj Tackles + Interceptions": """
SELECT 
    name, 
    team_short, 
    minutes, 
    padj_tackles_interceptions_p90, 
    ball_recoveries_p90, 
    duel_win_pct, 
    press_resistance_pct
FROM isl_players 
WHERE season = '2026-27' AND pos_group = 'Central / Holding Mids'
ORDER BY padj_tackles_interceptions_p90 DESC 
LIMIT 10;
""",
    "4. 2026-27 Goalkeepers Shot-Stopping (PSxG +/-)": """
SELECT 
    name, 
    team_short, 
    minutes, 
    psxg_minus_ga_p90, 
    save_pct, 
    crosses_stopped_pct, 
    clean_sheet_pct
FROM isl_players 
WHERE season = '2026-27' AND pos_group = 'Goalkeepers'
ORDER BY psxg_minus_ga_p90 DESC 
LIMIT 10;
""",
    "5. East Bengal FC (Defending Champions) Squad Roster": """
SELECT 
    name,
    pos_group,
    age,
    minutes,
    sofascore_rating,
    market_value
FROM isl_players 
WHERE team = 'East Bengal FC'
ORDER BY sofascore_rating DESC;
"""
}

with tab_sql:
    st.markdown(
        f"""
        <div style="background:{PALETTE['white']}; border:1px solid {PALETTE['border']}; border-radius:12px; padding:18px; margin-bottom:16px;">
            <h4 style="color:{PALETTE['primary']}; margin-top:0; margin-bottom:6px;">
                Interactive SQL Query Console
            </h4>
            <p style="color:{PALETTE['text_muted']}; font-size:0.85rem; margin-bottom:12px;">
                Execute read-only SQL queries directly against the local DuckDB database. Select an analytical query template or draft custom SQL.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    selected_template = st.selectbox("Select SQL Query Template", list(SQL_TEMPLATES.keys()), index=0)
    query_input = st.text_area("SQL Query", value=SQL_TEMPLATES[selected_template].strip(), height=150)
    
    run_btn = st.button("🚀 Execute SQL Query")
    
    if run_btn or query_input:
        try:
            start_time = time.perf_counter()
            query_df = execute_custom_query(query_input)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            st.markdown(
                f"""
                <div style="font-size:0.85rem; color:{PALETTE['text_muted']}; margin:10px 0;">
                    Returned <b>{len(query_df)}</b> rows in <b>{elapsed_ms:.2f} ms</b> via DuckDB columnar engine.
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.dataframe(query_df, use_container_width=True, hide_index=True)
            
            # Export result
            csv_res = query_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export Query Result (CSV)",
                data=csv_res,
                file_name="isl_duckdb_query_result.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

with tab_tables:
    st.markdown(f"#### DuckDB Catalog & Schemas")
    
    sel_table = st.selectbox("Inspect Table", list(summary.keys()), index=0)
    t_info = summary[sel_table]
    
    st.markdown(f"**Table:** `{sel_table}` | **Row Count:** `{t_info['count']}` | **Columns:** `{len(t_info['columns'])}`")
    
    conn = get_connection()
    try:
        preview_df = conn.execute(f"SELECT * FROM {sel_table} LIMIT 10").fetchdf()
        st.dataframe(preview_df, use_container_width=True, hide_index=True)
    finally:
        conn.close()
        
    with st.expander("View Full Column Definitions"):
        col_df = pd.DataFrame({"Column Name": t_info["columns"]})
        st.dataframe(col_df, use_container_width=True, hide_index=True)
