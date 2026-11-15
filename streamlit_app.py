import random
import streamlit as st

from game.engine import GameState, MAPS, MAX_DICE, list_map_variants, load_map_file
from agents.ai_controller import AIController
from agents.oracle_agent import OracleAgent
from theme import inject_css, brand_header
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


def render_feed(placeholder):
    if st.session_state.feed:
        placeholder.markdown("".join(render_thought_html(t) for t in st.session_state.feed[:20]),
                             unsafe_allow_html=True)
    else:
        placeholder.markdown('<div class="dw-empty">No moves yet. The AI&rsquo;s three agents report '
                             'their reasoning here as they play.</div>', unsafe_allow_html=True)


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
            render_feed(feed_placeholder)
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
    st.markdown(render_thought_html(vars(thought)), unsafe_allow_html=True)
    if shortlist:
        rows = "".join(
            f'<div class="dw-cheat-row">'
            f'<span><span class="dw-cheat-rank">#{i+1}</span>T{c["src"]} → T{c["dst"]}</span>'
            f'<span class="mono">{int(c["win_prob"]*100)}% win · exposure {c["exposure"]}</span>'
            f'</div>'
            for i, c in enumerate(shortlist)
        )
        st.markdown(rows, unsafe_allow_html=True)


def front(caption, h, a, unit):
    return f"""
        <div class="dw-front">
            <div class="head"><span class="h">You <b>{h}</b></span><span>{caption}</span><span class="a"><b>{a}</b> AI</span></div>
            <div class="bar" role="img" aria-label="You {h} {unit}, AI {a} {unit}">
                <span class="h" style="flex-grow:{h};"></span><span class="a" style="flex-grow:{a};"></span>
            </div>
        </div>"""


def finish_human_reinforcement(state, feed_placeholder, battle_placeholder, board_placeholder):
    # Dice that don't fit under the 8-per-territory cap are forfeited, so the
    # turn can never get stuck with an unplaceable pool.
    state.pending_reinforcements = 0
    state.switch_turn()
    run_ai_turn(state, feed_placeholder, battle_placeholder, board_placeholder)
    st.session_state.selected_src = None
    st.session_state.click_message = None
    st.session_state.chart_seq += 1
    st.rerun()


@st.cache_data
def territory_count(map_id):
    return len(load_map_file(list_map_variants(map_id)[0])["territories"])


# =================================================================
# NO ACTIVE GAME -> MAP SELECT
# =================================================================
if st.session_state.game is None:
    brand_header()
    st.markdown(
        """
        <div class="dw-hero">
            <span class="dw-chip">TURN-BASED STRATEGY</span><span class="dw-chip">MULTI-AGENT AI</span>
            <h1>Choose your theater</h1>
            <p>You command the red. Across the water, an AI general built from three cooperating
            agents commands the blue. Every match deals a fresh coastline and territory layout.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    blurbs = {
        "skirmish_isle": ("Small and fast. The best place to learn the flow.", "Quick"),
        "twin_peninsulas": ("Mid-sized, with natural choke points to hold.", "Standard"),
        "grand_continent": ("A sprawling campaign for longer games.", "Long"),
    }
    _, *cols, _ = st.columns([0.15, 1, 1, 1, 0.15], gap="medium")
    for i, (col, (map_id, label)) in enumerate(zip(cols, MAPS.items())):
        name = label.split("(")[0].strip()
        blurb, pace = blurbs.get(map_id, ("", ""))
        scale = "".join(f'<i class="{"on" if b <= i else ""}" style="height:{10 + b * 8}px"></i>' for b in range(3))
        with col, st.container(key=f"dw_map_{map_id}"):
            st.markdown(
                f"""
                <div class="dw-map">
                    <div class="scale" aria-hidden="true">{scale}</div>
                    <h3>{name}</h3>
                    <p>{blurb}</p>
                    <div class="stats">
                        <div class="stat"><div class="v">{territory_count(map_id)}</div><div class="k">Territories</div></div>
                        <div class="stat"><div class="v">{pace}</div><div class="k">Pace</div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Play {name}", key=f"play_{map_id}", type="primary", width="stretch"):
                new_game(map_id)
                st.rerun()

# =================================================================
# ACTIVE GAME
# =================================================================
else:
    state = st.session_state.game
    sd = state.to_dict()

    with brand_header(), st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("Leave match", key="home_btn", help="Abandon this match and return to map select."):
            go_home()
            st.rerun()

    if state.winner:
        won = state.winner == "human"
        st.markdown(
            f"""
            <div class="dw-card dw-endcard" style="--dw-end:{'#c35a55' if won else '#5b93ad'};">
                <span class="eyebrow">Campaign over</span>
                <h1>{'The map is yours' if won else 'The AI general holds the map'}</h1>
                <p>Decided on turn {sd['turn_number']}, after {len(state.log)} battles.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _, mid, _ = st.columns([1, 0.6, 1])
        if mid.button("Play again", type="primary", width="stretch"):
            go_home()
            st.rerun()
        st.stop()

    human_t = [t for t in sd["territories"].values() if t["owner"] == "human"]
    ai_t = [t for t in sd["territories"].values() if t["owner"] == "ai"]
    is_human_turn = sd["turn_owner"] == "human"
    reinforcing = is_human_turn and state.pending_reinforcements > 0
    is_human_attack_phase = is_human_turn and not reinforcing
    attackable = [
        t["id"] for t in human_t
        if t["dice"] > 1 and any(sd["territories"][str(n)]["owner"] != "human" for n in t["neighbors"])
    ]
    own_ids = [t["id"] for t in human_t if t["dice"] < MAX_DICE]

    valid_targets = set()
    if is_human_attack_phase and st.session_state.selected_src is not None:
        src_t = sd["territories"].get(str(st.session_state.selected_src))
        if src_t:
            valid_targets = {n for n in src_t["neighbors"] if sd["territories"][str(n)]["owner"] != "human"}

    board_col, side_col = st.columns([2.25, 1], gap="medium")

    # ---------------------------------------------------------------- board
    with board_col:
        with st.container(key="dw_board"):
            board_placeholder = st.empty()
            event = board_placeholder.plotly_chart(
                build_board_figure(sd, selected_id=st.session_state.selected_src, valid_targets=valid_targets),
                width="stretch", config={"displayModeBar": False},
                on_select="rerun" if (is_human_attack_phase and attackable) or reinforcing else "ignore",
                selection_mode="points",
                key=f"board_chart_{st.session_state.chart_seq}",
            )
            st.markdown(
                '<div class="dw-legend">'
                '<span><i style="background:#9e3f3c"></i>Your territory</span>'
                '<span><i style="background:#3b6f88"></i>AI territory</span>'
                '<span><i style="background:#fff6e0"></i>Selected attacker</span>'
                '<span><i style="background:#e3bf6a"></i>Attackable target</span>'
                '</div>',
                unsafe_allow_html=True,
            )
        # Battle / reinforcement popups render here as a fixed, centered modal.
        battle_placeholder = st.empty()

    # ---------------------------------------------------------------- side panel
    end_clicked = place_clicked = auto_clicked = False
    with side_col:
        with st.container(key="dw_command"):
            badge = '<span class="dw-badge human">Your turn</span>' if is_human_turn \
                else '<span class="dw-badge ai">AI general is moving</span>'
            human_dice, ai_dice = sum(t["dice"] for t in human_t), sum(t["dice"] for t in ai_t)
            if is_human_attack_phase:
                phase = "Attack phase"
                if not attackable:
                    hint = "None of your territories can attack. End the phase to collect reinforcements."
                elif st.session_state.selected_src is not None:
                    hint = (f"<b>T{st.session_state.selected_src}</b> selected. Click a highlighted enemy "
                            f"territory to attack, or click it again to deselect.")
                else:
                    hint = "Click one of your territories with <b>2+ dice</b> to see what it can attack."
            elif reinforcing:
                phase = f"Reinforce · {state.pending_reinforcements} dice left"
                hint = ("Click your territories on the map to add a die each, or let the game place "
                        "the rest on your weakest border.")
            else:
                phase, hint = "Enemy turn", "Watch the live feed for the AI's reasoning."
            msg = st.session_state.click_message
            st.markdown(
                f"""
                <div class="dw-turn-row">{badge}<span class="num">TURN {sd['turn_number']}</span></div>
                {front("Territories", len(human_t), len(ai_t), "territories")}
                {front("Dice", human_dice, ai_dice, "dice")}
                <div class="dw-divider"></div>
                <div class="dw-phase">{phase}</div>
                <div class="dw-hint">{hint}</div>
                {f'<div class="dw-click-msg" role="status">{msg}</div>' if msg else ''}
                """,
                unsafe_allow_html=True,
            )
            if is_human_attack_phase:
                end_clicked = st.button("End attack phase", key="end_attack_btn", type="primary", width="stretch")
            elif reinforcing and own_ids:
                pick_col, place_col = st.columns([2.2, 1], vertical_alignment="bottom", gap="small")
                target = pick_col.selectbox(
                    "Place a reinforcement on", own_ids, label_visibility="collapsed",
                    format_func=lambda i: f"T{i} · {sd['territories'][str(i)]['dice']} dice",
                    key="reinforce_target",
                )
                place_clicked = place_col.button("Place", key="place_btn", width="stretch")
                auto_clicked = st.button("Auto-place the rest", key="auto_btn", type="primary", width="stretch")

        feed_tab, oracle_tab, log_tab = st.tabs(["Live feed", "Oracle (cheat)", "Battle log"])
        with feed_tab, st.container(height=250, border=False):
            feed_placeholder = st.empty()
            render_feed(feed_placeholder)
        with oracle_tab, st.container(height=250, border=False):
            if is_human_attack_phase and attackable:
                render_cheat_panel(state)
            else:
                st.markdown('<div class="dw-empty">The Oracle suggests your best-odds attack during your '
                            'attack phase.</div>', unsafe_allow_html=True)
        with log_tab, st.container(height=250, border=False):
            if state.log:
                st.markdown('<div class="dw-log">' + "<br>".join(reversed(state.log[-40:])) + "</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown('<div class="dw-empty">No battles yet this match.</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------------- turn flow
    if is_human_attack_phase:
        if end_clicked:
            state.end_turn_and_reinforce("human")
            st.session_state.selected_src = None
            st.session_state.click_message = None
            st.session_state.chart_seq += 1
            st.rerun()
        clicked_tid = get_clicked_tid(event) if attackable else None
        if clicked_tid is not None:
            battle_result = handle_board_click(state, sd, human_t, clicked_tid)
            if battle_result is not None:
                play_battle_animation(battle_placeholder, battle_result)
            st.session_state.chart_seq += 1  # reset chart selection state
            st.rerun()

    elif reinforcing:
        if not own_ids or auto_clicked:
            before = {t["id"]: t["dice"] for t in human_t}
            detail = []
            for tid in state.auto_place_reinforcements("human"):
                before[tid] += 1
                detail.append((tid, before[tid]))
            if detail:
                show_reinforcement_overlay(battle_placeholder, "You", detail)
            finish_human_reinforcement(state, feed_placeholder, battle_placeholder, board_placeholder)

        clicked_tid = get_clicked_tid(event)
        placed = False
        if clicked_tid is not None:
            st.session_state.click_message = None
            placed = state.place_reinforcement("human", clicked_tid)
            if not placed:
                t = sd["territories"].get(str(clicked_tid))
                st.session_state.click_message = (
                    "Reinforce your own territories only." if t and t["owner"] != "human"
                    else f"That territory is already at the {MAX_DICE}-dice cap."
                )
            st.session_state.chart_seq += 1
        elif place_clicked:
            st.session_state.click_message = None
            placed = state.place_reinforcement("human", target)

        if placed and state.pending_reinforcements == 0:
            finish_human_reinforcement(state, feed_placeholder, battle_placeholder, board_placeholder)
        if clicked_tid is not None or placed:
            st.rerun()

    else:
        # Safety net: the AI turn normally runs synchronously above, but if
        # state was left mid-AI-turn, finish it now.
        run_ai_turn(state, feed_placeholder, battle_placeholder, board_placeholder)
        st.rerun()
