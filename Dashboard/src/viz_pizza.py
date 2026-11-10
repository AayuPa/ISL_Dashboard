"""
PyPizza Radar Visualizations for Indian Super League (ISL) Player Analytics
Powered by mplsoccer and matplotlib, strictly adhering to the warm earth/mocha palette:
[#815337] [#926a52] [#ab8a76] [#d2b7a7] [#f7e5da]
"""

import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mplsoccer import PyPizza
from typing import Dict, List, Tuple
from src.config import PALETTE, PILLAR_CONFIG

def create_pizza_chart(
    player_name: str,
    team_name: str,
    pos_group: str,
    player_percentiles: Dict[str, Dict[str, dict]],
    minutes: int,
    sofascore_rating: float = None
) -> plt.Figure:
    """
    Generate an mplsoccer PyPizza radar chart with 4-pillar color-coded slices.
    """
    params = []
    values = []
    slice_colors = []
    
    # Pillar color mapping using the required palette
    pillar_colors = {
        "Attacking & Threat": "#815337",        # Deep chestnut
        "Creativity & Progression": "#926a52",  # Warm mocha
        "Defensive & Duels": "#ab8a76",         # Muted caramel
        "Possession & Efficiency": "#63422d"    # Deep espresso / dark walnut
    }
    
    # Flatten pillars in logical order
    for pillar_name in ["Attacking & Threat", "Creativity & Progression", "Defensive & Duels", "Possession & Efficiency"]:
        kpis = player_percentiles.get(pillar_name, {})
        for col, data in kpis.items():
            # Format param name for neat radial display
            clean_label = data["label"].replace(" / 90", "").replace(" (Shot Quality)", "").replace(" (Shot-Stopping)", "")
            clean_label = clean_label.replace("Pass Comp % under Pressure", "Pass % vs Press").replace("Pass Comp % under High Press", "Press Pass %")
            params.append(clean_label)
            values.append(int(round(data["pct"])))
            slice_colors.append(pillar_colors[pillar_name])
            
    if not params:
        # Fallback empty figure if no metrics
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.text(0.5, 0.5, "Insufficient KPI data for radar", ha="center", va="center")
        return fig
    
    # Instantiate PyPizza with light aesthetic styling
    baker = PyPizza(
        params=params,
        background_color=PALETTE["bg_secondary"],
        straight_line_color=PALETTE["border"],
        straight_line_lw=1.0,
        last_circle_lw=1.2,
        last_circle_color=PALETTE["primary"],
        other_circle_lw=0.8,
        other_circle_ls="--",
        other_circle_color=PALETTE["border"],
        inner_circle_size=12
    )
    
    fig, ax = baker.make_pizza(
        values,
        figsize=(8.5, 9.0),
        param_location=112,
        slice_colors=slice_colors,
        value_colors=[PALETTE["text_dark"]] * len(values),
        value_bck_colors=slice_colors,
        kwargs_slices=dict(
            edgecolor=PALETTE["bg_secondary"],
            zorder=2,
            linewidth=1.2
        ),
        kwargs_params=dict(
            color=PALETTE["text_dark"],
            fontsize=9.5,
            fontweight="semibold",
            va="center"
        ),
        kwargs_values=dict(
            color=PALETTE["text_dark"],
            fontsize=8.5,
            fontweight="bold",
            zorder=3,
            bbox=dict(
                edgecolor=PALETTE["border"],
                facecolor=PALETTE["light_card"],
                boxstyle="round,pad=0.25",
                lw=0.8
            )
        )
    )
    
    # Title and Subtitle with dark typography
    title_text = f"{player_name} • {team_name}"
    rating_str = f" | Sofascore Rating: {sofascore_rating:.2f}" if sofascore_rating else ""
    subtitle_text = f"Positional Percentile Ranks vs ISL {pos_group} (Min. {minutes} Mins Played){rating_str}"
    
    fig.text(
        0.515, 0.97, title_text,
        size=15, ha="center", color=PALETTE["text_dark"], weight="bold"
    )
    fig.text(
        0.515, 0.942, subtitle_text,
        size=9.5, ha="center", color=PALETTE["text_muted"]
    )
    
    # Pillar Legend at bottom
    legend_elements = [
        ("Attacking", "#815337"),
        ("Creativity", "#926a52"),
        ("Defending", "#ab8a76"),
        ("Possession", "#63422d")
    ]
    legend_x = 0.22
    for name, col in legend_elements:
        fig.patches.extend([
            plt.Rectangle(
                (legend_x, 0.02), 0.035, 0.018,
                fill=True, color=col, transform=fig.transFigure, figure=fig,
                edgecolor=PALETTE["border"], lw=0.5
            )
        ])
        fig.text(
            legend_x + 0.045, 0.022, name,
            size=9, color=PALETTE["text_dark"], weight="medium", transform=fig.transFigure
        )
        legend_x += 0.16
        
    return fig

def create_comparison_radar(
    p1_name: str, p1_vals: List[float],
    p2_name: str, p2_vals: List[float],
    params: List[str],
    pos_group: str
) -> plt.Figure:
    """
    Generate an overlaid comparison PyPizza chart for two players.
    """
    clean_params = [p.replace(" / 90", "").replace(" (Shot Quality)", "") for p in params]
    
    baker = PyPizza(
        params=clean_params,
        background_color=PALETTE["bg_secondary"],
        straight_line_color=PALETTE["border"],
        straight_line_lw=1.0,
        last_circle_lw=1.2,
        last_circle_color=PALETTE["primary"],
        other_circle_lw=0.8,
        other_circle_ls="--",
        other_circle_color=PALETTE["border"],
        inner_circle_size=12
    )
    
    fig, ax = baker.make_pizza(
        p1_vals,
        compare_values=p2_vals,
        figsize=(8.5, 9.0),
        param_location=112,
        kwargs_slices=dict(
            facecolor=PALETTE["primary"],
            alpha=0.45,
            edgecolor=PALETTE["primary"],
            zorder=2,
            linewidth=1.2
        ),
        kwargs_compare=dict(
            facecolor=PALETTE["tertiary"],
            alpha=0.45,
            edgecolor=PALETTE["tertiary"],
            zorder=2,
            linewidth=1.2
        ),
        kwargs_params=dict(
            color=PALETTE["text_dark"],
            fontsize=9.5,
            fontweight="semibold",
            va="center"
        ),
        kwargs_values=dict(
            color=PALETTE["text_dark"],
            fontsize=8,
            fontweight="bold",
            zorder=3,
            bbox=dict(
                edgecolor=PALETTE["primary"],
                facecolor=PALETTE["light_card"],
                boxstyle="round,pad=0.2",
                lw=0.8
            )
        ),
        kwargs_compare_values=dict(
            color=PALETTE["text_dark"],
            fontsize=8,
            fontweight="bold",
            zorder=3,
            bbox=dict(
                edgecolor=PALETTE["tertiary"],
                facecolor=PALETTE["white"],
                boxstyle="round,pad=0.2",
                lw=0.8
            )
        )
    )
    
    # Legend & header
    fig.text(
        0.515, 0.97, f"{p1_name} (Brown) vs {p2_name} (Tan)",
        size=14, ha="center", color=PALETTE["text_dark"], weight="bold"
    )
    fig.text(
        0.515, 0.942, f"Positional Percentile Comparison • ISL {pos_group}",
        size=9.5, ha="center", color=PALETTE["text_muted"]
    )
    
    return fig
