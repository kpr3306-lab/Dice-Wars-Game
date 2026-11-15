import streamlit as st
from theme import inject_css, brand_header

st.set_page_config(page_title="How to play · Dice Wars", page_icon="⚄", layout="wide")
inject_css()
brand_header()

st.markdown(
    """
    <div class="dw-page-head">
        <span class="eyebrow">How to play</span>
        <h1>Conquer the map</h1>
        <p>Dice Wars is a territory-control game. You hold the red territories, the AI general holds the
        blue. Attack with dice, rebuild your line, and take every territory on the board.</p>
    </div>

    <div class="dw-steps" style="margin-top:16px;">
        <div class="dw-step"><div class="n">01</div><div class="t">Pick an attacker</div>
            <div class="d">Click one of your territories with 2+ dice. Its attackable neighbors light up in brass.</div></div>
        <div class="dw-step"><div class="n">02</div><div class="t">Strike</div>
            <div class="d">Click a highlighted enemy territory. Both sides roll all their dice and the higher total wins.</div></div>
        <div class="dw-step"><div class="n">03</div><div class="t">End the attack phase</div>
            <div class="d">When you're done, press <b>End attack phase</b> in the command panel.</div></div>
        <div class="dw-step"><div class="n">04</div><div class="t">Reinforce</div>
            <div class="d">Click your territories to add dice, or auto-place the rest. Then the AI moves.</div></div>
    </div>

    <div class="dw-grid">
        <div class="dw-card">
            <h3>Combat</h3>
            <p><b>Win</b> and the defender's territory becomes yours: all but one of your attacking dice move in.
            <b>Lose</b> and your attacker drops to a single die while the defender is untouched.</p>
            <p>Only a territory with 2+ dice can attack, so a failed attack takes it out of action until you reinforce.
            Every battle, yours or the AI's, appears as a popup in the middle of the screen.</p>
        </div>
        <div class="dw-card">
            <h3>Reinforcements</h3>
            <p>You get one die for every territory in your <b>largest connected group</b>, so keeping your
            holdings linked matters as much as their number.</p>
            <p>Click your territories on the map or use the picker in the command panel. Each territory holds at
            most 8 dice, and any dice that don't fit are lost.</p>
        </div>
        <div class="dw-card">
            <h3>The opponent</h3>
            <p>The AI general is a pipeline of three cooperating agents: one sets the turn's strategy, one
            attacks, and one reinforces. The <b>Live feed</b> tab shows their reasoning as they play.</p>
            <p>Stuck? The <b>Oracle (cheat)</b> tab shows the best-odds move for you during your attack phase.</p>
        </div>
        <div class="dw-card">
            <h3>Maps</h3>
            <p><b>Skirmish Isle</b> is small and quick. <b>Twin Peninsulas</b> has natural choke points.
            <b>Grand Continent</b> is a sprawling 40-territory campaign.</p>
            <p>Each match picks a fresh layout, with lake-like gaps that break up the borders and create choke
            points. <b>Leave match</b> in the top bar takes you back to map select at any time.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
