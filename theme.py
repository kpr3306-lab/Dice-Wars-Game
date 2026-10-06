"""
Shared visual theme for the Streamlit rebuild of Dice Wars.
Keeps the same war-room palette as the original Flask/Canvas version:
ink navy, parchment, wax-seal red, steel blue, brass.
"""
import streamlit as st

NAVY = "#171c26"
NAVY2 = "#202838"
NAVY3 = "#2a3448"
PARCHMENT = "#f2ebda"
BRASS = "#c39a3f"
BRASS_LT = "#e0bb63"
SEAL_RED = "#8c3a3a"
SEAL_RED_LT = "#b25050"
STEEL_BLUE = "#3f6b80"
STEEL_BLUE_LT = "#5c8ca3"
INK = "#2b2013"

OWNER_COLOR = {"human": SEAL_RED, "ai": STEEL_BLUE}
OWNER_COLOR_LT = {"human": SEAL_RED_LT, "ai": STEEL_BLUE_LT}
OWNER_LABEL = {"human": "You", "ai": "AI General"}


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Spectral:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Spectral', serif;
        }}
        .stApp {{
            background: radial-gradient(ellipse at 20% 0%, #1b2231 0%, transparent 60%),
                        radial-gradient(ellipse at 80% 100%, #1b2231 0%, transparent 55%),
                        {NAVY};
            color: {PARCHMENT};
        }}
        h1, h2, h3 {{
            font-family: 'Cinzel', serif !important;
            letter-spacing: 0.03em;
            color: {BRASS_LT} !important;
        }}
        .dw-card {{
            background: {PARCHMENT};
            color: {INK};
            border-radius: 6px;
            padding: 16px 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35);
            margin-bottom: 14px;
        }}
        .dw-card h3, .dw-card h4 {{
            color: {"#3a2b16"} !important;
            margin-top: 0;
        }}
        .dw-badge {{
            display: inline-block;
            font-family: 'Spectral', serif;
            font-weight: 600;
            font-size: 0.85rem;
            padding: 4px 12px;
            border-radius: 3px;
            margin-bottom: 8px;
        }}
        .dw-badge.human {{ background: rgba(140,58,58,0.18); color: {SEAL_RED_LT}; border: 1px solid {SEAL_RED}; }}
        .dw-badge.ai {{ background: rgba(63,107,128,0.18); color: {STEEL_BLUE_LT}; border: 1px solid {STEEL_BLUE}; }}

        .dw-thought {{
            border-left: 3px solid {BRASS};
            padding: 6px 12px;
            margin-bottom: 8px;
            background: rgba(255,255,255,0.04);
            border-radius: 0 4px 4px 0;
        }}
        .dw-thought.strategy {{ border-left-color: {BRASS}; }}
        .dw-thought.attack {{ border-left-color: {SEAL_RED}; }}
        .dw-thought.defense {{ border-left-color: {STEEL_BLUE}; }}
        .dw-thought.oracle {{ border-left-color: #8a5cb0; }}
        .dw-thought .tag {{
            font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.65;
        }}
        .dw-thought .headline {{ font-weight: 600; margin: 2px 0; }}
        .dw-thought .detail {{ font-size: 0.85rem; opacity: 0.85; }}

        .die-face {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 40px; height: 40px;
            background: #fff; border-radius: 6px; border: 2px solid {INK};
            font-weight: 700; font-size: 1.1rem; margin: 3px;
            box-shadow: 0 3px 0 rgba(0,0,0,0.25);
        }}
        .die-face.attacker {{ border-color: {SEAL_RED}; color: {SEAL_RED}; }}
        .die-face.defender {{ border-color: {STEEL_BLUE}; color: {STEEL_BLUE}; }}

        .dw-result {{
            font-weight: 600; padding: 10px; border-radius: 4px; text-align: center; margin-top: 8px;
        }}
        .dw-result.win {{ background: rgba(92,122,79,0.18); color: #b7d19f; }}
        .dw-result.lose {{ background: rgba(140,58,58,0.18); color: {SEAL_RED_LT}; }}

        .dw-map-card {{
            background: {PARCHMENT}; border-radius: 6px; padding: 18px; cursor: default;
            box-shadow: 0 8px 24px rgba(0,0,0,0.35); color: {INK}; height: 100%;
        }}

        .dw-hint {{
            font-size: 0.85rem; color: {BRASS_LT}; opacity: 0.9; margin: 4px 0 10px 0;
        }}
        .dw-click-msg {{
            font-size: 0.85rem; padding: 6px 10px; border-radius: 4px; margin: 6px 0 10px 0;
            background: rgba(224,187,99,0.12); border: 1px solid rgba(224,187,99,0.35);
            color: {BRASS_LT};
        }}
        .dw-cheat-row {{
            display:flex; justify-content:space-between; font-size:0.82rem;
            padding: 4px 0; border-bottom: 1px dashed rgba(43,32,19,0.15);
        }}
        .dw-cheat-row:last-child {{ border-bottom: none; }}
        .dw-cheat-rank {{ color: #8a5cb0; font-weight: 700; margin-right: 6px; }}
        .dw-feed-scroll {{
            max-height: 420px; overflow-y: auto; padding-right: 4px;
        }}
        .dw-feed-scroll::-webkit-scrollbar {{ width: 6px; }}
        .dw-feed-scroll::-webkit-scrollbar-thumb {{
            background: rgba(224,187,99,0.35); border-radius: 3px;
        }}

        /* ---------------- centered popup overlay (battle results, ---------------
           "placing reinforcements", etc.) -- fixed positioning takes it out of
           the normal document flow, so it stays centered in the viewport no
           matter where in the page the underlying st.empty() placeholder sits,
           and no scrolling is needed to see it. */
        .dw-overlay-backdrop {{
            position: fixed; inset: 0; z-index: 9999;
            background: rgba(10,13,20,0.72);
            display: flex; align-items: center; justify-content: center;
            animation: dwFadeIn 0.12s ease-out;
        }}
        .dw-overlay-modal {{
            background: {PARCHMENT}; color: {INK};
            border-radius: 10px; padding: 24px 28px;
            width: min(480px, 90vw);
            box-shadow: 0 20px 60px rgba(0,0,0,0.55);
            border: 1px solid rgba(195,154,63,0.5);
            animation: dwPopIn 0.16s ease-out;
        }}
        .dw-overlay-modal h4 {{
            margin-top: 0; color: {"#3a2b16"} !important; font-family: 'Cinzel', serif;
            font-size: 1.05rem; letter-spacing: 0.02em;
        }}
        .dw-overlay-msg {{
            text-align: center; font-size: 1.05rem; font-weight: 600;
            color: {"#3a2b16"}; padding: 10px 0;
        }}
        .dw-overlay-sub {{
            text-align: center; font-size: 0.8rem; color: #6b5a3a; margin-top: -4px;
        }}
        @keyframes dwFadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes dwPopIn {{
            from {{ opacity: 0; transform: scale(0.94) translateY(6px); }}
            to {{ opacity: 1; transform: scale(1) translateY(0); }}
        }}

        /* ---------------- buttons: highlighted when enabled, clearly grayed when not --- */
        div[data-testid="stButton"] button {{
            transition: all 0.12s ease;
            border: 1px solid rgba(224,187,99,0.55) !important;
        }}
        div[data-testid="stButton"] button:not(:disabled) {{
            background: linear-gradient(180deg, rgba(224,187,99,0.22), rgba(195,154,63,0.10)) !important;
            color: {BRASS_LT} !important;
            font-weight: 600;
        }}
        div[data-testid="stButton"] button:not(:disabled):hover {{
            background: linear-gradient(180deg, rgba(224,187,99,0.34), rgba(195,154,63,0.18)) !important;
            border-color: {BRASS_LT} !important;
        }}
        div[data-testid="stButton"] button:disabled {{
            opacity: 0.38 !important;
            border-color: rgba(255,255,255,0.12) !important;
            background: rgba(255,255,255,0.03) !important;
        }}

        .dw-badge.ai {{ animation: dwPulse 1.6s ease-in-out infinite; }}
        @keyframes dwPulse {{
            0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.55; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand_header():
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom: 4px;">
            <div style="width:26px; height:26px; border:2px solid {BRASS_LT}; border-radius:5px;
                        display:flex; align-items:center; justify-content:center; font-size:0.9rem; color:{BRASS_LT};">
                &#9861;
            </div>
            <span style="font-family:'Cinzel',serif; letter-spacing:0.12em; font-size:1.1rem; color:{BRASS_LT};">
                DICE WARS
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
