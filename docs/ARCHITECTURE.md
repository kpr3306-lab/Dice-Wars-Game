# Architecture

How Dice Wars is put together: the layers, how a turn flows, how each agent
decides, and the game engine API.

## Layers

```
┌──────────────────────────────────────────────────────────────┐
│ UI (Streamlit)                                               │
│  streamlit_app.py   map select, board, side panel, turn flow │
│  pages/             Instructions, Behind the Scenes          │
│  board_renderer.py  GameState dict -> Plotly figure          │
│  animation.py       battle/reinforcement popups, feed HTML   │
│  theme.py           CSS + header                             │
└───────────────┬──────────────────────────────┬───────────────┘
                │ reads/mutates                │ asks for moves
                ▼                              ▼
┌──────────────────────────────┐   ┌───────────────────────────┐
│ game/engine.py               │◄──│ agents/                   │
│  GameState (rules, combat,   │   │  AIController             │
│  reinforcement, win check)   │   │   Strategy→Attack→Defense │
│  game/data/*.json maps       │   │  OracleAgent (advisor)    │
└──────────────────────────────┘   └───────────────────────────┘
```

- **Engine** is pure Python with no UI code. It is deterministic given a seed
  (`random.Random(seed)`), so matches are reproducible.
- **Agents** only read the `GameState` and call its public methods. They
  never touch Streamlit.
- **UI** keeps one `GameState` per browser session in
  `st.session_state.game`, along with `selected_src` (selected attacker),
  `feed` (agent thoughts) and `click_message`.

## Turn flow

```
Human attack phase ──(End Attack Phase)──► end_turn_and_reinforce("human")
        ▲                                          │
        │                                          ▼
        │                               Human places dice
        │                       (Place Die / Auto-place rest)
        │                                          │
        │                                   switch_turn()
        │                                          ▼
        │                         AIController.run_turn(state)
        │                     1. StrategyAgent.think   -> goal
        │                     2. AttackAgent.think + state.attack, repeated
        │                     3. end_turn_and_reinforce("ai")
        │                        DefenseAgent.think    -> placements
        │                                          │
        │               steps replayed via animation.py (popups + feed)
        │                                          │
        └──────────────────── switch_turn() ◄──────┘
```

- The human's attack phase is when `turn_owner == "human"` and
  `pending_reinforcements == 0`.
- A board click is read from Plotly's `on_select` event
  (`get_clicked_tid` → `handle_board_click` in `streamlit_app.py`). First
  click selects an owned territory with 2+ dice and an enemy neighbour; second
  click on a highlighted neighbour calls `state.attack`.
- `AIController.run_turn` returns an ordered list of steps
  (`{"type": "thought", ...}` or `{"type": "attack_result", ...}`) which the UI
  replays one by one: thoughts go to the feed, attack results go to
  `play_battle_animation`, and reinforcement placements go to
  `show_reinforcement_overlay`.

## Agents

All agents extend `BaseAgent` and return an `AgentThought`
([agents/base_agent.py](../agents/base_agent.py)):

| Field | Meaning |
|---|---|
| `agent` | `"strategy"`, `"attack"`, `"defense"` or `"oracle"` |
| `headline` | One-line summary shown in the feed |
| `detail` | 1–3 sentences of reasoning |
| `data` | Raw numbers (goal, win probability, placements, …) |

### Strategy Agent — picks the turn's goal

Computes over the AI's territories:

- `dice_ratio` = AI dice ÷ human dice
- `exposure_ratio` = weak border territories (≤ 2 dice) ÷ all border territories
- `largest_group` = size of the AI's largest connected group

Rules, checked in order:

| Condition | Goal |
|---|---|
| `exposure_ratio > 0.45` and `dice_ratio < 1.15` | `DEFEND` |
| `dice_ratio ≥ 1.4` | `EXPAND` |
| `largest_group < 0.6 × territories` | `CONSOLIDATE` |
| otherwise | `TARGET_WEAK` |

### Attack Agent — executes attacks under the goal

For every legal attack, win probability comes from
`GameState.win_probability` — a **Monte Carlo simulation of 400 rolls**.
Moves below the goal's threshold are dropped; the rest are scored and the
best one is executed. This repeats until no move qualifies or the per-turn
cap is reached.

| Goal | Min win probability | Max attacks per turn |
|---|---|---|
| `EXPAND` | 0.55 | 6 |
| `TARGET_WEAK` | 0.62 | 3 |
| `CONSOLIDATE` | 0.75 | 1 |
| `DEFEND` | 0.85 | 1 |

Score = win probability, plus:

- `TARGET_WEAK`: `+ 0.3 × (1 − defender_dice / 8)` (prefers weak targets)
- `EXPAND`: `+ 0.05 ×` human neighbours of the target (prefers opening fronts)

### Defense Agent — places reinforcements

Runs after the AI's reinforcement pool is computed. Places dice one at a
time on the territory (below 8 dice) with the highest

```
vulnerability = sum(dice of enemy neighbours) − own dice
```

recomputing after each placement, so dice spread across the most threatened
border.

### Oracle Agent — advises the human

Not part of the AI pipeline. For every legal human attack:

```
frontier = 1 + enemy neighbours of the target
exposure = max(src_threat − 1, 0) + max(dst_threat − moved_dice, 0)
score    = win_prob × (1 + 0.15 × frontier) − 0.05 × exposure
```

where `src_threat` / `dst_threat` are the enemy dice adjacent to the source
(left with 1 die) and the captured target (holding `moved_dice`). The top 3
are shown in the **Cheat: Recommended Move** panel.

### Why a pipeline

Independent bots can contradict each other (e.g. attacking until nothing is
left to defend with). Passing the Strategy goal down means Attack and Defense
work toward the same read of the board each turn.

## Game engine API

[game/engine.py](../game/engine.py)

**Constants:** `MAX_DICE = 8`; `MAPS` maps `map_id` → display name
(`skirmish_isle`, `twin_peninsulas`, `grand_continent`).

**Data classes**

- `Territory(id, owner, dice, neighbors, polygon, centroid)` — `owner` is
  `"human"` or `"ai"`.
- `AttackResult(attacker_id, defender_id, attacker_rolls, defender_rolls,
  attacker_total, defender_total, success, attacker_dice_before,
  defender_dice_before)`.

**`GameState(map_id, seed=None)`**

| Method | Does |
|---|---|
| `owned_by(owner)` | List of territory ids owned by `owner` |
| `valid_attacks(owner)` | All `(src, dst)` pairs where `src` has 2+ dice and `dst` is an enemy neighbour |
| `connected_groups(owner)` / `largest_group_size(owner)` | Connected clusters (DFS) and the largest one's size |
| `win_probability(a_dice, d_dice)` | Monte Carlo estimate (400 trials) that the attacker wins |
| `attack(src, dst)` | Rolls dice, applies the result, logs it, checks for a winner; returns `AttackResult` |
| `end_turn_and_reinforce(owner)` | Sets `pending_reinforcements` to the largest group size (min 1) |
| `place_reinforcement(owner, tid)` | Adds one die if owned, below 8, and dice remain; returns `bool` |
| `auto_place_reinforcements(owner)` | Places all remaining dice on the lowest-dice border territories; returns placed ids |
| `switch_turn()` | Flips `turn_owner`; increments `turn_number` when it returns to the human |
| `to_dict()` | JSON-friendly snapshot used by the renderer |

Key attributes: `territories`, `turn_owner`, `turn_number`, `winner`,
`pending_reinforcements`, `log`, `last_attack`.

## Map files

Each `game/data/<map_id>_<variant>.json` contains:

```json
{
  "name": "skirmish_isle",
  "width": 643.9, "height": 598.7, "offset": [-76.7, -17.6],
  "island_outline": [[x, y], ...],
  "territories": [
    {"id": 0, "polygon": [[x, y], ...], "centroid": [x, y], "neighbors": [1, 4, ...]}
  ]
}
```

### Generation ([generate_maps.py](../generate_maps.py))

1. Build an irregular island outline (random radii, smoothed).
2. Scatter more seed points than needed inside it, evenly spaced.
3. Compute a Voronoi diagram (scipy) over the seeds.
4. Clip each cell to the island (Shapely).
5. Derive adjacency from Voronoi ridge pairs.
6. Remove random interior cells to make "holes", keeping a removal only if
   the remaining land is still connected (BFS).
7. Re-index to exactly the target count (18 / 28 / 40).

Run `python generate_maps.py` (with `requirements-dev.txt` installed) to
regenerate the variants.
