import streamlit as st
from theme import inject_css, brand_header

st.set_page_config(page_title="Instructions — Dice Wars", page_icon="\u2684", layout="wide")
inject_css()
brand_header()
st.markdown("## Instructions")

st.markdown(
    """
    <div class="dw-card">
        <h3>The Objective</h3>
        <p><b>Conquer the map.</b> Dice Wars is a territory-control game. The map is split between you
        (wax-seal red) and the AI general (steel blue). On your turn, attack adjacent enemy territories
        using dice. Win enough battles and control the whole map — or simply hold more territory than
        the AI when the campaign settles.</p>
    </div>

    <div class="dw-card">
        <h3>Combat</h3>
        <p><b>How an attack works.</b> Every territory shows its dice as a little stack of dice-face
        icons, not just a number. <b>Click one of your own territories with 2+ dice</b> to select it as
        the attacker &mdash; its attackable enemy neighbors light up in brass. <b>Click a highlighted
        territory</b> to launch the attack from there; click your selected territory again to change
        your mind. All of your attacker's dice are rolled against all of the defender's dice &mdash;
        highest total wins.</p>
        <p><b>If you win:</b> the defender's territory becomes yours. All but one of your attacking dice
        move in to occupy it. <b>If you lose:</b> your attacking territory is left with just 1 die, and the
        defender is untouched. Either way, only a territory with 2+ dice can attack, so a losing attack
        takes you out of action there until you reinforce.</p>
        <p><b>Every battle pops up front and center.</b> Whether it's your attack or the AI's, the dice
        comparison appears as a popup in the middle of the screen so you never have to scroll to see what
        happened &mdash; the map updates right behind it the moment the popup clears. The AI's turn plays
        out the same way, capture by capture, rather than resolving silently offscreen.</p>
        <p><b>Cheating, if you want it.</b> The "Cheat: Recommended Move" panel in the sidebar is
        collapsed by default &mdash; open it any time during your attack phase to see the single
        best-odds move a fourth agent, the Oracle, would make in your position, plus its runner-up
        picks.</p>
    </div>

    <div class="dw-card">
        <h3>Reinforcements</h3>
        <p><b>Rebuilding your line.</b> When you're done attacking for the turn, click <b>End Attack
        Phase</b> in the side panel, next to the turn status card &mdash; it's highlighted while it's your
        attack phase and grayed out the rest of the time, so it's always obvious whether it's available.
        You receive one reinforcement die for every territory in your <i>largest connected group</i>
        &mdash; so keeping your holdings linked up matters as much as their number. Place dice one at a
        time on your own territories (max 8 per territory), or use <b>Auto-place rest</b> to let the game
        distribute what's left to your most exposed borders; either way, a "Placing reinforcements&hellip;"
        popup shows the dice landing in real time. The AI goes through the identical popup when it
        reinforces.</p>
    </div>

    <div class="dw-card">
        <h3>Leaving a Match</h3>
        <p>The <b>&#127968; Home</b> button at the top of the screen returns you to the map-select
        screen at any time, abandoning the current match. Use it if you want to switch maps or start
        over &mdash; there's no need to play a match out to see the Instructions or Behind the Scenes
        pages, either; both are always reachable from the sidebar navigation.</p>
    </div>

    <div class="dw-card">
        <h3>The Opponent</h3>
        <p><b>You're not playing a script.</b> The AI general is a small pipeline of three cooperating
        agents &mdash; one sets the turn's overall strategy, one executes attacks, one places
        reinforcements. Watch the <b>Behind the Scenes &mdash; Live</b> panel during play to see its
        reasoning in real time, or visit the Behind the Scenes page for the full architecture.</p>
    </div>

    <div class="dw-card">
        <h3>Maps</h3>
        <p><b>Three theaters.</b> Skirmish Isle is small and fast &mdash; good for learning the flow.
        Twin Peninsulas is a mid-sized map with natural choke points. Grand Continent is a sprawling
        40-territory campaign for longer games. All three are generated as organic landmasses, not a
        grid of nodes, so borders and choke points actually matter.</p>
        <p><b>No two matches look alike.</b> Each time you start a match, the coastline, territory
        layout, and a scattering of random gaps (lake-like holes left out of the map on purpose) are
        all regenerated &mdash; only the territory <i>count</i> for a given size stays fixed. The gaps
        break up straight borders and create natural choke points, the same way the original Dice Wars
        board never tiled perfectly edge to edge.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
