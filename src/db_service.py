"""
DuckDB Analytical Storage Service for Indian Super League (ISL) Platform
Manages fast read-only analytical queries, table schemas, and event retrieval for 2026/2027 season.
"""

import duckdb
import pandas as pd
import json
import streamlit as st
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "isl_analytics.duckdb")

def get_connection():
    """Returns a read-only DuckDB connection."""
    return duckdb.connect(DB_PATH, read_only=True)

@st.cache_data(show_spinner=False)
def get_available_seasons() -> list:
    """Return active ISL seasons in database."""
    conn = get_connection()
    try:
        seasons = conn.execute("SELECT DISTINCT season FROM isl_players ORDER BY season DESC").fetchall()
        return [s[0] for s in seasons]
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def get_all_players(season: str = "2026-27") -> pd.DataFrame:
    """Fetch complete ISL 2026/27 player database."""
    conn = get_connection()
    try:
        query = "SELECT * FROM isl_players WHERE season = ? ORDER BY sofascore_rating DESC"
        df = conn.execute(query, [season]).fetchdf()
        return df
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def get_teams(season: str = "2026-27") -> pd.DataFrame:
    """Fetch ISL 2026/27 team standings and team possession benchmarks."""
    conn = get_connection()
    try:
        query = "SELECT * FROM isl_teams WHERE season = ? ORDER BY pts DESC, (gf - ga) DESC"
        df = conn.execute(query, [season]).fetchdf()
        return df
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def get_players_by_pos(pos_group: str, season: str = "2026-27", min_minutes: int = 0) -> pd.DataFrame:
    """Fetch 2026/27 players belonging to a specific position group filtered by minutes played."""
    conn = get_connection()
    try:
        query = """
            SELECT * FROM isl_players
            WHERE pos_group = ? AND season = ? AND minutes >= ?
            ORDER BY sofascore_rating DESC
        """
        df = conn.execute(query, [pos_group, season, min_minutes]).fetchdf()
        return df
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def get_player_by_id(sofascore_id) -> dict:
    """Fetch single player record by Sofascore ID."""
    conn = get_connection()
    try:
        sid = int(sofascore_id)
        df = conn.execute("SELECT * FROM isl_players WHERE sofascore_id = ?", [sid]).fetchdf()
        if not df.empty:
            return df.iloc[0].to_dict()
        return {}
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def get_player_events(sofascore_id) -> dict:
    """Fetch touch coordinates and shot events for a player."""
    conn = get_connection()
    try:
        sid = int(sofascore_id)
        row = conn.execute("SELECT touches_x, touches_y, shots_json FROM isl_player_events WHERE sofascore_id = ?", [sid]).fetchone()
        if not row:
            return {"touches_x": [], "touches_y": [], "shots": []}
        
        touches_x = json.loads(row[0]) if isinstance(row[0], str) else (list(row[0]) if row[0] is not None else [])
        touches_y = json.loads(row[1]) if isinstance(row[1], str) else (list(row[1]) if row[1] is not None else [])
        shots = json.loads(row[2]) if isinstance(row[2], str) else (list(row[2]) if row[2] is not None else [])
        
        return {
            "touches_x": touches_x,
            "touches_y": touches_y,
            "shots": shots
        }
    finally:
        conn.close()

def execute_custom_query(sql_query: str) -> pd.DataFrame:
    """Execute arbitrary analytical SELECT query with read-only safety checks."""
    cleaned = sql_query.strip().lower()
    forbidden = ["drop", "delete", "insert", "update", "alter", "create", "truncate", "replace"]
    for word in forbidden:
        if cleaned.startswith(word) or f" {word} " in cleaned:
            raise ValueError(f"Write operation '{word.upper()}' is forbidden in analytical read-only mode.")
    
    conn = get_connection()
    try:
        return conn.execute(sql_query).fetchdf()
    finally:
        conn.close()

@st.cache_data(show_spinner=False)
def get_db_summary() -> dict:
    """Return database metadata, tables, row counts and memory footprints."""
    conn = get_connection()
    try:
        tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
        summary = {}
        for t in tables:
            cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            cols = [c[0] for c in conn.execute(f"DESCRIBE {t}").fetchall()]
            summary[t] = {"count": cnt, "columns": cols}
        return summary
    finally:
        conn.close()
