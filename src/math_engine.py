"""
Mathematical and Statistical Engine for Indian Super League (ISL) Player Analytics
Implements Possession Adjustment (PAdj), empirical CDF percentile ranks,
Z-scores, sigmoidal normalization, and multi-pillar aggregations.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple
from src.config import POSITION_KPIS

def calculate_padj(stat_val: float, team_poss: float, method: str = "sigmoid") -> float:
    """
    Calculate Possession-Adjusted (PAdj) defensive metric.
    
    Parameters:
    - stat_val: Unadjusted metric per 90 (e.g. Tackles, Interceptions)
    - team_poss: Team's average possession percentage (0-100)
    - method: 'linear' (StatsBomb baseline) or 'sigmoid' (logistic decay)
    """
    if pd.isna(stat_val) or pd.isna(team_poss):
        return np.nan
    
    opp_poss = 100.0 - team_poss
    if opp_poss <= 0:
        return stat_val
    
    if method == "linear":
        # Standard Trainor linear scaling: stat * (50 / opp_poss)
        adj_factor = 50.0 / opp_poss
        return float(stat_val * adj_factor)
    else:
        # Logistic / Sigmoidal adjustment curve centered at 50% possession
        # Adjusts smoothly and avoids extreme asymptotes at 20% or 80%
        k = 0.08
        sigmoid_weight = 2.0 / (1.0 + np.exp(-k * (50.0 - opp_poss)))
        return float(stat_val * sigmoid_weight)

def compute_percentile_rank(
    val: float,
    cohort_series: pd.Series,
    higher_better: bool = True
) -> float:
    """
    Calculate the percentile rank of a player's metric within their positional cohort.
    Uses empirical Cumulative Distribution Function (CDF) with mid-point adjustment.
    """
    if pd.isna(val):
        return 50.0
    
    valid_series = cohort_series.dropna()
    n = len(valid_series)
    if n == 0:
        return 50.0
    
    less_count = (valid_series < val).sum()
    equal_count = (valid_series == val).sum()
    
    # Empirical mid-point formula
    pct = ((less_count + 0.5 * equal_count) / n) * 100.0
    
    if not higher_better:
        # Invert percentile if lower value is superior (turnovers, dispossessed, errors)
        pct = 100.0 - pct
        
    # Clip between 1st and 99th percentile for visual aesthetic in radars
    return float(np.clip(pct, 1.0, 99.0))

def compute_z_score(val: float, cohort_series: pd.Series) -> float:
    """Calculate the standard score (z-score) relative to the positional cohort."""
    valid_series = cohort_series.dropna()
    if len(valid_series) < 2 or pd.isna(val):
        return 0.0
    mean = valid_series.mean()
    std = valid_series.std(ddof=1)
    if std == 0 or pd.isna(std):
        return 0.0
    return float((val - mean) / std)

def get_player_percentiles_for_position(
    player_row: pd.Series,
    cohort_df: pd.DataFrame,
    pos_group: str
) -> Dict[str, Dict[str, dict]]:
    """
    Calculate percentile ranks for all 4 analytical pillars for a player
    evaluated against their specific position cohort.
    
    Returns structured dict:
    {
       "Attacking & Threat": {
           "goals_p90": {"label": "Goals / 90", "raw": 0.65, "unit": "/90", "pct": 92.4, "z": 1.7},
           ...
       },
       ...
    }
    """
    if pos_group not in POSITION_KPIS:
        return {}
    
    pillars_def = POSITION_KPIS[pos_group]
    results = {}
    
    for pillar_name, kpi_list in pillars_def.items():
        results[pillar_name] = {}
        for kpi in kpi_list:
            col = kpi["col"]
            higher_better = kpi["higher_better"]
            raw_val = player_row.get(col, np.nan)
            
            if col in cohort_df.columns:
                cohort_series = cohort_df[col]
                pct = compute_percentile_rank(raw_val, cohort_series, higher_better)
                z = compute_z_score(raw_val, cohort_series)
            else:
                pct = 50.0
                z = 0.0
                
            results[pillar_name][col] = {
                "label": kpi["label"],
                "raw": raw_val,
                "unit": kpi["unit"],
                "pct": round(pct, 1),
                "z": round(z, 2),
                "desc": kpi["desc"],
                "higher_better": higher_better
            }
            
    return results

def compute_pillar_scores(player_percentiles: Dict[str, Dict[str, dict]]) -> Dict[str, float]:
    """
    Compute aggregate pillar score (0-100) for each of the 4 pillars.
    """
    scores = {}
    for pillar, kpis in player_percentiles.items():
        if not kpis:
            scores[pillar] = 0.0
            continue
        pcts = [item["pct"] for item in kpis.values() if not pd.isna(item["pct"])]
        scores[pillar] = round(float(np.mean(pcts)), 1) if pcts else 50.0
    return scores

def compute_archetype_fit(player_row: pd.Series, cohort_df: pd.DataFrame, weights: Dict[str, float]) -> float:
    """
    Compute 0-100 fit score for a specific tactical archetype based on weighted percentile scores.
    """
    fit_score = 0.0
    total_w = sum(weights.values())
    
    for col, w in weights.items():
        raw_val = player_row.get(col, np.nan)
        if col in cohort_df.columns:
            pct = compute_percentile_rank(raw_val, cohort_df[col], higher_better=True)
        else:
            pct = 50.0
        fit_score += (pct * (w / total_w))
        
    return round(fit_score, 1)
