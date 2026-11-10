"""
Football Pitch Visualizations for Indian Super League (ISL) Player Analytics
Powered by mplsoccer and matplotlib, strictly adhering to the warm earth/mocha palette:
[#815337] [#926a52] [#ab8a76] [#d2b7a7] [#f7e5da]
"""

import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch, VerticalPitch
from typing import List, Dict
from src.config import PALETTE

# Custom sequential colormap based on the user palette
WARM_CMAP = LinearSegmentedColormap.from_list(
    "isl_warm_gradient",
    [PALETTE["light_card"], PALETTE["accent"], PALETTE["tertiary"], PALETTE["secondary"], PALETTE["primary"]],
    N=256
)

def plot_touch_heatmap(
    touches_x: List[float],
    touches_y: List[float],
    player_name: str,
    pos_group: str,
    pitch_type: str = "statsbomb"
) -> plt.Figure:
    """
    Generate an authentic mplsoccer pitch with Kernel Density Estimate (KDE) touch heatmap.
    """
    pitch = Pitch(
        pitch_type=pitch_type,
        pitch_color=PALETTE["bg_secondary"],
        line_color=PALETTE["accent"],
        line_zorder=2,
        linewidth=1.2,
        goal_type="box"
    )
    
    fig, ax = pitch.draw(figsize=(8.5, 5.8))
    fig.patch.set_facecolor(PALETTE["bg_secondary"])
    
    if len(touches_x) >= 10:
        # Smooth Kernel Density Estimate Heatmap
        kde = pitch.kdeplot(
            np.array(touches_x),
            np.array(touches_y),
            ax=ax,
            cmap=WARM_CMAP,
            fill=True,
            levels=40,
            thresh=0.08,
            cut=4,
            alpha=0.82,
            zorder=1
        )
        # Touch scatter points with low opacity for tactical texture
        pitch.scatter(
            np.array(touches_x),
            np.array(touches_y),
            ax=ax,
            s=12,
            color=PALETTE["primary"],
            alpha=0.25,
            zorder=3
        )
    else:
        ax.text(
            60, 40, "No touch event samples recorded for player",
            ha="center", va="center", color=PALETTE["text_muted"], fontsize=11
        )
        
    # Attacking direction arrow
    pitch.lines(
        35, 75, 85, 75,
        ax=ax,
        color=PALETTE["secondary"],
        lw=1.5,
        transparent=False,
        zorder=4
    )
    ax.annotate(
        "Attacking Direction →",
        xy=(60, 77),
        ha="center",
        va="center",
        color=PALETTE["secondary"],
        fontsize=9,
        fontweight="bold"
    )
    
    # Title & Metadata
    total_touches = len(touches_x)
    title_text = f"{player_name} • Positional Touch Density Heatmap"
    subtitle_text = f"Sampled Ball Events ({total_touches} Touches) • Spatial KDE Analysis"
    
    ax.set_title(title_text, color=PALETTE["text_dark"], fontsize=12, fontweight="bold", pad=14)
    fig.text(0.5, 0.90, subtitle_text, ha="center", color=PALETTE["text_muted"], fontsize=8.5)
    
    return fig

def plot_shot_map(
    shots: List[dict],
    player_name: str,
    goals: float = None,
    npxg: float = None
) -> plt.Figure:
    """
    Generate an attacking half-pitch shot map with xG-proportional markers and outcome coding.
    """
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color=PALETTE["bg_secondary"],
        line_color=PALETTE["accent"],
        line_zorder=2,
        linewidth=1.2,
        goal_type="box"
    )
    
    fig, ax = pitch.draw(figsize=(6.5, 5.8))
    fig.patch.set_facecolor(PALETTE["bg_secondary"])
    
    if not shots:
        ax.text(
            40, 100, "No shot attempts recorded",
            ha="center", va="center", color=PALETTE["text_muted"], fontsize=11
        )
        return fig
    
    goal_x, goal_y, goal_s = [], [], []
    saved_x, saved_y, saved_s = [], [], []
    miss_x, miss_y, miss_s = [], [], []
    
    for s in shots:
        x = float(s.get("x", 100))
        y = float(s.get("y", 40))
        xg = float(s.get("xg", 0.08))
        res = str(s.get("result", "Missed")).lower()
        size = max(40, xg * 750)
        
        if "goal" in res:
            goal_x.append(x)
            goal_y.append(y)
            goal_s.append(size)
        elif "save" in res:
            saved_x.append(x)
            saved_y.append(y)
            saved_s.append(size)
        else:
            miss_x.append(x)
            miss_y.append(y)
            miss_s.append(size)
            
    # Scatter shots by category
    if miss_x:
        pitch.scatter(
            miss_x, miss_y, s=miss_s,
            ax=ax, color=PALETTE["light_card"], edgecolor=PALETTE["accent"],
            alpha=0.75, lw=1.2, zorder=3, label="Off Target / Blocked"
        )
    if saved_x:
        pitch.scatter(
            saved_x, saved_y, s=saved_s,
            ax=ax, color=PALETTE["secondary"], edgecolor=PALETTE["bg_secondary"],
            alpha=0.85, lw=1.2, zorder=4, label="Saved"
        )
    if goal_x:
        pitch.scatter(
            goal_x, goal_y, s=goal_s,
            ax=ax, color=PALETTE["primary"], edgecolor="#231812",
            alpha=0.95, lw=1.5, marker="*", zorder=5, label="Goal"
        )
        
    # Legend
    legend = ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=3,
        facecolor=PALETTE["bg_secondary"],
        edgecolor=PALETTE["border"],
        fontsize=8.5,
        framealpha=0.9
    )
    for text in legend.get_texts():
        text.set_color(PALETTE["text_dark"])
        
    title_text = f"{player_name} • Shot Trajectory & Location Map"
    stat_sub = f"{len(shots)} Total Attempts | {len(goal_x)} Goals"
    if npxg is not None:
        stat_sub += f" | {npxg:.2f} npxG"
        
    ax.set_title(title_text, color=PALETTE["text_dark"], fontsize=11.5, fontweight="bold", pad=12)
    fig.text(0.5, 0.90, stat_sub, ha="center", color=PALETTE["text_muted"], fontsize=8.5)
    
    return fig
