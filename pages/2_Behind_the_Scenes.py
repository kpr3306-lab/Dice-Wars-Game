import streamlit as st
from theme import inject_css, brand_header

st.set_page_config(page_title="Behind the Scenes — Dice Wars", page_icon="\u2684", layout="wide")
inject_css()
brand_header()
st.markdown("## Behind the Scenes")

st.markdown(
    """
    <div class="dw-card">
        <h3>Architecture</h3>
        <p><b>The AI general is three agents wearing one coat.</b> From your side of the table there is
        one opponent. Underneath, each of its turns runs a fixed hierarchical pipeline: a
        <b>Strategy Agent</b> sets the turn's posture, an <b>Attack Agent</b> executes moves under that
        posture, and a <b>Defense Agent</b> places reinforcements once attacking stops. Each agent hands
        its output to the next &mdash; this is deliberately a pipeline, not three bots acting
        independently.</p>
        <p style="font-family:'JetBrains Mono',monospace; font-size:0.82rem; background:#f3efe2;
                   border-radius:4px; padding:10px 14px;">
            Strategy Agent (sets goal) &rarr; Attack Agent (executes) &rarr; Defense Agent (reinforces)
        </p>
        <p>A fourth agent, the <b>Oracle</b>, sits outside this pipeline entirely &mdash; it advises the
        human player rather than the AI, and is described further down this page.</p>
    </div>

    <div class="dw-card">
        <h3>Strategy Agent</h3>
        <p><b>Reading the board.</b> Runs once at the start of every AI turn. It compares total dice on
        each side, checks how exposed the AI's border is (territories at 1&ndash;2 dice next to the
        human), and checks how fragmented the AI's territory is. From that it picks one posture:
        <b>EXPAND</b> when it holds a clear dice advantage, <b>DEFEND</b> when its border is dangerously
        thin, <b>CONSOLIDATE</b> when its territory is too fragmented to benefit from more expansion, and
        <b>TARGET_WEAK</b> as the default even-fight posture, hunting the single best-odds attack.</p>
    </div>

    <div class="dw-card">
        <h3>Attack Agent</h3>
        <p><b>Scoring every legal move.</b> Enumerates every territory the AI can legally attack from,
        and for each one runs a Monte-Carlo simulation (400 trials of rolling both dice pools) to
        estimate a real win probability rather than relying on a fixed odds table. Moves are filtered
        against a minimum win-probability threshold that depends on the current posture &mdash; DEFEND
        only takes near-certain fights (&ge;85%), while EXPAND will take reasonable trades (&ge;55%) to
        keep momentum.</p>
    </div>

    <div class="dw-card">
        <h3>Defense Agent</h3>
        <p><b>Reinforcing the line.</b> Once the Attack Agent stops, the reinforcement pool is fixed
        &mdash; one die per territory in the AI's largest connected group. The Defense Agent distributes
        that pool one die at a time, always to the territory with the highest <i>vulnerability score</i>
        (total enemy dice threatening it, minus its own current dice), which keeps reinforcement
        concentrated on the border under the most pressure.</p>
    </div>

    <div class="dw-card">
        <h3>Oracle Agent — the fourth agent</h3>
        <p><b>Playing advisor, not opponent.</b> Strategy, Attack, and Defense all act <i>for</i> the AI
        general. The Oracle is a separate, fourth agent that acts for nobody &mdash; it looks at the
        board from your side of the table and surfaces a ranked shortlist of recommended moves in a
        collapsed "Cheat: Recommended Move" panel during your attack phase.</p>
        <p>It isn't just the Attack Agent re-run with the owner flipped. Alongside win probability, it
        scores each candidate move on how much new frontier the captured territory would open up, and
        penalizes moves that would leave your attacking territory (down to 1 die) or your newly-taken
        territory exposed to an immediate enemy counter-attack next turn. The panel stays collapsed by
        default precisely because it's a cheat &mdash; open it if you want the hint, ignore it if you'd
        rather read the board yourself.</p>
    </div>

    <div class="dw-card">
        <h3>Why a pipeline instead of independent bots</h3>
        <p>Three independent agents making unrelated decisions can easily contradict each other &mdash;
        for example, an attack agent overextending right before a defense agent has no reinforcement
        bonus left to cover it. Feeding the strategy goal downward means every agent's decision that
        turn is working toward the same read of the board, which is what "multi-agent system" should
        mean here: agents that hand off state and reasoning to each other, not just three separate
        scripts that happen to move the same pieces.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
