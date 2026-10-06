import random
import streamlit as st

from game.engine import GameState, MAPS
from agents.ai_controller import AIController
from agents.oracle_agent import OracleAgent
from theme import inject_css, brand_header, OWNER_LABEL
from board_renderer import build_board_figure
from animation import (
    play_battle_animation, show_reinforcement_overlay, clear_overlay,
    render_thought_html, append_feed,
)

st.set_page_config(page_title="Dice Wars", page_icon="\u2694", layout="wide")
inject_css()

AI = AIController(owner="ai")
ORACLE = OracleAgent(owner="human")

# ---------------------------------------------------------------- session state
DEFAULTS = {
    "game": None,
    "selected_src": None,
    "feed": [],
    "click_message": None,
    "chart_seq": 0,
}
for key, default in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default() if callable(default) else default


def new_game(map_id):
    st.session_state.game = GameState(map_id, seed=random.randint(0, 1_000_000))
    st.session_state.selected_src = None
    st.session_state.feed = []
    st.session_state.click_message = None
    st.session_state.chart_seq += 1


def go_home():
    """Abandon the current match and return to the map-select screen."""
    st.session_state.game = None
    st.session_state.selected_src = None
    st.session_state.feed = []
    st.session_state.click_message = None
    st.session_state.chart_seq += 1


def redraw_board(board_placeholder, state, redraw_key):
    """Redraw the map mid-script (no rerun) so captures and reinforcements are
    visible on the board the instant they happen, not just after the AI's
    whole turn finishes. Non-interactive (on_select='ignore') -- it's never
    the human's turn while this is called. Each call needs its own `key`:
    Streamlit de-dupes same-type elements by their static call signature, not
    by the figure data inside them, so repeated redraws in one script run
    would otherwise collide."""
    fig = build_board_figure(state.to_dict())
    board_placeholder.plotly_chart(
        fig, width='stretch', config={"displayModeBar": False}, on_select="ignore",
        key=redraw_key,
    )


def run_ai_turn(state, feed_placeholder, battle_placeholder, board_placeholder):
    """Runs the AI's whole turn, but -- unlike a black box -- each attack and
    the reinforcement pass are surfaced exactly the way the human's own moves
    are: a centered dice-comparison popup per capture, the board redrawn
    right after, then on to the next step."""
    steps = AI.run_turn(state)
    st.session_state.chart_seq += 1
    redraw_i = 0
    for step in steps:
        if step["type"] == "thought":
            append_feed(step["thought"])
            feed_placeholder.markdown(
                '<div class="dw-feed-scroll">'
                + "".join(render_thought_html(t) for t in st.session_state.feed[:12])
                + "</div>",
                unsafe_allow_html=True,
            )
            if step["thought"]["agent"] == "defense":
                placements = step.get("placements_detail") or []
                if placements:
                    show_reinforcement_overlay(battle_placeholder, "AI General", placements)
                    redraw_i += 1
                    redraw_board(board_placeholder, state, f"board_ai_{st.session_state.chart_seq}_{redraw_i}")
        elif step["type"] == "attack_result":
            play_battle_animation(battle_placeholder, step["result"])
            redraw_i += 1
            redraw_board(board_placeholder, state, f"board_ai_{st.session_state.chart_seq}_{redraw_i}")
    state.switch_turn()  # back to human


def get_clicked_tid(event):
    """Pull the territory id out of a plotly_chart on_select event, if any."""
    if not event:
        return None
    try:
        points = event["selection"]["points"]
    except (TypeError, KeyError):
        points = []
    if not points:
        return None
    point = points[0]
    customdata = point.get("customdata") if isinstance(point, dict) else None
    if not customdata:
        return None
    return customdata[0]


def handle_board_click(state, sd, human_t, clicked_tid):
    """Click-to-attack: first click on your own territory selects it as the
    source (lighting up its attackable enemy neighbors); a second click on a
    highlighted neighbor fires the attack. Clicking the source again
    deselects it; clicking a different eligible territory of yours re-aims
    the selection instead."""
    st.session_state.click_message = None
    t_clicked = sd["territories"].get(str(clicked_tid))
    if t_clicked is None:
        return None

    src = st.session_state.selected_src

    def can_attack_from(tid):
        tt = sd["territories"][str(tid)]
        return tt["owner"] == "human" and tt["dice"] > 1 and any(
            sd["territories"][str(n)]["owner"] != "human" for n in tt["neighbors"]
        )

    if src is None:
        if t_clicked["owner"] != "human":
            st.session_state.click_message = "Select one of your own territories first."
        elif t_clicked["dice"] <= 1:
            st.session_state.click_message = "That territory only has 1 die \u2014 it can't attack."
        elif not can_attack_from(clicked_tid):
            st.session_state.click_message = "That territory has no enemy neighbors to attack."
        else:
            st.session_state.selected_src = clicked_tid
        return None

    if clicked_tid == src:
        st.session_state.selected_src = None
        return None

    src_t = sd["territories"][str(src)]
    valid_targets = {n for n in src_t["neighbors"] if sd["territories"][str(n)]["owner"] != "human"}

    if clicked_tid in valid_targets:
        result = state.attack(src, clicked_tid)
        st.session_state.selected_src = None
        return vars(result)
    elif can_attack_from(clicked_tid):
        st.session_state.selected_src = clicked_tid
    else:
        st.session_state.click_message = "That territory isn't reachable from your current selection."
    return None


def render_cheat_panel(state):
    thought = ORACLE.think(state, owner="human")
    shortlist = thought.data.get("shortlist", [])
    with st.expander("\U0001F575\uFE0F Cheat: Recommended Move", expanded=False):
        st.markdown(render_thought_html(vars(thought)), unsafe_allow_html=True)
        if shortlist:
            rows = "".join(
                f'<div class="dw-cheat-row">'
                f'<span><span class="dw-cheat-rank">#{i+1}</span>T{c["src"]} \u2192 T{c["dst"]}</span>'
                f'<span>{int(c["win_prob"]*100)}% win \u00b7 exposure {c["exposure"]}</span>'
                f'</div>'
                for i, c in enumerate(shortlist)
            )
            st.markdown(f'<div class="dw-card">{rows}</div>', unsafe_allow_html=True)


# =================================================================
# NO ACTIVE GAME -> MAP SELECT
# =================================================================
if st.session_state.game is None:
    brand_header()
    st.markdown("## Choose Your Theater")
    st.markdown(
        "*Three campaign maps. One AI general, built from three cooperating agents, standing against you. "
        "Every match generates a freshly randomized layout, coastline, and set of gaps.*"
    )
    st.write("")
    cols = st.columns(3)
    descriptions = {
        "skirmish_isle": "Small and fast — good for learning the flow.",
        "twin_peninsulas": "Mid-sized, with natural choke points.",
        "grand_continent": "A sprawling campaign for longer games.",
    }
    for col, (map_id, label) in zip(cols, MAPS.items()):
        with col:
            st.markdown(
                f"""
                <div class="dw-map-card">
                    <h3>{label.split('(')[0].strip()}</h3>
                    <p style="font-size:0.85rem; color:#5a4a30;">
                        {'(' + label.split('(')[1] if '(' in label else ''}
                    </p>
                    <p>{descriptions.get(map_id, '')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Play {label.split('(')[0].strip()}", key=f"play_{map_id}", width='stretch'):
                new_game(map_id)
                st.rerun()

# =================================================================
# ACTIVE GAME
# =================================================================
else:
    state = st.session_state.game
    sd = state.to_dict()

    header_col, home_col = st.columns([5, 1])
    with header_col:
        brand_header()
    with home_col:
        if st.button("\U0001F3E0 Home", key="home_btn", width='stretch'):
            go_home()
            st.rerun()

    if state.winner:
        winner_label = "Victory is Yours" if state.winner == "human" else "The AI General Prevails"
        color = "#b25050" if state.winner == "human" else "#5c8ca3"
        st.markdown(
            f"<h1 style='text-align:center; color:{color};'>{winner_label}</h1>",
            unsafe_allow_html=True,
        )
        if st.button("Play Again", width='stretch'):
            go_home()
            st.rerun()
        st.stop()

    human_t = [t for t in sd["territories"].values() if t["owner"] == "human"]
    ai_t = [t for t in sd["territories"].values() if t["owner"] == "ai"]
    is_human_attack_phase = sd["turn_owner"] == "human" and state.pending_reinforcements == 0
    attackable = [
        t["id"] for t in human_t
        if t["dice"] > 1 and any(sd["territories"][str(n)]["owner"] != "human" for n in t["neighbors"])
    ]

    board_col, side_col = st.columns([2.1, 1])

    with side_col:
        badge_class = "human" if sd["turn_owner"] == "human" else "ai"
        badge_text = "Your Turn" if sd["turn_owner"] == "human" else "AI Turn"
        st.markdown(
            f"""
            <div class="dw-card">
                <span class="dw-badge {badge_class}">{badge_text}</span>
                <table style="width:100%; font-size:0.85rem; margin-top:8px;">
                    <tr><td>Turn</td><td style="text-align:right;"><b>{sd['turn_number']}</b></td></tr>
                    <tr><td>Your territories</td><td style="text-align:right;"><b>{len(human_t)}</b></td></tr>
                    <tr><td>AI territories</td><td style="text-align:right;"><b>{len(ai_t)}</b></td></tr>
                    <tr><td>Your dice</td><td style="text-align:right;"><b>{sum(t['dice'] for t in human_t)}</b></td></tr>
                    <tr><td>AI dice</td><td style="text-align:right;"><b>{sum(t['dice'] for t in ai_t)}</b></td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        end_attack_disabled = not is_human_attack_phase
        if st.button(
            "End Attack Phase", key="end_attack_btn", width='stretch',
            disabled=end_attack_disabled,
            help="Available during your attack phase; grayed out during reinforcement "
                 "placement and the AI's turn.",
        ):
            state.end_turn_and_reinforce("human")
            st.session_state.selected_src = None
            st.session_state.chart_seq += 1
            st.rerun()

        with st.expander("Behind the Scenes — Live", expanded=True):
            feed_placeholder = st.empty()
            if st.session_state.feed:
                feed_placeholder.markdown(
                    '<div class="dw-feed-scroll">'
                    + "".join(render_thought_html(t) for t in st.session_state.feed[:12])
                    + "</div>",
                    unsafe_allow_html=True,
                )
            else:
                feed_placeholder.markdown(
                    '<div class="dw-thought strategy"><div class="tag">System</div>'
                    '<div class="headline">Awaiting first move\u2026</div></div>',
                    unsafe_allow_html=True,
                )

        if is_human_attack_phase:
            render_cheat_panel(state)

        with st.expander("\U0001F4DC Attack Log", expanded=False):
            if state.log:
                st.markdown(
                    "<div class='dw-card' style='font-family:JetBrains Mono, monospace; "
                    "font-size:0.78rem;'>" +
                    "<br>".join(reversed(state.log[-40:])) +
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No attacks yet this match.")

    with board_col:
        valid_targets = set()
        if is_human_attack_phase and st.session_state.selected_src is not None:
            src_t = sd["territories"].get(str(st.session_state.selected_src))
            if src_t:
                valid_targets = {n for n in src_t["neighbors"] if sd["territories"][str(n)]["owner"] != "human"}

        fig = build_board_figure(sd, selected_id=st.session_state.selected_src, valid_targets=valid_targets)

        board_placeholder = st.empty()
        chart_key = f"board_chart_{st.session_state.chart_seq}"
        event = board_placeholder.plotly_chart(
            fig, width='stretch', config={"displayModeBar": False},
            on_select="rerun" if is_human_attack_phase else "ignore",
            selection_mode="points",
            key=chart_key,
        )

        # Overlay placeholder: battle popups and "placing reinforcements" both
        # render here as a centered, fixed-position modal (see theme.py /
        # animation.py) -- same treatment regardless of whose move it is.
        battle_placeholder = st.empty()

        if sd["turn_owner"] == "human":
            if state.pending_reinforcements > 0:
                st.markdown(f"**Reinforcements remaining: {state.pending_reinforcements}**")
                own_ids = [t["id"] for t in human_t if t["dice"] < 8]
                if own_ids:
                    target = st.selectbox(
                        "Place a reinforcement on:", own_ids,
                        format_func=lambda i: f"Territory {i} ({sd['territories'][str(i)]['dice']} dice)",
                        key="reinforce_target",
                    )
                    rc1, rc2 = st.columns(2)
                    if rc1.button("Place Die", width='stretch'):
                        state.place_reinforcement("human", target)
                        st.rerun()
                    if rc2.button("Auto-place rest", width='stretch'):
                        before = {t["id"]: t["dice"] for t in human_t}
                        placed = state.auto_place_reinforcements("human")
                        if placed:
                            running = dict(before)
                            detail = []
                            for tid in placed:
                                running[tid] = running.get(tid, 0) + 1
                                detail.append((tid, running[tid]))
                            show_reinforcement_overlay(battle_placeholder, "You", detail)
                        state.switch_turn()
                        run_ai_turn(state, feed_placeholder, battle_placeholder, board_placeholder)
                        st.session_state.selected_src = None
                        st.rerun()
                else:
                    state.auto_place_reinforcements("human")
                    st.rerun()

                if state.pending_reinforcements == 0:
                    state.switch_turn()
                    run_ai_turn(state, feed_placeholder, battle_placeholder, board_placeholder)
                    st.session_state.selected_src = None
                    st.rerun()
            else:
                if attackable:
                    clicked_tid = get_clicked_tid(event)
                    if clicked_tid is not None:
                        battle_result = handle_board_click(state, sd, human_t, clicked_tid)
                        if battle_result is not None:
                            play_battle_animation(battle_placeholder, battle_result)
                        st.session_state.chart_seq += 1  # reset chart selection state
                        st.rerun()

                    if st.session_state.selected_src is not None:
                        st.markdown(
                            f'<div class="dw-hint">Territory <b>T{st.session_state.selected_src}</b> '
                            f'selected \u2014 click a highlighted enemy territory to attack, '
                            f'or click it again to deselect.</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="dw-hint">Click one of your territories (2+ dice) to see '
                            'which enemy territories it can attack.</div>',
                            unsafe_allow_html=True,
                        )
                    if st.session_state.click_message:
                        st.markdown(
                            f'<div class="dw-click-msg">{st.session_state.click_message}</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No legal attacks available \u2014 use End Attack Phase in the side panel.")
        else:
            # Shouldn't normally be reached (AI turn runs synchronously above),
            # but acts as a safety net if state was left mid-AI-turn.
            run_ai_turn(state, feed_placeholder, battle_placeholder, board_placeholder)
            st.rerun()
