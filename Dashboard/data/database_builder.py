"""
ISL Analytics Database Builder and Data Ingestion Pipeline.
Populates DuckDB with complete Indian Super League SofaScore-style datasets,
including teams, player profiles, positional KPIs, tracking telemetry, and pitch coordinates.
"""

import os
import json
import duckdb
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure data directory exists
DATA_DIR = Path(__file__).resolve().parent
DB_PATH = DATA_DIR / "isl_analytics.duckdb"

CLUBS_DATA = [
    {"team": "Mohun Bagan Super Giant", "short": "MBSG", "played": 22, "won": 15, "draw": 3, "lost": 4, "gf": 47, "ga": 26, "pts": 48, "poss_pct": 58.4, "city": "Kolkata"},
    {"team": "Mumbai City FC", "short": "MCFC", "played": 22, "won": 14, "draw": 5, "lost": 3, "gf": 42, "ga": 19, "pts": 47, "poss_pct": 61.2, "city": "Mumbai"},
    {"team": "FC Goa", "short": "FCG", "played": 22, "won": 13, "draw": 6, "lost": 3, "gf": 39, "ga": 21, "pts": 45, "poss_pct": 57.8, "city": "Goa"},
    {"team": "Odisha FC", "short": "OFC", "played": 22, "won": 11, "draw": 6, "lost": 5, "gf": 35, "ga": 23, "pts": 39, "poss_pct": 53.6, "city": "Bhubaneswar"},
    {"team": "Kerala Blasters FC", "short": "KBFC", "played": 22, "won": 10, "draw": 3, "lost": 9, "gf": 32, "ga": 31, "pts": 33, "poss_pct": 51.5, "city": "Kochi"},
    {"team": "Chennaiyin FC", "short": "CFC", "played": 22, "won": 8, "draw": 3, "lost": 11, "gf": 26, "ga": 36, "pts": 27, "poss_pct": 47.2, "city": "Chennai"},
    {"team": "NorthEast United FC", "short": "NEUFC", "played": 22, "won": 6, "draw": 8, "lost": 8, "gf": 28, "ga": 32, "pts": 26, "poss_pct": 46.5, "city": "Guwahati"},
    {"team": "East Bengal FC", "short": "EBFC", "played": 22, "won": 6, "draw": 6, "lost": 10, "gf": 27, "ga": 29, "pts": 24, "poss_pct": 48.9, "city": "Kolkata"},
    {"team": "Punjab FC", "short": "PFC", "played": 22, "won": 6, "draw": 6, "lost": 10, "gf": 28, "ga": 35, "pts": 24, "poss_pct": 45.8, "city": "New Delhi / Mohali"},
    {"team": "Bengaluru FC", "short": "BFC", "played": 22, "won": 6, "draw": 4, "lost": 12, "gf": 20, "ga": 34, "pts": 22, "poss_pct": 50.1, "city": "Bengaluru"},
    {"team": "Jamshedpur FC", "short": "JFC", "played": 22, "won": 5, "draw": 6, "lost": 11, "gf": 23, "ga": 32, "pts": 21, "poss_pct": 44.2, "city": "Jamshedpur"},
    {"team": "Mohammedan SC", "short": "MSC", "played": 22, "won": 4, "draw": 6, "lost": 12, "gf": 18, "ga": 38, "pts": 18, "poss_pct": 43.1, "city": "Kolkata"},
    {"team": "Hyderabad FC", "short": "HFC", "played": 22, "won": 1, "draw": 5, "lost": 16, "gf": 10, "ga": 43, "pts": 8, "poss_pct": 41.5, "city": "Hyderabad"},
]

# Prominent ISL Core Roster definition with realistic profiles & exact KPI anchors
ROSTER_SEEDS = [
    # FORWARDS / STRIKERS
    {
        "name": "Sunil Chhetri", "team": "Bengaluru FC", "pos_group": "Forwards / Strikers", "sec_pos": "Second Striker",
        "age": 40, "foot": "Right", "nat": "India", "val": "€150k", "mins": 1420, "apps": 21, "starts": 16,
        "goals": 10, "npxg": 7.4, "psxg": 9.1, "sot_pct": 58.2, "xga": 2.8, "sca": 45, "touches_box": 76,
        "f3_tackles": 14, "pressures": 220, "aerial_win": 46.5, "conv_pct": 21.3, "npxg_per_shot": 0.16, "offsides": 18,
        "top_speed": 31.4, "dist_p90": 9.6, "hsr": 480, "sprint": 130, "acc_dec": 38,
        "xt": 0.19, "obv": 0.22, "vaep_off": 0.42, "vaep_def": 0.04
    },
    {
        "name": "Jason Cummings", "team": "Mohun Bagan Super Giant", "pos_group": "Forwards / Strikers", "sec_pos": "Right Winger",
        "age": 29, "foot": "Left", "nat": "Australia", "val": "€1.10m", "mins": 1680, "apps": 22, "starts": 19,
        "goals": 12, "npxg": 10.8, "psxg": 12.3, "sot_pct": 52.6, "xga": 4.1, "sca": 54, "touches_box": 94,
        "f3_tackles": 18, "pressures": 265, "aerial_win": 41.2, "conv_pct": 19.8, "npxg_per_shot": 0.17, "offsides": 15,
        "top_speed": 32.2, "dist_p90": 10.1, "hsr": 560, "sprint": 170, "acc_dec": 44,
        "xt": 0.23, "obv": 0.28, "vaep_off": 0.51, "vaep_def": 0.05
    },
    {
        "name": "Armando Sadiku", "team": "FC Goa", "pos_group": "Forwards / Strikers", "sec_pos": "Centre-Forward",
        "age": 33, "foot": "Right", "nat": "Albania", "val": "€700k", "mins": 1510, "apps": 21, "starts": 17,
        "goals": 11, "npxg": 9.5, "psxg": 10.8, "sot_pct": 51.0, "xga": 2.2, "sca": 38, "touches_box": 82,
        "f3_tackles": 12, "pressures": 210, "aerial_win": 54.0, "conv_pct": 20.4, "npxg_per_shot": 0.18, "offsides": 21,
        "top_speed": 31.8, "dist_p90": 9.4, "hsr": 490, "sprint": 140, "acc_dec": 36,
        "xt": 0.17, "obv": 0.20, "vaep_off": 0.44, "vaep_def": 0.03
    },
    {
        "name": "Roy Krishna", "team": "Odisha FC", "pos_group": "Forwards / Strikers", "sec_pos": "Attacking Mid",
        "age": 37, "foot": "Right", "nat": "Fiji", "val": "€350k", "mins": 1820, "apps": 22, "starts": 21,
        "goals": 13, "npxg": 11.2, "psxg": 12.6, "sot_pct": 54.5, "xga": 5.4, "sca": 62, "touches_box": 108,
        "f3_tackles": 22, "pressures": 280, "aerial_win": 49.3, "conv_pct": 21.0, "npxg_per_shot": 0.17, "offsides": 24,
        "top_speed": 32.6, "dist_p90": 10.3, "hsr": 590, "sprint": 190, "acc_dec": 48,
        "xt": 0.26, "obv": 0.31, "vaep_off": 0.56, "vaep_def": 0.06
    },
    {
        "name": "Alaeddine Ajaraie", "team": "NorthEast United FC", "pos_group": "Forwards / Strikers", "sec_pos": "Left Winger",
        "age": 31, "foot": "Right", "nat": "Morocco", "val": "€500k", "mins": 1710, "apps": 20, "starts": 19,
        "goals": 14, "npxg": 11.9, "psxg": 13.8, "sot_pct": 56.8, "xga": 4.6, "sca": 58, "touches_box": 112,
        "f3_tackles": 20, "pressures": 295, "aerial_win": 43.1, "conv_pct": 23.5, "npxg_per_shot": 0.19, "offsides": 19,
        "top_speed": 33.1, "dist_p90": 10.4, "hsr": 620, "sprint": 210, "acc_dec": 52,
        "xt": 0.28, "obv": 0.34, "vaep_off": 0.61, "vaep_def": 0.05
    },
    {
        "name": "Cleiton Silva", "team": "East Bengal FC", "pos_group": "Forwards / Strikers", "sec_pos": "Second Striker",
        "age": 37, "foot": "Right", "nat": "Brazil", "val": "€250k", "mins": 1640, "apps": 21, "starts": 19,
        "goals": 9, "npxg": 7.8, "psxg": 8.9, "sot_pct": 47.5, "xga": 3.8, "sca": 49, "touches_box": 74,
        "f3_tackles": 15, "pressures": 230, "aerial_win": 42.0, "conv_pct": 18.0, "npxg_per_shot": 0.15, "offsides": 14,
        "top_speed": 31.0, "dist_p90": 9.7, "hsr": 470, "sprint": 120, "acc_dec": 35,
        "xt": 0.20, "obv": 0.21, "vaep_off": 0.38, "vaep_def": 0.04
    },
    {
        "name": "Wilmar Jordan Gil", "team": "Chennaiyin FC", "pos_group": "Forwards / Strikers", "sec_pos": "Centre-Forward",
        "age": 34, "foot": "Right", "nat": "Colombia", "val": "€400k", "mins": 1390, "apps": 18, "starts": 15,
        "goals": 8, "npxg": 7.1, "psxg": 7.9, "sot_pct": 49.0, "xga": 1.9, "sca": 32, "touches_box": 80,
        "f3_tackles": 11, "pressures": 190, "aerial_win": 57.2, "conv_pct": 19.5, "npxg_per_shot": 0.18, "offsides": 16,
        "top_speed": 31.5, "dist_p90": 9.2, "hsr": 440, "sprint": 115, "acc_dec": 32,
        "xt": 0.16, "obv": 0.18, "vaep_off": 0.37, "vaep_def": 0.03
    },

    # WINGERS / ATTACKING MIDS
    {
        "name": "Lallianzuala Chhangte", "team": "Mumbai City FC", "pos_group": "Wingers / Attacking Mids", "sec_pos": "Left Winger",
        "age": 27, "foot": "Left", "nat": "India", "val": "€550k", "mins": 1780, "apps": 22, "starts": 21,
        "npxg_xga": 13.5, "gca": 16, "box_entries": 78, "key_passes": 46, "prog_carries": 88, "takeon_pct": 59.4, "cross_comp_pct": 34.8,
        "counter_press": 215, "recov_att3": 28, "f3_pass_pct": 82.4, "dispossessed": 26, "prog_pass_rec": 112,
        "top_speed": 34.2, "dist_p90": 10.8, "hsr": 740, "sprint": 260, "acc_dec": 64,
        "xt": 0.38, "obv": 0.44, "vaep_off": 0.58, "vaep_def": 0.08
    },
    {
        "name": "Liston Colaco", "team": "Mohun Bagan Super Giant", "pos_group": "Wingers / Attacking Mids", "sec_pos": "Right Winger",
        "age": 26, "foot": "Right", "nat": "India", "val": "€450k", "mins": 1540, "apps": 20, "starts": 17,
        "npxg_xga": 11.2, "gca": 13, "box_entries": 65, "key_passes": 38, "prog_carries": 76, "takeon_pct": 57.0, "cross_comp_pct": 31.2,
        "counter_press": 190, "recov_att3": 22, "f3_pass_pct": 79.5, "dispossessed": 31, "prog_pass_rec": 98,
        "top_speed": 33.9, "dist_p90": 10.5, "hsr": 690, "sprint": 240, "acc_dec": 58,
        "xt": 0.32, "obv": 0.38, "vaep_off": 0.49, "vaep_def": 0.06
    },
    {
        "name": "Noah Sadaoui", "team": "Kerala Blasters FC", "pos_group": "Wingers / Attacking Mids", "sec_pos": "Centre-Forward",
        "age": 31, "foot": "Both", "nat": "Morocco", "val": "€600k", "mins": 1690, "apps": 21, "starts": 19,
        "npxg_xga": 14.8, "gca": 18, "box_entries": 85, "key_passes": 52, "prog_carries": 94, "takeon_pct": 61.5, "cross_comp_pct": 36.0,
        "counter_press": 230, "recov_att3": 31, "f3_pass_pct": 81.0, "dispossessed": 34, "prog_pass_rec": 124,
        "top_speed": 33.6, "dist_p90": 10.6, "hsr": 710, "sprint": 245, "acc_dec": 62,
        "xt": 0.41, "obv": 0.47, "vaep_off": 0.63, "vaep_def": 0.07
    },
    {
        "name": "Madih Talal", "team": "East Bengal FC", "pos_group": "Wingers / Attacking Mids", "sec_pos": "Central Mid",
        "age": 27, "foot": "Right", "nat": "France", "val": "€700k", "mins": 1820, "apps": 22, "starts": 21,
        "npxg_xga": 15.6, "gca": 21, "box_entries": 92, "key_passes": 68, "prog_carries": 104, "takeon_pct": 64.2, "cross_comp_pct": 38.5,
        "counter_press": 245, "recov_att3": 35, "f3_pass_pct": 84.1, "dispossessed": 38, "prog_pass_rec": 135,
        "top_speed": 32.8, "dist_p90": 10.7, "hsr": 670, "sprint": 215, "acc_dec": 60,
        "xt": 0.46, "obv": 0.52, "vaep_off": 0.69, "vaep_def": 0.09
    },
    {
        "name": "Hugo Boumous", "team": "Odisha FC", "pos_group": "Wingers / Attacking Mids", "sec_pos": "Attacking Mid",
        "age": 29, "foot": "Right", "nat": "Morocco", "val": "€750k", "mins": 1490, "apps": 19, "starts": 17,
        "npxg_xga": 12.8, "gca": 17, "box_entries": 81, "key_passes": 56, "prog_carries": 82, "takeon_pct": 62.0, "cross_comp_pct": 35.5,
        "counter_press": 210, "recov_att3": 29, "f3_pass_pct": 83.2, "dispossessed": 29, "prog_pass_rec": 110,
        "top_speed": 32.1, "dist_p90": 10.2, "hsr": 580, "sprint": 180, "acc_dec": 50,
        "xt": 0.39, "obv": 0.45, "vaep_off": 0.55, "vaep_def": 0.07
    },
    {
        "name": "Naorem Mahesh Singh", "team": "East Bengal FC", "pos_group": "Wingers / Attacking Mids", "sec_pos": "Left Winger",
        "age": 25, "foot": "Left", "nat": "India", "val": "€400k", "mins": 1620, "apps": 21, "starts": 18,
        "npxg_xga": 9.4, "gca": 11, "box_entries": 58, "key_passes": 39, "prog_carries": 69, "takeon_pct": 53.8, "cross_comp_pct": 32.5,
        "counter_press": 205, "recov_att3": 24, "f3_pass_pct": 78.2, "dispossessed": 28, "prog_pass_rec": 89,
        "top_speed": 33.2, "dist_p90": 10.4, "hsr": 660, "sprint": 220, "acc_dec": 55,
        "xt": 0.29, "obv": 0.33, "vaep_off": 0.43, "vaep_def": 0.06
    },

    # CENTRAL / HOLDING MIDS
    {
        "name": "Lalengmawia Ralte (Apuia)", "team": "Mohun Bagan Super Giant", "pos_group": "Central / Holding Mids", "sec_pos": "Defensive Mid",
        "age": 24, "foot": "Right", "nat": "India", "val": "€500k", "mins": 1840, "apps": 22, "starts": 21,
        "late_box": 14, "long_xg": 0.85, "prog_passes": 142, "f3_passes": 118, "deep_comp": 34, "through_balls": 16,
        "padj_ti": 78, "recoveries": 185, "duel_win_pct": 58.6, "pass_press_pct": 86.4, "press_resist_pct": 89.2, "turnovers": 19,
        "top_speed": 31.9, "dist_p90": 11.2, "hsr": 640, "sprint": 180, "acc_dec": 56,
        "xt": 0.31, "obv": 0.36, "vaep_off": 0.34, "vaep_def": 0.28
    },
    {
        "name": "Ahmed Jahouh", "team": "Odisha FC", "pos_group": "Central / Holding Mids", "sec_pos": "Deep-Lying Playmaker",
        "age": 36, "foot": "Right", "nat": "Morocco", "val": "€300k", "mins": 1890, "apps": 22, "starts": 22,
        "late_box": 6, "long_xg": 1.20, "prog_passes": 215, "f3_passes": 186, "deep_comp": 48, "through_balls": 26,
        "padj_ti": 84, "recoveries": 198, "duel_win_pct": 55.4, "pass_press_pct": 84.8, "press_resist_pct": 91.5, "turnovers": 24,
        "top_speed": 29.8, "dist_p90": 10.4, "hsr": 420, "sprint": 90, "acc_dec": 34,
        "xt": 0.44, "obv": 0.48, "vaep_off": 0.45, "vaep_def": 0.24
    },
    {
        "name": "Vibin Mohanan", "team": "Kerala Blasters FC", "pos_group": "Central / Holding Mids", "sec_pos": "Central Mid",
        "age": 21, "foot": "Right", "nat": "India", "val": "€300k", "mins": 1410, "apps": 19, "starts": 16,
        "late_box": 11, "long_xg": 0.65, "prog_passes": 115, "f3_passes": 88, "deep_comp": 22, "through_balls": 12,
        "padj_ti": 66, "recoveries": 145, "duel_win_pct": 53.2, "pass_press_pct": 82.5, "press_resist_pct": 85.0, "turnovers": 22,
        "top_speed": 31.7, "dist_p90": 11.0, "hsr": 610, "sprint": 160, "acc_dec": 52,
        "xt": 0.24, "obv": 0.27, "vaep_off": 0.27, "vaep_def": 0.21
    },
    {
        "name": "Alberto Noguera", "team": "Bengaluru FC", "pos_group": "Central / Holding Mids", "sec_pos": "Attacking Mid",
        "age": 35, "foot": "Right", "nat": "Spain", "val": "€350k", "mins": 1580, "apps": 20, "starts": 18,
        "late_box": 16, "long_xg": 0.95, "prog_passes": 138, "f3_passes": 124, "deep_comp": 36, "through_balls": 18,
        "padj_ti": 62, "recoveries": 152, "duel_win_pct": 52.0, "pass_press_pct": 85.2, "press_resist_pct": 88.6, "turnovers": 21,
        "top_speed": 30.5, "dist_p90": 10.6, "hsr": 510, "sprint": 130, "acc_dec": 42,
        "xt": 0.33, "obv": 0.38, "vaep_off": 0.39, "vaep_def": 0.18
    },
    {
        "name": "Yoell van Nieff", "team": "Mumbai City FC", "pos_group": "Central / Holding Mids", "sec_pos": "Defensive Mid",
        "age": 31, "foot": "Left", "nat": "Netherlands", "val": "€550k", "mins": 1750, "apps": 21, "starts": 20,
        "late_box": 8, "long_xg": 0.90, "prog_passes": 168, "f3_passes": 135, "deep_comp": 31, "through_balls": 15,
        "padj_ti": 76, "recoveries": 178, "duel_win_pct": 57.8, "pass_press_pct": 87.0, "press_resist_pct": 90.1, "turnovers": 17,
        "top_speed": 30.8, "dist_p90": 10.9, "hsr": 540, "sprint": 140, "acc_dec": 46,
        "xt": 0.32, "obv": 0.37, "vaep_off": 0.32, "vaep_def": 0.26
    },
    {
        "name": "Suresh Singh Wangjam", "team": "Bengaluru FC", "pos_group": "Central / Holding Mids", "sec_pos": "Central Mid",
        "age": 24, "foot": "Right", "nat": "India", "val": "€400k", "mins": 1690, "apps": 21, "starts": 19,
        "late_box": 12, "long_xg": 0.55, "prog_passes": 108, "f3_passes": 82, "deep_comp": 19, "through_balls": 9,
        "padj_ti": 86, "recoveries": 172, "duel_win_pct": 56.4, "pass_press_pct": 81.2, "press_resist_pct": 83.5, "turnovers": 23,
        "top_speed": 32.4, "dist_p90": 11.5, "hsr": 690, "sprint": 210, "acc_dec": 60,
        "xt": 0.22, "obv": 0.25, "vaep_off": 0.22, "vaep_def": 0.31
    },

    # FULLBACKS / WINGBACKS
    {
        "name": "Subhasish Bose", "team": "Mohun Bagan Super Giant", "pos_group": "Fullbacks / Wingbacks", "sec_pos": "Centre-Back",
        "age": 29, "foot": "Left", "nat": "India", "val": "€400k", "mins": 1910, "apps": 22, "starts": 22,
        "fb_xga": 3.6, "crosses_comp": 28, "overlap_runs": 45, "prog_carries": 54, "prog_passes": 89, "f3_entries": 42,
        "dribble_tackle_pct": 68.4, "padj_int": 44, "backpost_aerial_pct": 66.8, "pass_comp_pct": 82.5, "prog_dist": 2250,
        "top_speed": 32.8, "dist_p90": 10.6, "hsr": 670, "sprint": 220, "acc_dec": 54,
        "xt": 0.24, "obv": 0.28, "vaep_off": 0.25, "vaep_def": 0.34
    },
    {
        "name": "Akash Mishra", "team": "Mumbai City FC", "pos_group": "Fullbacks / Wingbacks", "sec_pos": "Left Mid",
        "age": 23, "foot": "Left", "nat": "India", "val": "€450k", "mins": 1580, "apps": 19, "starts": 18,
        "fb_xga": 4.1, "crosses_comp": 34, "overlap_runs": 62, "prog_carries": 72, "prog_passes": 96, "f3_entries": 56,
        "dribble_tackle_pct": 64.0, "padj_int": 38, "backpost_aerial_pct": 58.2, "pass_comp_pct": 83.8, "prog_dist": 2680,
        "top_speed": 34.4, "dist_p90": 11.1, "hsr": 780, "sprint": 270, "acc_dec": 66,
        "xt": 0.31, "obv": 0.35, "vaep_off": 0.33, "vaep_def": 0.26
    },
    {
        "name": "Jay Gupta", "team": "FC Goa", "pos_group": "Fullbacks / Wingbacks", "sec_pos": "Centre-Back",
        "age": 23, "foot": "Left", "nat": "India", "val": "€375k", "mins": 1790, "apps": 21, "starts": 20,
        "fb_xga": 3.8, "crosses_comp": 31, "overlap_runs": 51, "prog_carries": 64, "prog_passes": 92, "f3_entries": 49,
        "dribble_tackle_pct": 66.5, "padj_int": 42, "backpost_aerial_pct": 64.1, "pass_comp_pct": 81.6, "prog_dist": 2420,
        "top_speed": 33.5, "dist_p90": 10.9, "hsr": 720, "sprint": 240, "acc_dec": 59,
        "xt": 0.27, "obv": 0.31, "vaep_off": 0.29, "vaep_def": 0.30
    },
    {
        "name": "Nikhil Poojary", "team": "Bengaluru FC", "pos_group": "Fullbacks / Wingbacks", "sec_pos": "Right Winger",
        "age": 29, "foot": "Right", "nat": "India", "val": "€350k", "mins": 1720, "apps": 20, "starts": 20,
        "fb_xga": 2.9, "crosses_comp": 25, "overlap_runs": 48, "prog_carries": 58, "prog_passes": 81, "f3_entries": 44,
        "dribble_tackle_pct": 63.8, "padj_int": 39, "backpost_aerial_pct": 59.5, "pass_comp_pct": 80.2, "prog_dist": 2180,
        "top_speed": 33.1, "dist_p90": 10.7, "hsr": 690, "sprint": 230, "acc_dec": 56,
        "xt": 0.22, "obv": 0.26, "vaep_off": 0.24, "vaep_def": 0.27
    },

    # CENTER BACKS
    {
        "name": "Sandesh Jhingan", "team": "FC Goa", "pos_group": "Center Backs", "sec_pos": "Right-Back",
        "age": 31, "foot": "Right", "nat": "India", "val": "€350k", "mins": 1620, "apps": 19, "starts": 18,
        "sp_xg": 1.4, "sp_aerial": 26, "line_break_pass": 62, "prog_pass_dist": 3450, "switches": 18,
        "aerial_duel_pct": 71.4, "ground_tackle_pct": 74.2, "shots_blocked": 28, "clearances": 94, "err_shot": 1,
        "buildup_comp_pct": 86.8, "long_pass_acc_pct": 64.5,
        "top_speed": 31.2, "dist_p90": 9.8, "hsr": 420, "sprint": 110, "acc_dec": 36,
        "xt": 0.14, "obv": 0.17, "vaep_off": 0.12, "vaep_def": 0.46
    },
    {
        "name": "Anwar Ali", "team": "East Bengal FC", "pos_group": "Center Backs", "sec_pos": "Right-Back",
        "age": 24, "foot": "Right", "nat": "India", "val": "€500k", "mins": 1860, "apps": 21, "starts": 21,
        "sp_xg": 1.6, "sp_aerial": 29, "line_break_pass": 84, "prog_pass_dist": 4120, "switches": 24,
        "aerial_duel_pct": 69.2, "ground_tackle_pct": 72.8, "shots_blocked": 24, "clearances": 86, "err_shot": 2,
        "buildup_comp_pct": 89.4, "long_pass_acc_pct": 68.2,
        "top_speed": 32.5, "dist_p90": 10.2, "hsr": 490, "sprint": 145, "acc_dec": 42,
        "xt": 0.22, "obv": 0.25, "vaep_off": 0.18, "vaep_def": 0.44
    },
    {
        "name": "Rahul Bheke", "team": "Bengaluru FC", "pos_group": "Center Backs", "sec_pos": "Right-Back",
        "age": 34, "foot": "Right", "nat": "India", "val": "€300k", "mins": 1780, "apps": 21, "starts": 20,
        "sp_xg": 1.1, "sp_aerial": 22, "line_break_pass": 58, "prog_pass_dist": 3280, "switches": 16,
        "aerial_duel_pct": 67.8, "ground_tackle_pct": 73.0, "shots_blocked": 26, "clearances": 89, "err_shot": 1,
        "buildup_comp_pct": 87.2, "long_pass_acc_pct": 62.0,
        "top_speed": 31.6, "dist_p90": 9.9, "hsr": 440, "sprint": 120, "acc_dec": 38,
        "xt": 0.13, "obv": 0.16, "vaep_off": 0.11, "vaep_def": 0.42
    },
    {
        "name": "Mourtada Fall", "team": "Odisha FC", "pos_group": "Center Backs", "sec_pos": "Centre-Forward",
        "age": 36, "foot": "Right", "nat": "Senegal", "val": "€300k", "mins": 1650, "apps": 19, "starts": 19,
        "sp_xg": 2.8, "sp_aerial": 42, "line_break_pass": 52, "prog_pass_dist": 2980, "switches": 14,
        "aerial_duel_pct": 78.5, "ground_tackle_pct": 75.0, "shots_blocked": 32, "clearances": 112, "err_shot": 2,
        "buildup_comp_pct": 85.0, "long_pass_acc_pct": 59.8,
        "top_speed": 30.8, "dist_p90": 9.4, "hsr": 380, "sprint": 95, "acc_dec": 30,
        "xt": 0.12, "obv": 0.15, "vaep_off": 0.22, "vaep_def": 0.48
    },
    {
        "name": "Mehtab Singh", "team": "Mumbai City FC", "pos_group": "Center Backs", "sec_pos": "Right-Back",
        "age": 26, "foot": "Right", "nat": "India", "val": "€400k", "mins": 1720, "apps": 20, "starts": 19,
        "sp_xg": 1.2, "sp_aerial": 24, "line_break_pass": 71, "prog_pass_dist": 3760, "switches": 21,
        "aerial_duel_pct": 68.0, "ground_tackle_pct": 71.5, "shots_blocked": 22, "clearances": 78, "err_shot": 1,
        "buildup_comp_pct": 90.1, "long_pass_acc_pct": 66.4,
        "top_speed": 32.1, "dist_p90": 10.0, "hsr": 460, "sprint": 130, "acc_dec": 40,
        "xt": 0.18, "obv": 0.21, "vaep_off": 0.14, "vaep_def": 0.40
    },

    # GOALKEEPERS
    {
        "name": "Vishal Kaith", "team": "Mohun Bagan Super Giant", "pos_group": "Goalkeepers", "sec_pos": "Goalkeeper",
        "age": 28, "foot": "Right", "nat": "India", "val": "€450k", "mins": 1980, "apps": 22, "starts": 22,
        "pass_40yds_pct": 46.2, "launch_pct": 38.5, "gk_length": 42.5,
        "psxg_minus_ga": 5.4, "crosses_stopped_pct": 9.4, "sweeper_actions": 34,
        "save_pct": 77.8, "pass_press_pct": 72.4, "clean_sheets": 10,
        "top_speed": 28.5, "dist_p90": 5.2, "hsr": 90, "sprint": 25, "acc_dec": 16,
        "xt": 0.04, "obv": 0.06, "vaep_off": 0.02, "vaep_def": 0.52
    },
    {
        "name": "Phurba Lachenpa", "team": "Mumbai City FC", "pos_group": "Goalkeepers", "sec_pos": "Goalkeeper",
        "age": 26, "foot": "Right", "nat": "India", "val": "€400k", "mins": 1890, "apps": 21, "starts": 21,
        "pass_40yds_pct": 49.5, "launch_pct": 34.0, "gk_length": 39.8,
        "psxg_minus_ga": 4.8, "crosses_stopped_pct": 8.8, "sweeper_actions": 38,
        "save_pct": 76.5, "pass_press_pct": 75.2, "clean_sheets": 9,
        "top_speed": 28.9, "dist_p90": 5.5, "hsr": 110, "sprint": 30, "acc_dec": 18,
        "xt": 0.05, "obv": 0.08, "vaep_off": 0.03, "vaep_def": 0.49
    },
    {
        "name": "Gurpreet Singh Sandhu", "team": "Bengaluru FC", "pos_group": "Goalkeepers", "sec_pos": "Goalkeeper",
        "age": 32, "foot": "Right", "nat": "India", "val": "€350k", "mins": 1980, "apps": 22, "starts": 22,
        "pass_40yds_pct": 43.8, "launch_pct": 48.0, "gk_length": 46.2,
        "psxg_minus_ga": 3.9, "crosses_stopped_pct": 11.2, "sweeper_actions": 26,
        "save_pct": 74.2, "pass_press_pct": 68.0, "clean_sheets": 6,
        "top_speed": 27.8, "dist_p90": 4.9, "hsr": 75, "sprint": 20, "acc_dec": 14,
        "xt": 0.03, "obv": 0.05, "vaep_off": 0.01, "vaep_def": 0.44
    },
    {
        "name": "Amrinder Singh", "team": "Odisha FC", "pos_group": "Goalkeepers", "sec_pos": "Goalkeeper",
        "age": 31, "foot": "Right", "nat": "India", "val": "€350k", "mins": 1980, "apps": 22, "starts": 22,
        "pass_40yds_pct": 45.0, "launch_pct": 42.1, "gk_length": 43.0,
        "psxg_minus_ga": 4.2, "crosses_stopped_pct": 9.0, "sweeper_actions": 31,
        "save_pct": 75.0, "pass_press_pct": 71.0, "clean_sheets": 8,
        "top_speed": 28.2, "dist_p90": 5.1, "hsr": 85, "sprint": 22, "acc_dec": 15,
        "xt": 0.04, "obv": 0.06, "vaep_off": 0.02, "vaep_def": 0.47
    },
    {
        "name": "Prabhsukhan Singh Gill", "team": "East Bengal FC", "pos_group": "Goalkeepers", "sec_pos": "Goalkeeper",
        "age": 23, "foot": "Right", "nat": "India", "val": "€350k", "mins": 1980, "apps": 22, "starts": 22,
        "pass_40yds_pct": 41.5, "launch_pct": 45.8, "gk_length": 44.5,
        "psxg_minus_ga": 2.8, "crosses_stopped_pct": 8.2, "sweeper_actions": 24,
        "save_pct": 73.1, "pass_press_pct": 69.5, "clean_sheets": 5,
        "top_speed": 28.0, "dist_p90": 5.0, "hsr": 80, "sprint": 20, "acc_dec": 14,
        "xt": 0.03, "obv": 0.04, "vaep_off": 0.01, "vaep_def": 0.38
    }
]

# Additional synthetic players generator across all teams to reach 180+ players
INDIAN_FIRST_NAMES = ["Rohit", "Ashique", "Brandon", "Aniket", "Hitesh", "Glan", "Pratik", "Deepak", "Narender", "Chinglensana", "Lalthathanga", "Vinit", "Bipin", "Jerry", "Salam", "Givson", "Bryce", "Mark", "Ayush", "Ayush", "Suhair", "Jobby", "Sanjeev", "Soraisham", "Danish", "Mohammad", "Tondonba", "Ricky", "Makan", "Ngangom"]
INDIAN_LAST_NAMES = ["Fernandes", "Kuruniyan", "Martins", "Choudhary", "Jadhav", "Sharma", "Borges", "Tangri", "Gahlot", "Singh", "Khawlhring", "Rai", "Mawihmingthanga", "Lalrinzuala", "Devrani", "Miranda", "Zothanmawia", "Bhat", "Chhetri", "Farooq", "Yasir", "Pandita", "Chothe", "Kiyam", "Adhikari", "Shabong"]
FOREIGN_FIRST_NAMES = ["Carlos", "Diego", "Lucas", "Javier", "Daniel", "Matej", "Milos", "Borja", "Adrian", "Edu", "Tiri", "Slavko", "Ryan", "Carl", "Saul", "Connor", "Jordan", "Greg"]
FOREIGN_LAST_NAMES = ["Perez", "Silva", "Hernandez", "Gimenez", "Luna", "Bedia", "Crespo", "Edwards", "Shields", "Murray", "Stewart", "Drincic", "Damjanovic", "McHugh", "Valpuia"]

POSITIONS_LIST = [
    "Forwards / Strikers",
    "Wingers / Attacking Mids",
    "Central / Holding Mids",
    "Fullbacks / Wingbacks",
    "Center Backs",
    "Goalkeepers"
]

def generate_full_roster():
    """Generates a rich, consistent database of 180+ ISL players with realistic distributions."""
    np.random.seed(42)
    team_names = [c["team"] for c in CLUBS_DATA]
    team_dict = {c["team"]: c for c in CLUBS_DATA}
    
    players = []
    sofascore_id_counter = 100000
    
    # First add the hand-curated seeds
    for s in ROSTER_SEEDS:
        sofascore_id_counter += 1
        team_info = team_dict[s["team"]]
        mins = s["mins"]
        poss = team_info["poss_pct"]
        p90_factor = 90.0 / mins
        
        # Calculate Universal Baseline Header fields
        available_league_mins = 22 * 90  # 1980 mins
        pct_mins = round((mins / available_league_mins) * 100.0, 1)
        injuries = np.random.randint(0, 4)
        yellows = np.random.randint(1, 6)
        reds = 1 if np.random.rand() < 0.1 else 0
        fouls_comm = np.random.randint(12, 38)
        fouls_drawn = np.random.randint(15, 45)
        sofascore_rating = round(float(np.random.uniform(6.85, 7.55)), 2)

        # Baseline record
        rec = {
            "sofascore_id": sofascore_id_counter,
            "name": s["name"],
            "team": s["team"],
            "team_short": team_info["short"],
            "pos_group": s["pos_group"],
            "secondary_pos": s["sec_pos"],
            "age": s["age"],
            "preferred_foot": s["foot"],
            "nationality": s["nat"],
            "market_value": s["val"],
            "minutes": mins,
            "appearances": s["apps"],
            "starts": s["starts"],
            "subs": s["apps"] - s["starts"],
            "pct_available_mins": pct_mins,
            "matches_missed_injury": injuries,
            "yellow_cards": yellows,
            "red_cards": reds,
            "fouls_committed": fouls_comm,
            "fouls_drawn": fouls_drawn,
            "fouls_committed_p90": round(fouls_comm * p90_factor, 2),
            "fouls_drawn_p90": round(fouls_drawn * p90_factor, 2),
            "team_possession_pct": poss,
            "sofascore_rating": sofascore_rating,
            # Physical tracking
            "distance_covered_p90": s["dist_p90"],
            "hsr_distance_p90": s["hsr"],
            "sprint_distance_p90": s["sprint"],
            "peak_velocity_kmh": s["top_speed"],
            "high_intensity_accel_decel_p90": s["acc_dec"],
            # Advanced value-added
            "xthreat_p90": s["xt"],
            "obv_p90": s["obv"],
            "vaep_offensive_p90": s["vaep_off"],
            "vaep_defensive_p90": s["vaep_def"],
            "vaep_total_p90": round(s["vaep_off"] + s["vaep_def"], 3),
        }

        # Populate group-specific metrics
        pg = s["pos_group"]
        if pg == "Forwards / Strikers":
            rec["goals"] = s["goals"]
            rec["goals_p90"] = round(s["goals"] * p90_factor, 2)
            rec["npxg"] = s["npxg"]
            rec["npxg_p90"] = round(s["npxg"] * p90_factor, 2)
            rec["psxg"] = s["psxg"]
            rec["psxg_p90"] = round(s["psxg"] * p90_factor, 2)
            rec["shots_on_target_pct"] = s["sot_pct"]
            rec["xga"] = s["xga"]
            rec["xga_p90"] = round(s["xga"] * p90_factor, 2)
            rec["sca"] = s["sca"]
            rec["sca_p90"] = round(s["sca"] * p90_factor, 2)
            rec["touches_in_box"] = s["touches_box"]
            rec["touches_in_box_p90"] = round(s["touches_box"] * p90_factor, 1)
            rec["final_third_tackles"] = s["f3_tackles"]
            rec["final_third_tackles_p90"] = round(s["f3_tackles"] * p90_factor, 2)
            rec["high_intensity_pressures"] = s["pressures"]
            rec["high_intensity_pressures_p90"] = round(s["pressures"] * p90_factor, 1)
            rec["aerial_win_pct"] = s["aerial_win"]
            rec["conversion_rate_pct"] = s["conv_pct"]
            rec["npxg_per_shot"] = s["npxg_per_shot"]
            rec["offsides"] = s["offsides"]
            rec["offsides_p90"] = round(s["offsides"] * p90_factor, 2)

        elif pg == "Wingers / Attacking Mids":
            rec["npxg_plus_xga"] = s["npxg_xga"]
            rec["npxg_plus_xga_p90"] = round(s["npxg_xga"] * p90_factor, 2)
            rec["gca"] = s["gca"]
            rec["gca_p90"] = round(s["gca"] * p90_factor, 2)
            rec["box_entries"] = s["box_entries"]
            rec["box_entries_p90"] = round(s["box_entries"] * p90_factor, 2)
            rec["key_passes"] = s["key_passes"]
            rec["key_passes_p90"] = round(s["key_passes"] * p90_factor, 2)
            rec["progressive_carries"] = s["prog_carries"]
            rec["progressive_carries_p90"] = round(s["prog_carries"] * p90_factor, 2)
            rec["takeon_success_pct"] = s["takeon_pct"]
            rec["cross_completion_pct"] = s["cross_comp_pct"]
            rec["counter_pressures"] = s["counter_press"]
            rec["counter_pressures_p90"] = round(s["counter_press"] * p90_factor, 1)
            rec["recoveries_att_third"] = s["recov_att3"]
            rec["recoveries_att_third_p90"] = round(s["recov_att3"] * p90_factor, 2)
            rec["final_third_pass_pct"] = s["f3_pass_pct"]
            rec["dispossessed"] = s["dispossessed"]
            rec["dispossessed_p90"] = round(s["dispossessed"] * p90_factor, 2)
            rec["prog_passes_received"] = s["prog_pass_rec"]
            rec["prog_passes_received_p90"] = round(s["prog_pass_rec"] * p90_factor, 2)

        elif pg == "Central / Holding Mids":
            rec["late_box_arrivals"] = s["late_box"]
            rec["late_box_arrivals_p90"] = round(s["late_box"] * p90_factor, 2)
            rec["long_range_shot_xg"] = s["long_xg"]
            rec["long_range_shot_xg_p90"] = round(s["long_xg"] * p90_factor, 2)
            rec["progressive_passes"] = s["prog_passes"]
            rec["progressive_passes_p90"] = round(s["prog_passes"] * p90_factor, 2)
            rec["passes_to_final_third"] = s["f3_passes"]
            rec["passes_to_final_third_p90"] = round(s["f3_passes"] * p90_factor, 2)
            rec["deep_completions"] = s["deep_comp"]
            rec["deep_completions_p90"] = round(s["deep_comp"] * p90_factor, 2)
            rec["through_balls"] = s["through_balls"]
            rec["through_balls_p90"] = round(s["through_balls"] * p90_factor, 2)
            
            # PAdj calculations
            opp_poss = 100.0 - poss
            padj_scaling = 50.0 / opp_poss
            rec["tackles_interceptions"] = s["padj_ti"]
            rec["padj_tackles_interceptions_p90"] = round(s["padj_ti"] * p90_factor * padj_scaling, 2)
            rec["ball_recoveries"] = s["recoveries"]
            rec["ball_recoveries_p90"] = round(s["recoveries"] * p90_factor, 2)
            rec["duel_win_pct"] = s["duel_win_pct"]
            rec["pass_completion_under_pressure_pct"] = s["pass_press_pct"]
            rec["press_resistance_pct"] = s["press_resist_pct"]
            rec["turnovers"] = s["turnovers"]
            rec["turnovers_p90"] = round(s["turnovers"] * p90_factor, 2)

        elif pg == "Fullbacks / Wingbacks":
            rec["xga"] = s["fb_xga"]
            rec["xga_p90"] = round(s["fb_xga"] * p90_factor, 2)
            rec["open_play_crosses"] = s["crosses_comp"]
            rec["open_play_crosses_p90"] = round(s["crosses_comp"] * p90_factor, 2)
            rec["overlapping_runs"] = s["overlap_runs"]
            rec["overlapping_runs_p90"] = round(s["overlap_runs"] * p90_factor, 2)
            rec["progressive_carries"] = s["prog_carries"]
            rec["progressive_carries_p90"] = round(s["prog_carries"] * p90_factor, 2)
            rec["progressive_passes"] = s["prog_passes"]
            rec["progressive_passes_p90"] = round(s["prog_passes"] * p90_factor, 2)
            rec["final_third_entries"] = s["f3_entries"]
            rec["final_third_entries_p90"] = round(s["f3_entries"] * p90_factor, 2)
            rec["dribble_tackle_pct"] = s["dribble_tackle_pct"]
            
            opp_poss = 100.0 - poss
            padj_scaling = 50.0 / opp_poss
            rec["interceptions"] = s["padj_int"]
            rec["padj_interceptions_p90"] = round(s["padj_int"] * p90_factor * padj_scaling, 2)
            rec["back_post_aerial_win_pct"] = s["backpost_aerial_pct"]
            rec["pass_completion_pct"] = s["pass_comp_pct"]
            rec["prog_distance_carried"] = s["prog_dist"]
            rec["prog_distance_carried_p90"] = round(s["prog_dist"] * p90_factor, 0)

        elif pg == "Center Backs":
            rec["set_piece_xg"] = s["sp_xg"]
            rec["set_piece_xg_p90"] = round(s["sp_xg"] * p90_factor, 2)
            rec["set_piece_aerial_contacts"] = s["sp_aerial"]
            rec["set_piece_aerial_contacts_p90"] = round(s["sp_aerial"] * p90_factor, 2)
            rec["line_breaking_passes"] = s["line_break_pass"]
            rec["line_breaking_passes_p90"] = round(s["line_break_pass"] * p90_factor, 2)
            rec["prog_pass_distance"] = s["prog_pass_dist"]
            rec["prog_pass_distance_p90"] = round(s["prog_pass_dist"] * p90_factor, 0)
            rec["switches_of_play"] = s["switches"]
            rec["switches_of_play_p90"] = round(s["switches"] * p90_factor, 2)
            rec["aerial_win_pct"] = s["aerial_duel_pct"]
            rec["ground_tackle_win_pct"] = s["ground_tackle_pct"]
            rec["shots_blocked"] = s["shots_blocked"]
            rec["shots_blocked_p90"] = round(s["shots_blocked"] * p90_factor, 2)
            rec["clearances"] = s["clearances"]
            rec["clearances_p90"] = round(s["clearances"] * p90_factor, 2)
            rec["errors_leading_to_shot"] = s["err_shot"]
            rec["errors_leading_to_shot_p90"] = round(s["err_shot"] * p90_factor, 2)
            rec["buildup_pass_completion_pct"] = s["buildup_comp_pct"]
            rec["long_pass_accuracy_pct"] = s["long_pass_acc_pct"]

        elif pg == "Goalkeepers":
            rec["passes_40yds_pct"] = s["pass_40yds_pct"]
            rec["launch_pct"] = s["launch_pct"]
            rec["goal_kick_length_avg"] = s["gk_length"]
            rec["psxg_minus_ga"] = s["psxg_minus_ga"]
            rec["psxg_minus_ga_p90"] = round(s["psxg_minus_ga"] * p90_factor, 2)
            rec["crosses_stopped_pct"] = s["crosses_stopped_pct"]
            rec["sweeper_actions"] = s["sweeper_actions"]
            rec["sweeper_actions_p90"] = round(s["sweeper_actions"] * p90_factor, 2)
            rec["save_pct"] = s["save_pct"]
            rec["pass_completion_under_press_pct"] = s["pass_press_pct"]
            rec["clean_sheet_pct"] = round((s["clean_sheets"] / s["apps"]) * 100.0, 1)

        players.append(rec)

    # Now generate complementary cohort players per position group across all 13 teams
    for team_name in team_names:
        team_info = team_dict[team_name]
        poss = team_info["poss_pct"]
        opp_poss = 100.0 - poss
        padj_scaling = 50.0 / opp_poss
        
        for pos_group in POSITIONS_LIST:
            # Generate 2 additional players per team per position group
            for idx in range(2):
                sofascore_id_counter += 1
                is_indian = np.random.rand() < 0.70
                if is_indian:
                    p_name = f"{np.random.choice(INDIAN_FIRST_NAMES)} {np.random.choice(INDIAN_LAST_NAMES)}"
                    nat = "India"
                    val_val = np.random.choice(["€100k", "€175k", "€225k", "€300k", "€375k"])
                else:
                    p_name = f"{np.random.choice(FOREIGN_FIRST_NAMES)} {np.random.choice(FOREIGN_LAST_NAMES)}"
                    nat = np.random.choice(["Spain", "Brazil", "Australia", "France", "Argentina", "Nigeria", "Japan"])
                    val_val = np.random.choice(["€350k", "€450k", "€600k", "€800k"])

                mins = int(np.random.uniform(320, 1900))
                apps = max(int(np.ceil(mins / 85.0)), 4)
                starts = max(int(apps * np.random.uniform(0.6, 1.0)), 1)
                p90_factor = 90.0 / mins
                
                age = int(np.random.choice([19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]))
                foot = np.random.choice(["Right", "Left", "Both"], p=[0.72, 0.22, 0.06])
                
                injuries = np.random.randint(0, 5)
                yellows = np.random.randint(0, 7)
                reds = 1 if np.random.rand() < 0.08 else 0
                fouls_comm = int(np.random.uniform(5, 35))
                fouls_drawn = int(np.random.uniform(8, 42))

                rec = {
                    "sofascore_id": sofascore_id_counter,
                    "name": p_name,
                    "team": team_name,
                    "team_short": team_info["short"],
                    "pos_group": pos_group,
                    "secondary_pos": "Utility",
                    "age": age,
                    "preferred_foot": foot,
                    "nationality": nat,
                    "market_value": val_val,
                    "minutes": mins,
                    "appearances": apps,
                    "starts": starts,
                    "subs": apps - starts,
                    "pct_available_mins": round((mins / 1980.0) * 100.0, 1),
                    "matches_missed_injury": injuries,
                    "yellow_cards": yellows,
                    "red_cards": reds,
                    "fouls_committed": fouls_comm,
                    "fouls_drawn": fouls_drawn,
                    "fouls_committed_p90": round(fouls_comm * p90_factor, 2),
                    "fouls_drawn_p90": round(fouls_drawn * p90_factor, 2),
                    "team_possession_pct": poss,
                    "sofascore_rating": round(float(np.random.normal(6.92, 0.25)), 2),
                    # Physical tracking
                    "distance_covered_p90": round(float(np.random.normal(10.2, 0.6)), 2),
                    "hsr_distance_p90": int(np.random.normal(550, 120)),
                    "sprint_distance_p90": int(np.random.normal(180, 50)),
                    "peak_velocity_kmh": round(float(np.random.normal(32.2, 1.2)), 1),
                    "high_intensity_accel_decel_p90": round(float(np.random.normal(48.0, 8.0)), 1),
                    # Advanced Possession Value
                    "xthreat_p90": round(float(np.random.normal(0.22, 0.08)), 3),
                    "obv_p90": round(float(np.random.normal(0.26, 0.09)), 3),
                    "vaep_offensive_p90": round(float(np.random.normal(0.32, 0.12)), 3),
                    "vaep_defensive_p90": round(float(np.random.normal(0.20, 0.10)), 3),
                }
                rec["vaep_total_p90"] = round(rec["vaep_offensive_p90"] + rec["vaep_defensive_p90"], 3)

                if pos_group == "Forwards / Strikers":
                    goals = int(np.random.poisson(lam=max(1.0, mins / 260.0)))
                    npxg = round(float(goals * np.random.uniform(0.75, 1.15) + 0.5), 1)
                    psxg = round(float(npxg * np.random.uniform(0.85, 1.25)), 1)
                    rec["goals"] = goals
                    rec["goals_p90"] = round(goals * p90_factor, 2)
                    rec["npxg"] = npxg
                    rec["npxg_p90"] = round(npxg * p90_factor, 2)
                    rec["psxg"] = psxg
                    rec["psxg_p90"] = round(psxg * p90_factor, 2)
                    rec["shots_on_target_pct"] = round(float(np.random.normal(48.0, 6.0)), 1)
                    rec["xga"] = round(float(np.random.uniform(0.8, 3.5)), 1)
                    rec["xga_p90"] = round(rec["xga"] * p90_factor, 2)
                    rec["sca"] = int(np.random.uniform(15, 55))
                    rec["sca_p90"] = round(rec["sca"] * p90_factor, 2)
                    rec["touches_in_box"] = int(np.random.uniform(30, 95))
                    rec["touches_in_box_p90"] = round(rec["touches_in_box"] * p90_factor, 1)
                    rec["final_third_tackles"] = int(np.random.uniform(5, 20))
                    rec["final_third_tackles_p90"] = round(rec["final_third_tackles"] * p90_factor, 2)
                    rec["high_intensity_pressures"] = int(np.random.uniform(120, 290))
                    rec["high_intensity_pressures_p90"] = round(rec["high_intensity_pressures"] * p90_factor, 1)
                    rec["aerial_win_pct"] = round(float(np.random.normal(44.0, 7.0)), 1)
                    rec["conversion_rate_pct"] = round(float(np.random.normal(16.5, 4.0)), 1)
                    rec["npxg_per_shot"] = round(float(np.random.normal(0.15, 0.03)), 2)
                    rec["offsides"] = int(np.random.uniform(4, 22))
                    rec["offsides_p90"] = round(rec["offsides"] * p90_factor, 2)

                elif pos_group == "Wingers / Attacking Mids":
                    rec["npxg_plus_xga"] = round(float(np.random.uniform(4.0, 13.0)), 1)
                    rec["npxg_plus_xga_p90"] = round(rec["npxg_plus_xga"] * p90_factor, 2)
                    rec["gca"] = int(np.random.uniform(3, 16))
                    rec["gca_p90"] = round(rec["gca"] * p90_factor, 2)
                    rec["box_entries"] = int(np.random.uniform(25, 80))
                    rec["box_entries_p90"] = round(rec["box_entries"] * p90_factor, 2)
                    rec["key_passes"] = int(np.random.uniform(18, 55))
                    rec["key_passes_p90"] = round(rec["key_passes"] * p90_factor, 2)
                    rec["progressive_carries"] = int(np.random.uniform(30, 85))
                    rec["progressive_carries_p90"] = round(rec["progressive_carries"] * p90_factor, 2)
                    rec["takeon_success_pct"] = round(float(np.random.normal(54.0, 6.5)), 1)
                    rec["cross_completion_pct"] = round(float(np.random.normal(30.0, 5.0)), 1)
                    rec["counter_pressures"] = int(np.random.uniform(110, 240))
                    rec["counter_pressures_p90"] = round(rec["counter_pressures"] * p90_factor, 1)
                    rec["recoveries_att_third"] = int(np.random.uniform(10, 32))
                    rec["recoveries_att_third_p90"] = round(rec["recoveries_att_third"] * p90_factor, 2)
                    rec["final_third_pass_pct"] = round(float(np.random.normal(78.5, 4.5)), 1)
                    rec["dispossessed"] = int(np.random.uniform(14, 36))
                    rec["dispossessed_p90"] = round(rec["dispossessed"] * p90_factor, 2)
                    rec["prog_passes_received"] = int(np.random.uniform(40, 115))
                    rec["prog_passes_received_p90"] = round(rec["prog_passes_received"] * p90_factor, 2)

                elif pos_group == "Central / Holding Mids":
                    rec["late_box_arrivals"] = int(np.random.uniform(4, 18))
                    rec["late_box_arrivals_p90"] = round(rec["late_box_arrivals"] * p90_factor, 2)
                    rec["long_range_shot_xg"] = round(float(np.random.uniform(0.3, 1.2)), 2)
                    rec["long_range_shot_xg_p90"] = round(rec["long_range_shot_xg"] * p90_factor, 2)
                    rec["progressive_passes"] = int(np.random.uniform(50, 160))
                    rec["progressive_passes_p90"] = round(rec["progressive_passes"] * p90_factor, 2)
                    rec["passes_to_final_third"] = int(np.random.uniform(40, 130))
                    rec["passes_to_final_third_p90"] = round(rec["passes_to_final_third"] * p90_factor, 2)
                    rec["deep_completions"] = int(np.random.uniform(10, 40))
                    rec["deep_completions_p90"] = round(rec["deep_completions"] * p90_factor, 2)
                    rec["through_balls"] = int(np.random.uniform(4, 20))
                    rec["through_balls_p90"] = round(rec["through_balls"] * p90_factor, 2)
                    ti_raw = int(np.random.uniform(35, 80))
                    rec["tackles_interceptions"] = ti_raw
                    rec["padj_tackles_interceptions_p90"] = round(ti_raw * p90_factor * padj_scaling, 2)
                    rec["ball_recoveries"] = int(np.random.uniform(60, 175))
                    rec["ball_recoveries_p90"] = round(rec["ball_recoveries"] * p90_factor, 2)
                    rec["duel_win_pct"] = round(float(np.random.normal(54.0, 5.0)), 1)
                    rec["pass_completion_under_pressure_pct"] = round(float(np.random.normal(83.0, 4.0)), 1)
                    rec["press_resistance_pct"] = round(float(np.random.normal(85.5, 4.5)), 1)
                    rec["turnovers"] = int(np.random.uniform(10, 26))
                    rec["turnovers_p90"] = round(rec["turnovers"] * p90_factor, 2)

                elif pos_group == "Fullbacks / Wingbacks":
                    rec["xga"] = round(float(np.random.uniform(1.0, 4.0)), 1)
                    rec["xga_p90"] = round(rec["xga"] * p90_factor, 2)
                    rec["open_play_crosses"] = int(np.random.uniform(12, 36))
                    rec["open_play_crosses_p90"] = round(rec["open_play_crosses"] * p90_factor, 2)
                    rec["overlapping_runs"] = int(np.random.uniform(18, 55))
                    rec["overlapping_runs_p90"] = round(rec["overlapping_runs"] * p90_factor, 2)
                    rec["progressive_carries"] = int(np.random.uniform(25, 68))
                    rec["progressive_carries_p90"] = round(rec["progressive_carries"] * p90_factor, 2)
                    rec["progressive_passes"] = int(np.random.uniform(35, 90))
                    rec["progressive_passes_p90"] = round(rec["progressive_passes"] * p90_factor, 2)
                    rec["final_third_entries"] = int(np.random.uniform(18, 52))
                    rec["final_third_entries_p90"] = round(rec["final_third_entries"] * p90_factor, 2)
                    rec["dribble_tackle_pct"] = round(float(np.random.normal(63.0, 5.5)), 1)
                    int_raw = int(np.random.uniform(16, 42))
                    rec["interceptions"] = int_raw
                    rec["padj_interceptions_p90"] = round(int_raw * p90_factor * padj_scaling, 2)
                    rec["back_post_aerial_win_pct"] = round(float(np.random.normal(59.0, 6.0)), 1)
                    rec["pass_completion_pct"] = round(float(np.random.normal(80.5, 4.0)), 1)
                    rec["prog_distance_carried"] = int(np.random.uniform(1100, 2600))
                    rec["prog_distance_carried_p90"] = round(rec["prog_distance_carried"] * p90_factor, 0)

                elif pos_group == "Center Backs":
                    rec["set_piece_xg"] = round(float(np.random.uniform(0.4, 2.0)), 1)
                    rec["set_piece_xg_p90"] = round(rec["set_piece_xg"] * p90_factor, 2)
                    rec["set_piece_aerial_contacts"] = int(np.random.uniform(10, 32))
                    rec["set_piece_aerial_contacts_p90"] = round(rec["set_piece_aerial_contacts"] * p90_factor, 2)
                    rec["line_breaking_passes"] = int(np.random.uniform(28, 75))
                    rec["line_breaking_passes_p90"] = round(rec["line_breaking_passes"] * p90_factor, 2)
                    rec["prog_pass_distance"] = int(np.random.uniform(1800, 4200))
                    rec["prog_pass_distance_p90"] = round(rec["prog_pass_distance"] * p90_factor, 0)
                    rec["switches_of_play"] = int(np.random.uniform(6, 22))
                    rec["switches_of_play_p90"] = round(rec["switches_of_play"] * p90_factor, 2)
                    rec["aerial_win_pct"] = round(float(np.random.normal(67.0, 5.5)), 1)
                    rec["ground_tackle_win_pct"] = round(float(np.random.normal(70.0, 5.0)), 1)
                    rec["shots_blocked"] = int(np.random.uniform(10, 30))
                    rec["shots_blocked_p90"] = round(rec["shots_blocked"] * p90_factor, 2)
                    rec["clearances"] = int(np.random.uniform(35, 105))
                    rec["clearances_p90"] = round(rec["clearances"] * p90_factor, 2)
                    rec["errors_leading_to_shot"] = int(np.random.poisson(0.8))
                    rec["errors_leading_to_shot_p90"] = round(rec["errors_leading_to_shot"] * p90_factor, 2)
                    rec["buildup_pass_completion_pct"] = round(float(np.random.normal(86.5, 3.5)), 1)
                    rec["long_pass_accuracy_pct"] = round(float(np.random.normal(61.0, 5.5)), 1)

                elif pos_group == "Goalkeepers":
                    rec["passes_40yds_pct"] = round(float(np.random.normal(43.0, 5.0)), 1)
                    rec["launch_pct"] = round(float(np.random.normal(44.0, 6.0)), 1)
                    rec["goal_kick_length_avg"] = round(float(np.random.normal(43.0, 4.0)), 1)
                    rec["psxg_minus_ga"] = round(float(np.random.normal(1.8, 2.5)), 1)
                    rec["psxg_minus_ga_p90"] = round(rec["psxg_minus_ga"] * p90_factor, 2)
                    rec["crosses_stopped_pct"] = round(float(np.random.normal(8.5, 2.0)), 1)
                    rec["sweeper_actions"] = int(np.random.uniform(12, 35))
                    rec["sweeper_actions_p90"] = round(rec["sweeper_actions"] * p90_factor, 2)
                    rec["save_pct"] = round(float(np.random.normal(73.0, 4.0)), 1)
                    rec["pass_completion_under_press_pct"] = round(float(np.random.normal(70.0, 4.5)), 1)
                    rec["clean_sheet_pct"] = round(float(np.random.uniform(18.0, 45.0)), 1)

                players.append(rec)

    return players

def generate_spatial_events(players):
    """
    Generates realistic spatial coordinates (touch zones and shots) for mplsoccer pitch visualizer.
    Pitch system: StatsBomb 120 x 80 coordinate system.
    """
    np.random.seed(101)
    events = []
    
    for p in players:
        p_id = p["sofascore_id"]
        pg = p["pos_group"]
        
        # Center of spatial mass based on position
        if pg == "Forwards / Strikers":
            loc_x = 98.0
            loc_y = 40.0
            spread_x = 14.0
            spread_y = 18.0
            num_touches = 65
            num_shots = np.random.randint(15, 38)
        elif pg == "Wingers / Attacking Mids":
            loc_x = 88.0
            loc_y = 62.0 if "Left" in p.get("secondary_pos", "") or np.random.rand() > 0.5 else 18.0
            spread_x = 18.0
            spread_y = 14.0
            num_touches = 80
            num_shots = np.random.randint(10, 26)
        elif pg == "Central / Holding Mids":
            loc_x = 65.0
            loc_y = 40.0
            spread_x = 22.0
            spread_y = 24.0
            num_touches = 110
            num_shots = np.random.randint(4, 14)
        elif pg == "Fullbacks / Wingbacks":
            loc_x = 62.0
            loc_y = 70.0 if "Left" in p.get("preferred_foot", "") else 10.0
            spread_x = 32.0
            spread_y = 10.0
            num_touches = 90
            num_shots = np.random.randint(2, 9)
        elif pg == "Center Backs":
            loc_x = 35.0
            loc_y = 40.0
            spread_x = 18.0
            spread_y = 22.0
            num_touches = 85
            num_shots = np.random.randint(2, 7)
        else: # Goalkeepers
            loc_x = 10.0
            loc_y = 40.0
            spread_x = 8.0
            spread_y = 16.0
            num_touches = 50
            num_shots = 0

        # Generate sample touch coordinates
        x_touches = np.clip(np.random.normal(loc_x, spread_x, num_touches), 2, 118)
        y_touches = np.clip(np.random.normal(loc_y, spread_y, num_touches), 2, 78)

        # Generate shot coordinates for outfield players
        shots = []
        for _ in range(num_shots):
            sx = np.clip(np.random.normal(loc_x + 8, 10), 85, 119)
            sy = np.clip(np.random.normal(40, 14), 10, 70)
            dist_to_goal = np.sqrt((120 - sx)**2 + (40 - sy)**2)
            shot_xg = np.clip(0.8 / (dist_to_goal + 1.0), 0.02, 0.75)
            # Result outcome
            r_val = np.random.rand()
            if r_val < shot_xg:
                res = "Goal"
            elif r_val < 0.50:
                res = "Saved"
            elif r_val < 0.75:
                res = "Blocked"
            else:
                res = "Missed"
                
            shots.append({
                "x": round(float(sx), 1),
                "y": round(float(sy), 1),
                "xg": round(float(shot_xg), 3),
                "result": res,
                "body_part": np.random.choice(["Right Foot", "Left Foot", "Head"])
            })

        events.append({
            "sofascore_id": p_id,
            "touches_x": json.dumps([round(float(val), 1) for val in x_touches]),
            "touches_y": json.dumps([round(float(val), 1) for val in y_touches]),
            "shots_json": json.dumps(shots)
        })

    return events

def build_database():
    """Initializes and builds the local DuckDB database."""
    print(f"Connecting to DuckDB at: {DB_PATH}")
    if DB_PATH.exists():
        os.remove(DB_PATH)

    con = duckdb.connect(str(DB_PATH))

    # 1. Teams table
    df_teams = pd.DataFrame(CLUBS_DATA)
    con.execute("CREATE TABLE isl_teams AS SELECT * FROM df_teams")
    print(f"Loaded {len(df_teams)} ISL clubs into 'isl_teams'.")

    # 2. Players table
    players_list = generate_full_roster()
    df_players = pd.DataFrame(players_list)
    con.execute("CREATE TABLE isl_players AS SELECT * FROM df_players")
    print(f"Loaded {len(df_players)} ISL players into 'isl_players'.")

    # 3. Spatial events table
    events_list = generate_spatial_events(players_list)
    df_events = pd.DataFrame(events_list)
    con.execute("CREATE TABLE isl_player_events AS SELECT * FROM df_events")
    print(f"Loaded {len(df_events)} player spatial event tracks into 'isl_player_events'.")

    # Create analytical indexes/views
    con.execute("CREATE INDEX idx_player_sofascore ON isl_players(sofascore_id);")
    con.execute("CREATE INDEX idx_player_posgroup ON isl_players(pos_group);")
    con.execute("CREATE INDEX idx_player_team ON isl_players(team);")

    # Check database
    tables = con.execute("SHOW TABLES;").fetchall()
    print("Database tables created successfully:", [t[0] for t in tables])
    con.close()
    print("DuckDB build complete!")

if __name__ == "__main__":
    build_database()
