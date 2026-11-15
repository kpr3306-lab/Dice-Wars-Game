import streamlit as st
from theme import inject_css, brand_header

st.set_page_config(page_title="Behind the scenes · Dice Wars", page_icon="⚄", layout="wide")
inject_css()
brand_header()

st.markdown(
    """
    <div class="dw-page-head">
        <span class="eyebrow">Behind the scenes</span>
        <h1>Three agents, one general</h1>
        <p>From your side of the table there is one opponent. Underneath, every AI turn runs a fixed
        hierarchical pipeline, and each agent hands its output to the next.</p>
    </div>

    <div class="dw-pipeline" style="margin-top:16px;">
        <div class="node" style="--c:#c9a24a"><div class="t">Strategy Agent</div><div class="d">Reads the board, sets the turn's posture</div></div>
        <div class="arrow" aria-hidden="true">&rarr;</div>
        <div class="node" style="--c:#c35a55"><div class="t">Attack Agent</div><div class="d">Scores and executes attacks under that posture</div></div>
        <div class="arrow" aria-hidden="true">&rarr;</div>
        <div class="node" style="--c:#5b93ad"><div class="t">Defense Agent</div><div class="d">Places reinforcements on the most exposed border</div></div>
        <div class="node side" style="--c:#9a72c4"><div class="t">Oracle Agent</div><div class="d">Outside the pipeline. Advises you, not the AI</div></div>
    </div>

    <div class="dw-grid">
        <div class="dw-card">
            <h3>Strategy Agent</h3>
            <p>Runs once at the start of every AI turn. It compares total dice, checks how exposed the AI's
            border is (territories at 1&ndash;2 dice next to yours) and how fragmented its territory is.</p>
            <p>It then picks one posture: <b>EXPAND</b> with a clear dice advantage, <b>DEFEND</b> when the
            border is thin, <b>CONSOLIDATE</b> when fragmented, or <b>TARGET_WEAK</b> as the default.</p>
        </div>
        <div class="dw-card">
            <h3>Attack Agent</h3>
            <p>Enumerates every legal attack and runs a 400-trial Monte-Carlo simulation of both dice pools
            to estimate a real win probability, rather than using a fixed odds table.</p>
            <p>Moves are filtered by a posture-dependent threshold: DEFEND only takes near-certain fights
            (&ge;85%), while EXPAND accepts reasonable trades (&ge;55%).</p>
        </div>
        <div class="dw-card">
            <h3>Defense Agent</h3>
            <p>Once attacking stops, the pool is fixed at one die per territory in the AI's largest connected
            group. It places dice one at a time on the territory with the highest <i>vulnerability score</i>:
            enemy dice threatening it minus its own.</p>
        </div>
        <div class="dw-card">
            <h3>Oracle Agent</h3>
            <p>A fourth agent that plays advisor. It is not the Attack Agent with the owner flipped:
            alongside win probability it rewards moves that open new frontier and penalises moves that leave
            your attacker or your new territory exposed to a counter-attack.</p>
        </div>
    </div>

    <div class="dw-card" style="margin-top:12px; height:auto;">
        <h3>Why a pipeline instead of independent bots</h3>
        <p>Independent agents can contradict each other, for example an attacker overextending right before
        a defender has no reinforcements left to cover it. Feeding the strategy downward means every
        decision in a turn works from the same read of the board: agents that hand off state and reasoning,
        not separate scripts moving the same pieces.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
