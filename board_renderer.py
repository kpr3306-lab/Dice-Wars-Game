"""
Renders the campaign map as a Plotly figure: each territory is drawn as its
actual Voronoi-clipped polygon (same geometry data as the original Canvas
version), colored by owner, labeled with its dice count.

On top of the polygons sits a single marker trace, one point per territory,
centered on each polygon's centroid. That marker trace is what the app
listens to via Streamlit's `on_select="rerun"` -- polygons drawn with
fill="toself" aren't click-selectable in Plotly, but markers are, so the
dice-stack chip showing each territory's dice count doubles as its click
target. Selecting a territory (as an attack source, or as a valid target
once a source is chosen) is expressed purely through this figure's styling
-- brighter fill + thicker brass ring -- so the whole click-to-attack flow
needs no extra widgets.

The map itself is generated with random interior holes (see
generate_maps.py) -- cells deliberately left out of the Voronoi tiling so
the island has lake-like gaps in it, the way the original Dice Wars board
does. Those gaps are painted as a muted "unclaimed" water tone, drawn once
as the full island silhouette *behind* every territory polygon, so a hole
reads as a gap in the land rather than a transparent hitbox.
"""
import random
import plotly.graph_objects as go
from theme import OWNER_COLOR, OWNER_COLOR_LT, BRASS_LT, INK

WATER_COLOR = "#17222c"
PLOT_BG = "#0e141d"

# Unicode "die face" glyphs, U+2680-U+2685 (one through six pips). Only used
# for visual flavor -- which face shows has no gameplay meaning, it's purely
# "what a little stack of n dice looks like" -- so the choice is seeded by
# (territory id, dice count) to stay stable across reruns and only change
# when the dice count itself actually changes.
DICE_GLYPHS = ["\u2680", "\u2681", "\u2682", "\u2683", "\u2684", "\u2685"]
DICE_PER_ROW = 3


def _dice_stack_text(tid, n):
    rnd = random.Random(tid * 97 + n * 131)
    faces = [rnd.choice(DICE_GLYPHS) for _ in range(n)]
    rows = ["".join(faces[i:i + DICE_PER_ROW]) for i in range(0, len(faces), DICE_PER_ROW)]
    return "<br>".join(rows), len(rows)


def build_board_figure(state_dict, selected_id=None, valid_targets=None):
    valid_targets = valid_targets or set()
    fig = go.Figure()

    fig.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor="rgba(0,0,0,0)")

    # Water/gap backdrop: the island's full silhouette, painted once, behind
    # every territory. Any hole left by the map generator shows through as
    # this color instead of either player's, reading as a lake/gap.
    island = state_dict.get("island_outline")
    if island:
        ix = [p[0] for p in island] + [island[0][0]]
        iy = [-p[1] for p in island] + [-island[0][1]]
        fig.add_trace(go.Scatter(
            x=ix, y=iy, fill="toself", fillcolor=WATER_COLOR,
            line=dict(color="rgba(0,0,0,0)", width=0),
            mode="lines", hoverinfo="skip", showlegend=False,
        ))

    marker_x, marker_y, marker_text, marker_customdata = [], [], [], []
    marker_fill, marker_line_color, marker_line_width, marker_size, marker_hover = [], [], [], [], []
    marker_font_size = []

    for tid_str, t in state_dict["territories"].items():
        tid = t["id"]
        poly = t["polygon"]
        xs = [p[0] for p in poly] + [poly[0][0]]
        ys = [p[1] for p in poly] + [poly[0][1]]
        # flip y for natural screen orientation (Plotly y-up, our data y-down)
        ys = [-y for y in ys]

        base_color = OWNER_COLOR[t["owner"]]
        light_color = OWNER_COLOR_LT[t["owner"]]
        is_selected = tid == selected_id
        is_target = tid in valid_targets

        poly_line_color = "#fff6e0" if is_selected else (BRASS_LT if is_target else INK)
        poly_line_width = 3 if is_selected else (2.5 if is_target else 1)

        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill="toself",
            fillcolor=light_color if is_selected else base_color,
            line=dict(color=poly_line_color, width=poly_line_width),
            mode="lines",
            hoverinfo="skip",
            showlegend=False,
        ))

        cx, cy = t["centroid"][0], -t["centroid"][1]
        marker_x.append(cx)
        marker_y.append(cy)
        stack_text, n_rows = _dice_stack_text(tid, t["dice"])
        marker_text.append(stack_text)
        marker_customdata.append([tid])
        owner_label = "You" if t["owner"] == "human" else "AI"
        marker_hover.append(f"Territory {tid} \u2014 {owner_label} \u2014 {t['dice']} dice")

        base_size = 20 + n_rows * 15
        if is_selected:
            marker_fill.append("rgba(255,246,224,0.95)")
            marker_line_color.append("#fff6e0")
            marker_line_width.append(3)
            marker_size.append(base_size + 6)
        elif is_target:
            marker_fill.append("rgba(224,187,99,0.92)")
            marker_line_color.append(BRASS_LT)
            marker_line_width.append(3)
            marker_size.append(base_size + 4)
        else:
            marker_fill.append("rgba(18,13,9,0.88)")
            marker_line_color.append("rgba(224,187,99,0.6)")
            marker_line_width.append(1)
            marker_size.append(base_size)
        marker_font_size.append(12 if n_rows <= 2 else 10.5)

        fig.add_annotation(
            x=cx, y=cy - (base_size / 2) - 9, text=f"T{tid}", showarrow=False,
            font=dict(color="#8a93a8", size=9), opacity=0.85,
        )

    text_color = [
        "#1c1408" if (f.startswith("rgba(255") or f.startswith("rgba(224")) else "#f3e6c8"
        for f in marker_fill
    ]

    fig.add_trace(go.Scatter(
        x=marker_x, y=marker_y, mode="markers+text",
        text=marker_text, textposition="middle center",
        textfont=dict(color=text_color, size=marker_font_size, family="JetBrains Mono, monospace"),
        marker=dict(
            size=marker_size, color=marker_fill,
            line=dict(color=marker_line_color, width=marker_line_width),
        ),
        customdata=marker_customdata,
        hoverinfo="text", hovertext=marker_hover,
        showlegend=False,
        name="territories",
    ))

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=560,
        dragmode=False,
        clickmode="event+select",
    )
    return fig
