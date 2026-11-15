"""
Shared visual theme for the Streamlit rebuild of Dice Wars.
War-room palette -- ink navy, wax-seal red, steel blue, brass -- reworked
as a dark "command console": layered navy surfaces, hairline borders,
brass as the single accent colour.
"""
import streamlit as st

NAVY = "#10151e"
NAVY2 = "#171e2b"
NAVY3 = "#202a3b"
PARCHMENT = "#ede6d4"
MUTED = "#98a1b3"
BRASS = "#c9a24a"
BRASS_LT = "#e3bf6a"
SEAL_RED = "#9e3f3c"
SEAL_RED_LT = "#c35a55"
STEEL_BLUE = "#3b6f88"
STEEL_BLUE_LT = "#5b93ad"
INK = "#1d160d"

OWNER_COLOR = {"human": SEAL_RED, "ai": STEEL_BLUE}
OWNER_COLOR_LT = {"human": SEAL_RED_LT, "ai": STEEL_BLUE_LT}
OWNER_LABEL = {"human": "You", "ai": "AI General"}


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

        :root {{
            --bg: {NAVY}; --s1: {NAVY2}; --s2: {NAVY3};
            --line: rgba(255,255,255,0.07); --line-2: rgba(227,191,106,0.28);
            --text: {PARCHMENT}; --muted: {MUTED};
            --brass: {BRASS}; --brass-lt: {BRASS_LT};
            --red: {SEAL_RED}; --red-lt: {SEAL_RED_LT};
            --blue: {STEEL_BLUE}; --blue-lt: {STEEL_BLUE_LT};
            --radius: 12px;
        }}
        html, body, .stApp, [class*="css"], .stMarkdown, button, input {{
            font-family: 'Inter', system-ui, sans-serif;
        }}
        .stApp {{
            background:
                radial-gradient(1200px 600px at 15% -10%, rgba(201,162,74,0.07), transparent 60%),
                radial-gradient(900px 500px at 100% 110%, rgba(59,111,136,0.10), transparent 60%),
                var(--bg);
            color: var(--text);
        }}
        h1, h2, h3, h4 {{ font-family: 'Cinzel', serif !important; letter-spacing: 0.02em; color: var(--text) !important; }}
        p {{ line-height: 1.55; }}
        b, strong {{ color: var(--text); font-weight: 600; }}
        .mono {{ font-family: 'JetBrains Mono', monospace; }}

        /* ---------------- app chrome ---------------- */
        header[data-testid="stHeader"] {{ display: none; }}
        [data-testid="stDecoration"], footer, #MainMenu, [data-testid="stAppDeployButton"],
        [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
        .block-container {{ padding: 0.9rem 1.5rem 1.2rem !important; max-width: 1440px; }}
        [data-testid="stVerticalBlock"] {{ gap: 0.75rem; }}

        /* ---------------- top bar ---------------- */
        .st-key-dw_topbar {{
            border-bottom: 1px solid var(--line); padding-bottom: 0.6rem; margin-bottom: 0.2rem;
        }}
        .dw-brand {{ display: flex; align-items: center; gap: 10px; white-space: nowrap; }}
        .dw-brand .mark {{
            width: 30px; height: 30px; border-radius: 8px; display: grid; place-items: center;
            background: linear-gradient(145deg, var(--brass-lt), var(--brass)); color: {INK};
            font-size: 1.05rem; box-shadow: 0 4px 14px rgba(201,162,74,0.25);
        }}
        .dw-brand .name {{ font-family: 'Cinzel', serif; font-weight: 700; letter-spacing: 0.16em; font-size: 1.05rem; }}
        .dw-brand .tag {{ font-size: 0.72rem; color: var(--muted); letter-spacing: 0.04em; margin-left: 2px; }}
        [data-testid="stPageLink"] a {{
            border-radius: 8px; padding: 4px 12px; border: 1px solid transparent;
        }}
        [data-testid="stPageLink"] a:hover {{ background: rgba(255,255,255,0.04); }}
        [data-testid="stPageLink"] a[aria-current="page"], [data-testid="stPageLink-NavLink"][aria-current="page"] {{
            background: rgba(227,191,106,0.10); border-color: var(--line-2);
        }}
        [data-testid="stPageLink"] p {{ font-size: 0.88rem; font-weight: 500; }}

        /* ---------------- surfaces ---------------- */
        .dw-card, .st-key-dw_command, .st-key-dw_board, [class*="st-key-dw_map_"] {{
            background: linear-gradient(180deg, rgba(255,255,255,0.025), transparent), var(--s1);
            border: 1px solid var(--line); border-radius: var(--radius);
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        }}
        .dw-card {{ padding: 18px 20px; height: 100%; }}
        .dw-card h3 {{ font-size: 1.02rem; margin: 0 0 8px; color: var(--brass-lt) !important; }}
        .dw-card p {{ font-size: 0.9rem; color: #cfd4de; margin: 0 0 8px; }}
        .dw-card p:last-child {{ margin-bottom: 0; }}
        .st-key-dw_command {{ padding: 16px 18px; gap: 0.6rem; }}
        .st-key-dw_board {{ padding: 6px 6px 8px; }}
        /* Streamlit pulls markdown blocks up by a negative margin meant for a trailing paragraph;
           our HTML blocks have none, so it made text collide with the next widget. */
        .stMarkdown, [data-testid="stMarkdownContainer"] {{ margin-bottom: 0 !important; }}
        .eyebrow {{
            font-size: 0.7rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted);
        }}

        /* ---------------- status ---------------- */
        .dw-turn-row {{ display: flex; align-items: center; justify-content: space-between; }}
        .dw-turn-row .num {{ font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--muted); }}
        .dw-badge {{
            display: inline-flex; align-items: center; gap: 7px; font-weight: 600; font-size: 0.8rem;
            padding: 4px 11px; border-radius: 999px;
        }}
        .dw-badge::before {{ content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }}
        .dw-badge.human {{ background: rgba(158,63,60,0.16); color: var(--red-lt); border: 1px solid rgba(195,90,85,0.45); }}
        .dw-badge.ai {{ background: rgba(59,111,136,0.16); color: var(--blue-lt); border: 1px solid rgba(91,147,173,0.45); }}
        .dw-badge.ai::before {{ animation: dwPulse 1.2s ease-in-out infinite; }}
        .dw-front {{ margin-top: 12px; }}
        .dw-front .head {{ display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--muted); margin-bottom: 5px; }}
        .dw-front .head b {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; }}
        .dw-front .head .h {{ color: var(--red-lt); }}
        .dw-front .head .a {{ color: var(--blue-lt); }}
        .dw-front .bar {{ display: flex; height: 8px; border-radius: 999px; overflow: hidden; gap: 2px; background: var(--s2); }}
        .dw-front .bar span {{ transition: flex-grow 0.4s ease; }}
        .dw-front .bar .h {{ background: linear-gradient(90deg, var(--red), var(--red-lt)); }}
        .dw-front .bar .a {{ background: linear-gradient(90deg, var(--blue-lt), var(--blue)); }}
        .dw-divider {{ height: 1px; background: var(--line); margin: 4px 0 0; }}
        .dw-phase {{ font-weight: 600; font-size: 0.95rem; margin: 2px 0 3px; }}
        .dw-hint {{ font-size: 0.83rem; color: var(--muted); line-height: 1.5; }}
        .dw-hint b {{ color: var(--brass-lt); }}
        .dw-click-msg {{
            font-size: 0.8rem; padding: 7px 10px; border-radius: 8px; margin-top: 8px;
            background: rgba(227,191,106,0.09); border: 1px solid var(--line-2); color: var(--brass-lt);
        }}
        .dw-legend {{ display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; font-size: 0.74rem; color: var(--muted); padding: 2px 0 4px; }}
        .dw-legend i {{ display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; }}

        /* ---------------- agent feed ---------------- */
        .dw-thought {{
            border: 1px solid var(--line); border-left: 3px solid var(--brass);
            padding: 8px 12px; margin-bottom: 8px; background: var(--s1); border-radius: 8px;
        }}
        .dw-thought.attack {{ border-left-color: var(--red-lt); }}
        .dw-thought.defense {{ border-left-color: var(--blue-lt); }}
        .dw-thought.oracle {{ border-left-color: #9a72c4; }}
        .dw-thought .tag {{ font-size: 0.66rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); }}
        .dw-thought .headline {{ font-weight: 600; font-size: 0.86rem; margin: 3px 0 2px; }}
        .dw-thought .detail {{ font-size: 0.78rem; color: var(--muted); line-height: 1.45; }}
        .dw-cheat-row {{
            display: flex; justify-content: space-between; font-size: 0.8rem; padding: 7px 2px;
            border-bottom: 1px solid var(--line);
        }}
        .dw-cheat-row:last-child {{ border-bottom: none; }}
        .dw-cheat-row .mono {{ color: var(--muted); font-size: 0.75rem; }}
        .dw-cheat-rank {{ color: #b796da; font-weight: 700; margin-right: 8px; font-family: 'JetBrains Mono', monospace; }}
        .dw-log {{ font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #c3c9d4; line-height: 1.8; }}
        .dw-empty {{ font-size: 0.82rem; color: var(--muted); padding: 10px 2px; }}

        /* ---------------- tabs ---------------- */
        [data-testid="stTabs"] [role="tablist"] {{ gap: 18px; }}
        [data-testid="stTabs"] button[role="tab"] p {{ font-size: 0.82rem; font-weight: 500; }}
        [data-baseweb="tab-highlight"] {{ background: var(--brass-lt) !important; }}
        [data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(227,191,106,0.25); border-radius: 3px; }}

        /* ---------------- buttons ---------------- */
        div[data-testid="stButton"] button {{
            border-radius: 9px; font-weight: 600; transition: all 0.12s ease; min-height: 2.5rem;
            border: 1px solid var(--line-2); background: rgba(227,191,106,0.06); color: var(--brass-lt);
        }}
        div[data-testid="stButton"] button:hover:not(:disabled) {{ background: rgba(227,191,106,0.14); border-color: var(--brass-lt); color: var(--brass-lt); }}
        div[data-testid="stButton"] button[kind="primary"]:not(:disabled) {{
            background: linear-gradient(180deg, var(--brass-lt), var(--brass)); color: {INK}; border-color: var(--brass-lt);
            box-shadow: 0 6px 18px rgba(201,162,74,0.22);
        }}
        div[data-testid="stButton"] button[kind="primary"]:hover:not(:disabled) {{ filter: brightness(1.07); color: {INK}; }}
        div[data-testid="stButton"] button:disabled {{
            opacity: 0.4; background: transparent; border-color: var(--line); color: var(--muted);
        }}
        div[data-testid="stButton"] button:focus-visible {{ outline: 2px solid var(--brass-lt); outline-offset: 2px; }}
        .st-key-home_btn button {{ min-height: 2.1rem; font-size: 0.82rem; }}

        /* ---------------- map select ---------------- */
        .dw-hero {{ text-align: center; max-width: 720px; margin: 4vh auto 3vh; }}
        .dw-hero h1 {{ font-size: clamp(2rem, 3.8vw, 3rem); line-height: 1.08; margin: 10px 0 12px; }}
        .dw-hero p {{ font-size: 1.02rem; color: var(--muted); margin: 0 auto; max-width: 56ch; }}
        .dw-hero .dw-chip {{ margin: 0 3px; }}
        .dw-chip {{
            display: inline-block; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em;
            padding: 3px 10px; border-radius: 999px; border: 1px solid var(--line-2); color: var(--brass-lt);
            background: rgba(227,191,106,0.06);
        }}
        [class*="st-key-dw_map_"] {{ padding: 22px 22px 18px; transition: transform 0.15s ease, border-color 0.15s ease; }}
        [class*="st-key-dw_map_"]:hover {{ transform: translateY(-3px); border-color: var(--line-2); }}
        .dw-map h3 {{ font-size: 1.3rem; margin: 14px 0 4px; }}
        .dw-map p {{ font-size: 0.88rem; color: var(--muted); margin: 0; min-height: 2.8em; }}
        .dw-map .stats {{ display: flex; gap: 18px; margin-top: 14px; }}
        .dw-map .stat .v {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.15rem; }}
        .dw-map .stat .k {{ font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }}
        .dw-map .scale {{ display: flex; gap: 4px; align-items: flex-end; height: 26px; }}
        .dw-map .scale i {{ width: 8px; border-radius: 2px; background: var(--s2); }}
        .dw-map .scale i.on {{ background: var(--brass); }}

        /* ---------------- doc pages ---------------- */
        .dw-page-head {{ margin: 1.2rem 0 0.4rem; }}
        .dw-page-head h1 {{ font-size: clamp(1.6rem, 2.6vw, 2.2rem); margin: 6px 0 4px; }}
        .dw-page-head p {{ color: var(--muted); margin: 0; max-width: 70ch; }}
        .dw-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; margin-top: 12px; }}
        .dw-section {{ margin: 18px 0 2px; }}
        .dw-steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }}
        .dw-step {{ background: var(--s1); border: 1px solid var(--line); border-radius: var(--radius); padding: 14px 16px; }}
        .dw-step .n {{ font-family: 'JetBrains Mono', monospace; color: var(--brass-lt); font-size: 0.78rem; font-weight: 700; }}
        .dw-step .t {{ font-weight: 600; margin: 4px 0 2px; }}
        .dw-step .d {{ font-size: 0.82rem; color: var(--muted); line-height: 1.45; }}
        .dw-pipeline {{ display: flex; align-items: stretch; gap: 10px; flex-wrap: wrap; }}
        .dw-pipeline .node {{
            flex: 1 1 160px; background: var(--s1); border: 1px solid var(--line); border-radius: var(--radius);
            padding: 14px 16px; border-top: 3px solid var(--c);
        }}
        .dw-pipeline .node .t {{ font-weight: 600; }}
        .dw-pipeline .node .d {{ font-size: 0.8rem; color: var(--muted); margin-top: 2px; }}
        .dw-pipeline .arrow {{ align-self: center; color: var(--muted); font-size: 1.2rem; }}
        .dw-pipeline .node.side {{ border-style: dashed; border-top-style: solid; }}

        /* ---------------- end of match ---------------- */
        .dw-endcard {{ text-align: center; padding: 40px 28px 30px; max-width: 560px; margin: 10vh auto 18px; border-top: 4px solid var(--dw-end); height: auto; }}
        .dw-endcard h1 {{ color: var(--dw-end) !important; font-size: clamp(1.8rem, 4vw, 2.5rem); margin: 8px 0 10px; }}
        .dw-endcard p {{ color: var(--muted); }}

        /* ---------------- centered popup overlay ---------------
           fixed positioning takes it out of the document flow, so it stays
           centered in the viewport wherever its st.empty() placeholder sits. */
        .dw-overlay-backdrop {{
            position: fixed; inset: 0; z-index: 9999; background: rgba(6,9,14,0.68);
            backdrop-filter: blur(3px); display: flex; align-items: center; justify-content: center;
            animation: dwFadeIn 0.12s ease-out;
        }}
        .dw-overlay-modal {{
            background: var(--s1); color: var(--text); border-radius: 16px; padding: 22px 26px;
            width: min(480px, 92vw); box-shadow: 0 24px 70px rgba(0,0,0,0.6);
            border: 1px solid var(--line-2); animation: dwPopIn 0.16s ease-out;
        }}
        .dw-overlay-modal h4 {{ margin: 0 0 4px; font-size: 1rem; color: var(--brass-lt) !important; }}
        .dw-overlay-msg {{ text-align: center; font-size: 1.02rem; font-weight: 600; padding: 8px 0 4px; }}
        .dw-overlay-sub {{ text-align: center; font-size: 0.8rem; color: var(--muted); }}
        .dw-overlay-rows {{ font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; text-align: center; margin-top: 10px; color: #c3c9d4; line-height: 1.8; }}
        .die-face {{
            display: inline-grid; grid-template: repeat(3, 1fr) / repeat(3, 1fr);
            width: 40px; height: 40px; padding: 6px; box-sizing: border-box;
            background: linear-gradient(145deg, #fffaf0, #e6dcc4);
            border-radius: 9px; border: 2px solid; margin: 3px;
            box-shadow: 0 3px 0 rgba(0,0,0,0.35); vertical-align: middle;
        }}
        .die-face i {{ border-radius: 50%; margin: 1.5px; }}
        .die-face i.pip {{ background: currentColor; }}
        .die-face.attacker {{ border-color: var(--red); color: var(--red); }}
        .die-face.defender {{ border-color: var(--blue); color: var(--blue); }}
        .dw-side {{ display: flex; align-items: center; gap: 12px; margin-top: 12px; padding: 8px 10px; border-radius: 10px; background: rgba(255,255,255,0.03); }}
        .dw-side .who {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; min-width: 72px; }}
        .dw-side.attacker .who {{ color: var(--red-lt); }}
        .dw-side.defender .who {{ color: var(--blue-lt); }}
        .dw-side .dice {{ flex: 1; display: flex; flex-wrap: wrap; }}
        .dw-side .total {{ font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 700; min-width: 2.2ch; text-align: right; }}
        .dw-side.attacker .total {{ color: var(--red-lt); }}
        .dw-side.defender .total {{ color: var(--blue-lt); }}
        .dw-result {{ font-weight: 600; padding: 10px; border-radius: 10px; text-align: center; margin-top: 12px; font-size: 0.9rem; }}
        .dw-result.win {{ background: rgba(104,160,98,0.14); color: #9fd193; border: 1px solid rgba(104,160,98,0.4); }}
        .dw-result.lose {{ background: rgba(195,90,85,0.12); color: var(--red-lt); border: 1px solid rgba(195,90,85,0.4); }}

        @keyframes dwFadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes dwPopIn {{ from {{ opacity: 0; transform: scale(0.95) translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
        @keyframes dwPulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{ animation: none !important; transition: none !important; }}
        }}
        @media (max-width: 640px) {{
            .block-container {{ padding: 0.7rem 1rem 1rem !important; }}
            .dw-brand .tag {{ display: none; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand_header():
    """Top bar: brand, page navigation, and a right-hand slot (returned) for a
    page-specific action such as 'Leave match'. Replaces the sidebar nav."""
    with st.container(key="dw_topbar"):
        brand, nav, action = st.columns([1.2, 2, 1], vertical_alignment="center")
        brand.markdown(
            '<div class="dw-brand"><div class="mark">&#9861;</div>'
            '<span class="name">DICE WARS</span><span class="tag">vs. a multi-agent AI</span></div>',
            unsafe_allow_html=True,
        )
        with nav, st.container(horizontal=True, horizontal_alignment="center", gap="small"):
            st.page_link("streamlit_app.py", label="Play")
            st.page_link("pages/1_Instructions.py", label="How to play")
            st.page_link("pages/2_Behind_the_Scenes.py", label="Behind the scenes")
    return action
