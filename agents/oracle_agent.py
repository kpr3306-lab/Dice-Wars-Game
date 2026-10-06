"""
Oracle Agent
------------
The fourth agent in the system — separate from the AI opponent's pipeline.
Strategy, Attack, and Defense all play *for* the AI. The Oracle plays for
nobody: it looks at the board from the human's side and produces a ranked
shortlist of recommended moves, surfaced in the UI as a hidden "cheat"
panel.

It deliberately isn't just the Attack Agent re-run with the owner flipped.
Its scoring also accounts for counter-attack exposure: a move that wins big
but leaves the newly-taken (or newly-emptied) territory naked to an
immediate enemy response next turn is worth less than one that consolidates
the border, even at a slightly lower raw win probability.
"""
from .base_agent import BaseAgent, AgentThought


class OracleAgent(BaseAgent):
    name = "oracle"

    def _post_attack_exposure(self, state, src, dst, enemy):
        """Rough estimate of how exposed src (down to 1 die) and dst (holding
        the moved-in dice) would be to an immediate enemy counter-attack."""
        moved_dice = max(state.territories[src].dice - 1, 1)
        src_threat = sum(
            state.territories[n].dice for n in state.territories[src].neighbors
            if state.territories[n].owner == enemy
        )
        dst_threat = sum(
            state.territories[n].dice for n in state.territories[dst].neighbors
            if state.territories[n].owner == enemy and n != src
        )
        return max(src_threat - 1, 0) + max(dst_threat - moved_dice, 0)

    def shortlist(self, state, owner="human", top_n=3):
        """Ranked list of every legal attack for `owner`, best first."""
        enemy = "ai" if owner == "human" else "human"
        candidates = []
        for src, dst in state.valid_attacks(owner):
            a_dice = state.territories[src].dice
            d_dice = state.territories[dst].dice
            wp = state.win_probability(a_dice, d_dice)
            exposure = self._post_attack_exposure(state, src, dst, enemy)
            frontier_value = 1 + sum(
                1 for n in state.territories[dst].neighbors
                if state.territories[n].owner == enemy
            )
            score = wp * (1 + 0.15 * frontier_value) - 0.05 * exposure
            candidates.append({
                "src": src, "dst": dst,
                "win_prob": round(wp, 2),
                "exposure": exposure,
                "score": round(score, 3),
            })
        candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates[:top_n]

    def think(self, state, owner="human", **kwargs) -> AgentThought:
        shortlist = self.shortlist(state, owner=owner)
        if not shortlist:
            return AgentThought(
                agent=self.name,
                headline="No attack worth recommending right now",
                detail="Every legal move from your territories currently loses value once "
                       "counter-attack exposure is factored in. Reinforcing may be the "
                       "stronger play this turn.",
                data={"shortlist": []},
            )
        best = shortlist[0]
        headline = f"Best move: T{best['src']} \u2192 T{best['dst']} ({int(best['win_prob']*100)}% win chance)"
        detail = (
            f"Ranked {len(shortlist)} candidate attack(s) by win probability, how much "
            f"frontier the captured territory opens up, and how exposed you'd be to a "
            f"counter-attack afterward. T{best['src']} \u2192 T{best['dst']} comes out on top."
        )
        return AgentThought(
            agent=self.name, headline=headline, detail=detail,
            data={"shortlist": shortlist},
        )
