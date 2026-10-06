"""
Streamlit has no persistent client-side animation loop the way the Canvas/JS
version did, but a placeholder updated in a tight loop with short sleeps,
inside a single script run, still produces a real tumble-then-reveal effect.
This trades smoothness for zero extra JS/components -- which is the point
of the Streamlit rebuild: fewer moving parts, easier deploy.

Everything here renders into a `.dw-overlay-backdrop` / `.dw-overlay-modal`
pair (CSS in theme.py) so it shows as a centered popup over the whole
viewport -- the player never has to scroll to see what's happening, whether
it's their own attack, the AI's attack, or either side placing
reinforcements.
"""
import random
import time
import streamlit as st

AGENT_LABEL = {
    "strategy": "Strategy Agent", "attack": "Attack Agent", "defense": "Defense Agent",
    "oracle": "Oracle (Cheat)",
}


def _dice_html(rolls, side):
    return "".join(
        f'<span class="die-face {side}">{v}</span>' for v in rolls
    )


def _overlay(inner_html):
    return f'<div class="dw-overlay-backdrop"><div class="dw-overlay-modal">{inner_html}</div></div>'


def clear_overlay(placeholder):
    placeholder.empty()


def play_battle_animation(placeholder, result, frames=5, frame_delay=0.09, hold=0.9):
    """result: dict shaped like AttackResult (attacker_rolls, defender_rolls,
    attacker_total, defender_total, success, attacker_id, defender_id).
    Renders as a centered popup -- identical treatment whether the attack was
    the human's or the AI's, so the AI's turn is never a black box."""
    a_n = len(result["attacker_rolls"])
    d_n = len(result["defender_rolls"])

    for _ in range(frames):
        a_fake = [random.randint(1, 6) for _ in range(a_n)]
        d_fake = [random.randint(1, 6) for _ in range(d_n)]
        placeholder.markdown(
            _overlay(f"""
                <h4>Territory {result['attacker_id']} &rarr; Territory {result['defender_id']}</h4>
                <div><b>Attacker</b><br>{_dice_html(a_fake, 'attacker')}</div>
                <div style="margin-top:8px;"><b>Defender</b><br>{_dice_html(d_fake, 'defender')}</div>
            """),
            unsafe_allow_html=True,
        )
        time.sleep(frame_delay)

    outcome_class = "win" if result["success"] else "lose"
    outcome_text = (
        f"Attacker wins {result['attacker_total']} &ndash; {result['defender_total']} &middot; Territory captured"
        if result["success"] else
        f"Defender holds {result['defender_total']} &ndash; {result['attacker_total']} &middot; Attack repelled"
    )
    placeholder.markdown(
        _overlay(f"""
            <h4>Territory {result['attacker_id']} &rarr; Territory {result['defender_id']}</h4>
            <div><b>Attacker</b><br>{_dice_html(result['attacker_rolls'], 'attacker')}</div>
            <div style="margin-top:8px;"><b>Defender</b><br>{_dice_html(result['defender_rolls'], 'defender')}</div>
            <div class="dw-result {outcome_class}">{outcome_text}</div>
        """),
        unsafe_allow_html=True,
    )
    time.sleep(hold)
    clear_overlay(placeholder)


def show_reinforcement_overlay(placeholder, owner_label, placements=None, hold=0.55):
    """A short-lived centered popup shown while reinforcement dice are being
    placed, so that step is visible rather than happening silently between
    reruns. `placements` -- optional list of (territory_id, new_dice_count)
    -- is revealed one line at a time for a sense of real-time progress."""
    placeholder.markdown(
        _overlay(f"""
            <div class="dw-overlay-msg">&#127922; Placing reinforcements&hellip;</div>
            <div class="dw-overlay-sub">{owner_label} is reinforcing its border</div>
        """),
        unsafe_allow_html=True,
    )
    time.sleep(0.35)

    if placements:
        shown = []
        for tid, new_count in placements:
            shown.append(f"T{tid} &rarr; {new_count} dice")
            rows = "".join(f'<div style="padding:2px 0;">{s}</div>' for s in shown[-6:])
            placeholder.markdown(
                _overlay(f"""
                    <div class="dw-overlay-msg">&#127922; Placing reinforcements&hellip;</div>
                    <div style="font-family:'JetBrains Mono', monospace; font-size:0.85rem;
                                text-align:center; margin-top:8px;">{rows}</div>
                """),
                unsafe_allow_html=True,
            )
            time.sleep(0.16)
    time.sleep(hold)
    clear_overlay(placeholder)


def render_thought_html(thought):
    agent = thought["agent"]
    label = AGENT_LABEL.get(agent, agent)
    return f"""
    <div class="dw-thought {agent}">
        <div class="tag">{label}</div>
        <div class="headline">{thought['headline']}</div>
        <div class="detail">{thought['detail']}</div>
    </div>
    """


def append_feed(thought):
    if "feed" not in st.session_state:
        st.session_state.feed = []
    st.session_state.feed.insert(0, thought)
    st.session_state.feed = st.session_state.feed[:40]
