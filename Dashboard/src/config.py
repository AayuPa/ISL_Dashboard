"""
Central Configuration for Indian Super League (ISL) Player Analytics Platform
Defines the required color palette, position-group KPI hierarchies,
pillar definitions, and club metadata.
"""

# Palette requested by user:
# [#815337] [#926a52] [#ab8a76] [#d2b7a7] [#f7e5da]
# Font: Dark (#231812) | Background: Light (#FDFBF9 / #FAF6F3)
PALETTE = {
    "primary": "#815337",        # Deep Roasted Chestnut / Espresso
    "secondary": "#926a52",      # Warm Mocha / Walnut
    "tertiary": "#ab8a76",       # Muted Caramel / Latte
    "accent": "#d2b7a7",         # Soft Sand / Light Tan
    "light_card": "#f7e5da",     # Warm Cream / Biscuit surface
    "bg_main": "#FDFBF9",        # Pure warm off-white background
    "bg_secondary": "#FAF6F3",   # Light canvas background
    "text_dark": "#231812",      # Deep Espresso Dark Font
    "text_muted": "#6b5446",     # Muted warm font
    "border": "#d2b7a7",         # Soft card border
    "white": "#FFFFFF",
    "green_accent": "#5b7553",   # Subtle muted green for positive deltas
    "red_accent": "#9d4b3b"      # Subtle muted terra cotta for negative deltas
}

# 4 Pillars of Football Analytics mapped to user color palette
PILLAR_CONFIG = {
    "Attacking & Threat": {
        "color": "#815337",
        "icon": "⚡",
        "bg": "#f7e5da",
        "desc": "Direct goal scoring probability, finishing value, and box penetration."
    },
    "Creativity & Progression": {
        "color": "#926a52",
        "icon": "🪄",
        "bg": "#f7e5da",
        "desc": "Chance creation, progressive passing, take-ons, and territorial territory gain."
    },
    "Defensive & Duels": {
        "color": "#ab8a76",
        "icon": "🛡️",
        "bg": "#f7e5da",
        "desc": "Ball-winning, duels, pressure intensity, and defensive intervention."
    },
    "Possession & Efficiency": {
        "color": "#63422d",
        "icon": "🎯",
        "bg": "#f7e5da",
        "desc": "Ball retention, passing accuracy, turnover avoidance, and transition stability."
    }
}

# Position Group Definitions with exact KPIs required by user prompt
POSITION_KPIS = {
    "Forwards / Strikers": {
        "Attacking & Threat": [
            {"label": "Goals / 90", "col": "goals_p90", "unit": "/90", "higher_better": True, "desc": "Total non-shootout goals scored per 90 minutes."},
            {"label": "Non-Penalty xG / 90", "col": "npxg_p90", "unit": "/90", "higher_better": True, "desc": "Expected goals from open-play & set-play shots excluding penalties."},
            {"label": "Post-Shot xG (PSxG)", "col": "psxg", "unit": "val", "higher_better": True, "desc": "xG calculated based on trajectory, velocity, and goal placement post-strike."},
            {"label": "Shots on Target %", "col": "shots_on_target_pct", "unit": "%", "higher_better": True, "desc": "Percentage of total attempts directed on target."}
        ],
        "Creativity & Progression": [
            {"label": "xG Assisted (xGA) / 90", "col": "xga_p90", "unit": "/90", "higher_better": True, "desc": "Expected goals created via passes leading directly to shots."},
            {"label": "Shot-Creating Actions / 90", "col": "sca_p90", "unit": "/90", "higher_better": True, "desc": "The two offensive actions leading directly to a shot."},
            {"label": "Touches in Box / 90", "col": "touches_in_box_p90", "unit": "/90", "higher_better": True, "desc": "Total ball touches inside opponent's 18-yard penalty area."}
        ],
        "Defensive & Duels": [
            {"label": "Final-Third Tackles", "col": "final_third_tackles", "unit": "tot", "higher_better": True, "desc": "Tackles won in the opponent defensive third."},
            {"label": "High-Intensity Pressures / 90", "col": "high_intensity_pressures_p90", "unit": "/90", "higher_better": True, "desc": "Pressuring events closing down player in possession at high velocity."},
            {"label": "Aerial Win %", "col": "aerial_win_pct", "unit": "%", "higher_better": True, "desc": "Percentage of contested aerial duels won."}
        ],
        "Possession & Efficiency": [
            {"label": "Goal Conversion %", "col": "conversion_rate_pct", "unit": "%", "higher_better": True, "desc": "Goals scored divided by total shot attempts."},
            {"label": "npxG per Shot (Shot Quality)", "col": "npxg_per_shot", "unit": "xG/sh", "higher_better": True, "desc": "Average non-penalty expected goal value per attempt."},
            {"label": "Offsides / 90", "col": "offsides_p90", "unit": "/90", "higher_better": False, "desc": "Offside infringements flagged per 90 (lower is better)."}
        ]
    },
    "Wingers / Attacking Mids": {
        "Attacking & Threat": [
            {"label": "npxG + xGA / 90", "col": "npxg_plus_xga_p90", "unit": "/90", "higher_better": True, "desc": "Combined non-penalty goal threat and shot generation rate."},
            {"label": "Goal-Creating Actions / 90", "col": "gca_p90", "unit": "/90", "higher_better": True, "desc": "The two offensive actions leading directly to a goal."},
            {"label": "Box Entries / 90", "col": "box_entries_p90", "unit": "/90", "higher_better": True, "desc": "Passes and carries that penetrate the opponent penalty box."}
        ],
        "Creativity & Progression": [
            {"label": "Key Passes / 90", "col": "key_passes_p90", "unit": "/90", "higher_better": True, "desc": "Passes that directly result in an assist to a shot."},
            {"label": "Progressive Carries / 90", "col": "progressive_carries_p90", "unit": "/90", "higher_better": True, "desc": "Carries moving the ball >= 10m towards opponent goal or into box."},
            {"label": "Successful Take-On %", "col": "takeon_success_pct", "unit": "%", "higher_better": True, "desc": "Percentage of 1v1 dribbles successfully beating the defender."},
            {"label": "Cross Completion %", "col": "cross_completion_pct", "unit": "%", "higher_better": True, "desc": "Percentage of delivered crosses successfully finding a teammate."}
        ],
        "Defensive & Duels": [
            {"label": "Counter-Pressures / 90", "col": "counter_pressures_p90", "unit": "/90", "higher_better": True, "desc": "Pressures triggered within 5 seconds of turnover."},
            {"label": "Recoveries in Att. 3rd / 90", "col": "recoveries_att_third_p90", "unit": "/90", "higher_better": True, "desc": "Loose balls recovered in the opponent final third."}
        ],
        "Possession & Efficiency": [
            {"label": "Final Third Pass Comp %", "col": "final_third_pass_pct", "unit": "%", "higher_better": True, "desc": "Pass completion rate inside the opponent's defensive 35 meters."},
            {"label": "Dispossessed / 90", "col": "dispossessed_p90", "unit": "/90", "higher_better": False, "desc": "Times stripped of the ball by tackle (lower is better)."},
            {"label": "Prog. Passes Received / 90", "col": "prog_passes_received_p90", "unit": "/90", "higher_better": True, "desc": "Completed progressive passes received in attacking zones."}
        ]
    },
    "Central / Holding Mids": {
        "Attacking & Threat": [
            {"label": "Late Box Arrivals / 90", "col": "late_box_arrivals_p90", "unit": "/90", "higher_better": True, "desc": "Secondary surge entries into box to meet cutbacks or second balls."},
            {"label": "Long-Range Shot xG", "col": "long_range_shot_xg", "unit": "xG", "higher_better": True, "desc": "Cumulative expected goals generated from shots outside 18 yards."}
        ],
        "Creativity & Progression": [
            {"label": "Progressive Passes / 90", "col": "progressive_passes_p90", "unit": "/90", "higher_better": True, "desc": "Passes moving ball >= 10m towards opponent goal."},
            {"label": "Passes to Final Third / 90", "col": "passes_to_final_third_p90", "unit": "/90", "higher_better": True, "desc": "Completed passes played from middle/defensive into final third."},
            {"label": "Deep Completions", "col": "deep_completions", "unit": "tot", "higher_better": True, "desc": "Non-cross completed passes targeted within 20m of opponent goal."},
            {"label": "Through Balls / 90", "col": "through_balls_p90", "unit": "/90", "higher_better": True, "desc": "Passes sent between defenders into open space behind the defensive line."}
        ],
        "Defensive & Duels": [
            {"label": "PAdj T+I / 90", "col": "padj_tackles_interceptions_p90", "unit": "/90", "higher_better": True, "desc": "Possession-Adjusted Tackles + Interceptions normalized to 50% possession."},
            {"label": "Ball Recoveries / 90", "col": "ball_recoveries_p90", "unit": "/90", "higher_better": True, "desc": "Number of loose ball recoveries won per 90."},
            {"label": "Duel Win %", "col": "duel_win_pct", "unit": "%", "higher_better": True, "desc": "Overall ground and aerial duel winning percentage."}
        ],
        "Possession & Efficiency": [
            {"label": "Pass Comp % under Pressure", "col": "pass_completion_under_pressure_pct", "unit": "%", "higher_better": True, "desc": "Passing success rate while actively pressed by opposing defender."},
            {"label": "Press Resistance %", "col": "press_resistance_pct", "unit": "%", "higher_better": True, "desc": "Percentage of pressured possessions retained without turnover."},
            {"label": "Turnovers / 90", "col": "turnovers_p90", "unit": "/90", "higher_better": False, "desc": "Unforced ball losses due to misplaced passes or bad touches (lower is better)."}
        ]
    },
    "Fullbacks / Wingbacks": {
        "Attacking & Threat": [
            {"label": "xGA / 90", "col": "xga_p90", "unit": "/90", "higher_better": True, "desc": "Expected goals assisted per 90 from flank deliveries & build-up."},
            {"label": "Open-Play Crosses / 90", "col": "open_play_crosses_p90", "unit": "/90", "higher_better": True, "desc": "Completed crosses delivered during active open play."},
            {"label": "Overlapping Runs", "col": "overlapping_runs", "unit": "tot", "higher_better": True, "desc": "Decisive overlap runs made beyond the winger into the final third."}
        ],
        "Creativity & Progression": [
            {"label": "Progressive Carries / 90", "col": "progressive_carries_p90", "unit": "/90", "higher_better": True, "desc": "Ball carries driving play upfield along the sideline or half-space."},
            {"label": "Progressive Passes / 90", "col": "progressive_passes_p90", "unit": "/90", "higher_better": True, "desc": "Line-breaking flank and channel balls moving play forward >= 10m."},
            {"label": "Final-Third Entries / 90", "col": "final_third_entries_p90", "unit": "/90", "higher_better": True, "desc": "Actions carrying or passing the ball into the attacking third."}
        ],
        "Defensive & Duels": [
            {"label": "1v1 Dribble Tackle %", "col": "dribble_tackle_pct", "unit": "%", "higher_better": True, "desc": "Success percentage when tackling opposing dribbler (100 - dribbled past %)."},
            {"label": "PAdj Interceptions / 90", "col": "padj_interceptions_p90", "unit": "/90", "higher_better": True, "desc": "Possession-adjusted interceptions normalized to 50% possession."},
            {"label": "Back-Post Aerial Win %", "col": "back_post_aerial_win_pct", "unit": "%", "higher_better": True, "desc": "Aerial duel winning percentage defending deep crosses at back post."}
        ],
        "Possession & Efficiency": [
            {"label": "Pass Completion %", "col": "pass_completion_pct", "unit": "%", "higher_better": True, "desc": "Overall accurate pass percentage across all zones."},
            {"label": "Prog. Distance Carried / 90", "col": "prog_distance_carried_p90", "unit": "m", "higher_better": True, "desc": "Total progressive distance carried with the ball in meters."}
        ]
    },
    "Center Backs": {
        "Attacking & Threat": [
            {"label": "Set-Piece xG / 90", "col": "set_piece_xg_p90", "unit": "/90", "higher_better": True, "desc": "Expected goals generated from attacking corners and set pieces."},
            {"label": "Set-Piece Aerial Contacts", "col": "set_piece_aerial_contacts", "unit": "tot", "higher_better": True, "desc": "Total first contacts made from attacking corner and free kick deliveries."}
        ],
        "Creativity & Progression": [
            {"label": "Line-Breaking Passes / 90", "col": "line_breaking_passes_p90", "unit": "/90", "higher_better": True, "desc": "Passes that bypass an opposing defensive or midfield line."},
            {"label": "Prog. Pass Distance / 90", "col": "prog_pass_distance_p90", "unit": "m", "higher_better": True, "desc": "Total forward vertical distance of completed passes in meters."},
            {"label": "Switches of Play / 90", "col": "switches_of_play_p90", "unit": "/90", "higher_better": True, "desc": "Passes traveling > 40 yards laterally across the pitch."}
        ],
        "Defensive & Duels": [
            {"label": "Aerial Duel Win %", "col": "aerial_win_pct", "unit": "%", "higher_better": True, "desc": "Percentage of contested aerial duels won in defensive phases."},
            {"label": "Ground Tackle Win %", "col": "ground_tackle_win_pct", "unit": "%", "higher_better": True, "desc": "Success rate in ground challenges and slide/block tackles."},
            {"label": "Shots Blocked / 90", "col": "shots_blocked_p90", "unit": "/90", "higher_better": True, "desc": "Opposing shots on goal blocked per 90."},
            {"label": "Clearances / 90", "col": "clearances_p90", "unit": "/90", "higher_better": True, "desc": "Defensive clearances executed per 90."},
            {"label": "Errors Leading to Shot", "col": "errors_leading_to_shot", "unit": "tot", "higher_better": False, "desc": "Direct defensive errors resulting in opposing shot attempt (lower is better)."}
        ],
        "Possession & Efficiency": [
            {"label": "Build-up Pass Comp %", "col": "buildup_pass_completion_pct", "unit": "%", "higher_better": True, "desc": "Pass accuracy in the first two thirds during constructed build-up."},
            {"label": "Long Pass Accuracy %", "col": "long_pass_accuracy_pct", "unit": "%", "higher_better": True, "desc": "Pass completion rate on deliveries exceeding 30 meters."}
        ]
    },
    "Goalkeepers": {
        "Attacking & Threat": [],  # Goalkeepers have no direct attacking KPI required by user prompt
        "Creativity & Progression": [
            {"label": "Passes > 40 Yds Comp %", "col": "passes_40yds_pct", "unit": "%", "higher_better": True, "desc": "Completion percentage on passes traveling over 40 yards."},
            {"label": "Launch %", "col": "launch_pct", "unit": "%", "higher_better": True, "desc": "Percentage of goal kicks and open-play passes launched long."},
            {"label": "Avg Goal Kick Length", "col": "goal_kick_length_avg", "unit": "m", "higher_better": True, "desc": "Average distance of executed goal kicks in meters."}
        ],
        "Defensive & Duels": [
            {"label": "PSxG+/- / 90 (Shot-Stopping)", "col": "psxg_minus_ga_p90", "unit": "/90", "higher_better": True, "desc": "Post-Shot Expected Goals minus Goals Conceded per 90 (positive = goals saved)."},
            {"label": "Crosses Stopped %", "col": "crosses_stopped_pct", "unit": "%", "higher_better": True, "desc": "Percentage of opponent crosses into the box claimed or punched."},
            {"label": "Sweeper Actions / 90", "col": "sweeper_actions_p90", "unit": "/90", "higher_better": True, "desc": "Defensive interventions made outside the 18-yard penalty box."}
        ],
        "Possession & Efficiency": [
            {"label": "Save %", "col": "save_pct", "unit": "%", "higher_better": True, "desc": "Percentage of shots on target successfully saved."},
            {"label": "Pass Comp % under High Press", "col": "pass_completion_under_press_pct", "unit": "%", "higher_better": True, "desc": "Pass completion rate when closed down by opposing high-press."},
            {"label": "Clean Sheet %", "col": "clean_sheet_pct", "unit": "%", "higher_better": True, "desc": "Percentage of matches completed without conceding a goal."}
        ]
    }
}

# ISL Clubs Metadata
ISL_CLUBS = {
    "Mohun Bagan Super Giant": {"short": "MBSG", "city": "Kolkata", "primary_color": "#815337"},
    "Mumbai City FC": {"short": "MCFC", "city": "Mumbai", "primary_color": "#926a52"},
    "FC Goa": {"short": "FCG", "city": "Goa", "primary_color": "#815337"},
    "Odisha FC": {"short": "OFC", "city": "Bhubaneswar", "primary_color": "#ab8a76"},
    "Kerala Blasters FC": {"short": "KBFC", "city": "Kochi", "primary_color": "#926a52"},
    "Chennaiyin FC": {"short": "CFC", "city": "Chennai", "primary_color": "#815337"},
    "NorthEast United FC": {"short": "NEUFC", "city": "Guwahati", "primary_color": "#926a52"},
    "East Bengal FC": {"short": "EBFC", "city": "Kolkata", "primary_color": "#ab8a76"},
    "Punjab FC": {"short": "PFC", "city": "Mohali", "primary_color": "#815337"},
    "Bengaluru FC": {"short": "BFC", "city": "Bengaluru", "primary_color": "#926a52"},
    "Jamshedpur FC": {"short": "JFC", "city": "Jamshedpur", "primary_color": "#ab8a76"},
    "Mohammedan SC": {"short": "MSC", "city": "Kolkata", "primary_color": "#815337"},
    "Hyderabad FC": {"short": "HFC", "city": "Hyderabad", "primary_color": "#926a52"}
}

# Tactical Archetypes for the Role Finder
TACTICAL_ARCHETYPES = {
    "Target Man / Box Poacher": {
        "pos": "Forwards / Strikers",
        "desc": "Elite penalty box occupancy, high-volume shot quality, and aerial duel dominance.",
        "weights": {"touches_in_box_p90": 0.35, "npxg_per_shot": 0.25, "aerial_win_pct": 0.20, "conversion_rate_pct": 0.20}
    },
    "Complete Dynamic Striker": {
        "pos": "Forwards / Strikers",
        "desc": "Dual threat capable of creating for teammates, leading the press, and finishing clinically.",
        "weights": {"npxg_p90": 0.30, "xga_p90": 0.25, "sca_p90": 0.25, "high_intensity_pressures_p90": 0.20}
    },
    "Inverted Playmaking Winger": {
        "pos": "Wingers / Attacking Mids",
        "desc": "Creative hub cutting inside, creating shot-creating chances and entering the box.",
        "weights": {"key_passes_p90": 0.30, "box_entries_p90": 0.25, "npxg_plus_xga_p90": 0.25, "takeon_success_pct": 0.20}
    },
    "Direct Flank Penetrator": {
        "pos": "Wingers / Attacking Mids",
        "desc": "Speed merchant excelling in progressive carries, 1v1 take-ons, and high-volume crossing.",
        "weights": {"progressive_carries_p90": 0.35, "takeon_success_pct": 0.25, "cross_completion_pct": 0.20, "gca_p90": 0.20}
    },
    "Deep-Lying Controller (Regista)": {
        "pos": "Central / Holding Mids",
        "desc": "Tempo orchestrator with press-resistant passing, deep completions, and final-third entries.",
        "weights": {"progressive_passes_p90": 0.35, "press_resistance_pct": 0.30, "passes_to_final_third_p90": 0.20, "through_balls_p90": 0.15}
    },
    "Ball-Winning Destroyer": {
        "pos": "Central / Holding Mids",
        "desc": "Midfield enforcer breaking up counter-attacks with high PAdj tackles, recoveries, and duels.",
        "weights": {"padj_tackles_interceptions_p90": 0.40, "ball_recoveries_p90": 0.30, "duel_win_pct": 0.30}
    },
    "Attacking Overlapping Fullback": {
        "pos": "Fullbacks / Wingbacks",
        "desc": "Modern fullback providing flank width, open-play crosses, and progressive carrying.",
        "weights": {"open_play_crosses_p90": 0.30, "progressive_carries_p90": 0.25, "xga_p90": 0.25, "final_third_entries_p90": 0.20}
    },
    "Defensive Lock-Down Fullback": {
        "pos": "Fullbacks / Wingbacks",
        "desc": "1v1 specialist shutting down opposing wingers and winning back-post aerial balls.",
        "weights": {"dribble_tackle_pct": 0.40, "padj_interceptions_p90": 0.35, "back_post_aerial_win_pct": 0.25}
    },
    "Ball-Playing Center Back": {
        "pos": "Center Backs",
        "desc": "Central defender instigating build-up through line-breaking passes, long switches, and progression.",
        "weights": {"line_breaking_passes_p90": 0.35, "prog_pass_distance_p90": 0.25, "buildup_pass_completion_pct": 0.25, "switches_of_play_p90": 0.15}
    },
    "Dominant Box Defender": {
        "pos": "Center Backs",
        "desc": "Traditional physical stopper dominating aerial duels, clearances, and goal-line blocks.",
        "weights": {"aerial_win_pct": 0.35, "clearances_p90": 0.25, "shots_blocked_p90": 0.25, "ground_tackle_win_pct": 0.15}
    },
    "Modern Sweeper Keeper": {
        "pos": "Goalkeepers",
        "desc": "Proactive goalkeeper commanding the penalty area, sweeping outside the box, and distributing under press.",
        "weights": {"sweeper_actions_p90": 0.35, "crosses_stopped_pct": 0.25, "pass_completion_under_press_pct": 0.25, "psxg_minus_ga_p90": 0.15}
    },
    "Elite Shot-Stopper": {
        "pos": "Goalkeepers",
        "desc": "Pure shot-stopping specialist with superior PSxG-over-actual goals prevented.",
        "weights": {"psxg_minus_ga_p90": 0.50, "save_pct": 0.30, "clean_sheet_pct": 0.20}
    }
}
