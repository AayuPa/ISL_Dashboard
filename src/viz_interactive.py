"""
Interactive Plotly Visualizations for Indian Super League (ISL) Player Analytics
Styled strictly according to the warm earth/mocha palette:
[#815337] [#926a52] [#ab8a76] [#d2b7a7] [#f7e5da]
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Optional
from src.config import PALETTE

def apply_clean_theme(fig: go.Figure, height: Optional[int] = None):
    """Applies the warm earth/mocha aesthetic to Plotly figures cleanly without keyword collisions."""
    fig.update_layout(
        paper_bgcolor=PALETTE["bg_main"],
        plot_bgcolor=PALETTE["bg_secondary"],
        font=dict(color=PALETTE["text_dark"], family="sans-serif"),
        margin=dict(l=40, r=40, t=50, b=40),
        height=height
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=PALETTE["border"],
        gridwidth=0.6,
        zeroline=False,
        tickfont=dict(color=PALETTE["text_dark"])
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=PALETTE["border"],
        gridwidth=0.6,
        zeroline=False,
        tickfont=dict(color=PALETTE["text_dark"])
    )
    return fig

def plot_quadrant_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_label: str,
    y_label: str,
    title: str,
    highlight_player: Optional[str] = None
) -> go.Figure:
    """
    Generate an interactive 2D quadrant scatter plot with median dividing lines and custom tooltips.
    """
    clean_df = df.dropna(subset=[x_col, y_col]).copy()
    if clean_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data for selected axes", showarrow=False)
        return apply_clean_theme(fig)
    
    x_med = clean_df[x_col].median()
    y_med = clean_df[y_col].median()
    
    fig = go.Figure()
    
    # 1. Base cohort scatter points
    cohort_df = clean_df if not highlight_player else clean_df[clean_df["name"] != highlight_player]
    
    fig.add_trace(go.Scatter(
        x=cohort_df[x_col],
        y=cohort_df[y_col],
        mode="markers+text",
        marker=dict(
            size=10,
            color=PALETTE["tertiary"],
            opacity=0.8,
            line=dict(width=1, color=PALETTE["secondary"])
        ),
        text=cohort_df["name"],
        textposition="top center",
        textfont=dict(size=9, color=PALETTE["text_muted"]),
        customdata=cohort_df[["team_short", "minutes", "sofascore_rating"]],
        hovertemplate="<b>%{text}</b> (%{customdata[0]})<br>" +
                      f"{x_label}: <b>%{{x:.2f}}</b><br>" +
                      f"{y_label}: <b>%{{y:.2f}}</b><br>" +
                      "Minutes: %{customdata[1]} | Sofascore: %{customdata[2]:.2f}<extra></extra>",
        name="Cohort Players"
    ))
    
    # 2. Highlighted target player
    if highlight_player and highlight_player in clean_df["name"].values:
        target_row = clean_df[clean_df["name"] == highlight_player].iloc[0]
        fig.add_trace(go.Scatter(
            x=[target_row[x_col]],
            y=[target_row[y_col]],
            mode="markers+text",
            marker=dict(
                size=16,
                color=PALETTE["primary"],
                symbol="star",
                line=dict(width=2, color="#231812")
            ),
            text=[f"<b>{highlight_player}</b>"],
            textposition="top right",
            textfont=dict(size=11, color=PALETTE["primary"]),
            customdata=[[target_row["team_short"], target_row["minutes"], target_row["sofascore_rating"]]],
            hovertemplate="⭐ <b>%{text}</b> (%{customdata[0]})<br>" +
                          f"{x_label}: <b>%{{x:.2f}}</b><br>" +
                          f"{y_label}: <b>%{{y:.2f}}</b><br>" +
                          "Minutes: %{customdata[1]} | Sofascore: %{customdata[2]:.2f}<extra></extra>",
            name=highlight_player
        ))
        
    # Median reference quadrant lines
    fig.add_vline(x=x_med, line_dash="dash", line_color=PALETTE["accent"], line_width=1.2)
    fig.add_hline(y=y_med, line_dash="dash", line_color=PALETTE["accent"], line_width=1.2)
    
    # Quadrant annotations
    x_max = clean_df[x_col].max()
    y_max = clean_df[y_col].max()
    x_min = clean_df[x_col].min()
    y_min = clean_df[y_col].min()
    
    fig.add_annotation(
        x=x_max, y=y_max, text="High Output / Elite",
        showarrow=False, xanchor="right", yanchor="top",
        font=dict(size=9, color=PALETTE["primary"])
    )
    fig.add_annotation(
        x=x_min, y=y_min, text="Developing / Low Volume",
        showarrow=False, xanchor="left", yanchor="bottom",
        font=dict(size=9, color=PALETTE["text_muted"])
    )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=PALETTE["text_dark"], family="sans-serif")),
        showlegend=False
    )
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label)
    
    return apply_clean_theme(fig)

def plot_leaderboard_bar(
    df: pd.DataFrame,
    col: str,
    label: str,
    top_n: int = 10,
    highlight_player: Optional[str] = None
) -> go.Figure:
    """
    Generate a ranked horizontal bar chart for a specific KPI.
    """
    clean_df = df.dropna(subset=[col]).sort_values(by=col, ascending=True).tail(top_n).copy()
    if clean_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No leaderboard data available", showarrow=False)
        return apply_clean_theme(fig)
    
    bar_colors = []
    for name in clean_df["name"]:
        if highlight_player and name == highlight_player:
            bar_colors.append(PALETTE["primary"])
        else:
            bar_colors.append(PALETTE["secondary"])
            
    fig = go.Figure(go.Bar(
        x=clean_df[col],
        y=clean_df["name"],
        orientation="h",
        marker=dict(
            color=bar_colors,
            line=dict(color=PALETTE["border"], width=1)
        ),
        customdata=clean_df[["team_short", "minutes", "sofascore_rating"]],
        hovertemplate="<b>%{y}</b> (%{customdata[0]})<br>" +
                      f"{label}: <b>%{{x:.2f}}</b><br>" +
                      "Minutes: %{customdata[1]}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text=f"ISL Leaderboard • {label}", font=dict(size=12, color=PALETTE["text_dark"]))
    )
    fig.update_xaxes(title_text=label)
    fig.update_yaxes(autorange=True)
    
    return apply_clean_theme(fig, height=max(350, top_n * 26))

def plot_comparison_pillars_bar(
    p1_name: str, p1_scores: dict,
    p2_name: str, p2_scores: dict,
    p3_name: Optional[str] = None, p3_scores: Optional[dict] = None
) -> go.Figure:
    """
    Compare aggregate pillar scores (0-100) between 2 or 3 players.
    """
    pillars = list(p1_scores.keys())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pillars,
        y=[p1_scores.get(p, 50) for p in pillars],
        name=p1_name,
        marker_color=PALETTE["primary"]
    ))
    fig.add_trace(go.Bar(
        x=pillars,
        y=[p2_scores.get(p, 50) for p in pillars],
        name=p2_name,
        marker_color=PALETTE["secondary"]
    ))
    
    if p3_name and p3_scores:
        fig.add_trace(go.Bar(
            x=pillars,
            y=[p3_scores.get(p, 50) for p in pillars],
            name=p3_name,
            marker_color=PALETTE["tertiary"]
        ))
        
    fig.update_layout(
        barmode="group",
        title=dict(text="Analytical Pillar Scores (Percentile Composite 0-100)", font=dict(size=13, color=PALETTE["text_dark"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(range=[0, 100], title_text="Pillar Score")
    
    return apply_clean_theme(fig)
