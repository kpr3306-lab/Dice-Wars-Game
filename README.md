# Dice Wars — Streamlit Edition

A Streamlit rebuild of the Flask/Canvas Dice Wars project, for one-click
deployment on Streamlit Community Cloud. Same game engine, same four-agent
AI/advisor system — a reworked, click-driven presentation layer.

**Requires Python 3.10+.** `game/engine.py` uses PEP 604 union-type syntax
(`int | None`), which is a hard requirement of 3.10 or newer (it raises a
`TypeError` on 3.9 and earlier). Nothing else in the codebase needs anything
newer than that.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`. The **Instructions** and **Behind the
Scenes** pages appear automatically in the sidebar (Streamlit's built-in
multipage routing — anything in `pages/` becomes a nav entry).

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repo (root of the repo = this folder, so
   `streamlit_app.py` sits at the repo root).
2. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with
   GitHub → **New app**.
3. Pick your repo/branch, set **Main file path** to `streamlit_app.py`.
4. Click **Deploy**. That's the whole process — no build command, no
   worker/process config, no Python-version pinning needed.

You'll get a URL like `https://<something>.streamlit.app`.

## What changed vs. the Flask version, and why

| Flask/Canvas version | Streamlit version | Why |
|---|---|---|
| Flask-SocketIO WebSocket push | Plain Streamlit reruns + `st.session_state` | Streamlit has no persistent WebSocket event model to hook into |
| CSS keyframe dice-tumble animation | A `.dw-overlay-backdrop` / `.dw-overlay-modal` placeholder updated in a loop with `time.sleep` between frames, centered over the viewport | No custom JS in a stock Streamlit deploy; this reproduces "tumble then reveal" as a true centered popup using only Python + CSS |
| Live-streaming agent reasoning feed | Same feed, but revealed step-by-step *within one script run* rather than pushed live over a socket | Streamlit can't push mid-turn from server to client outside a script execution, but updating a placeholder in a loop during that execution still animates |
| Canvas click-to-attack | Native click-to-attack: click a territory to select it, click a highlighted neighbor to attack, via Plotly's `on_select` event on a marker trace | Streamlit 1.3x+ added first-party click-selection events for Plotly charts, so this no longer needs a third-party component (and no longer needs dropdowns either) |
| gunicorn + eventlet, `-w 1`, in-memory `GAMES` dict keyed by session | `st.session_state` (Streamlit's own per-browser-session store) | Streamlit handles session isolation for you — this is the one part that's genuinely simpler here |

**What's unchanged:** `game/engine.py` and every file in `agents/` are the
same pure-Python logic as the Flask version — combat, reinforcement rules,
the Strategy/Attack/Defense/Oracle agents, Monte Carlo win-probability, all
of it. Only the presentation layer and the map generator were reworked.

## Maps: randomized layout, fixed territory count

Each map *size* (Skirmish Isle / Twin Peninsulas / Grand Continent) now has
several pre-generated **variants** — `game/data/<map_id>_a.json` through
`_d.json` — each with its own randomized coastline, seed scatter, and
pattern of interior "holes" (cells deliberately left out of the tiling, so
the board has lake-like gaps instead of tiling edge-to-edge, same as the
original Dice Wars board). `GameState.__init__` picks a variant at random,
seeded by the match's own seed, so a given match is still fully
reproducible from that seed. Territory *count* is always exactly the
size's target (18 / 28 / 40) — holes are carved out only after first
over-generating territories, and only ever removed if the remainder stays
one connected landmass (checked with a BFS after every candidate removal).
Regenerate or add variants with `python generate_maps.py`.

## Notes for the write-up

- Since maps are pre-generated JSON, **scipy/Shapely aren't required at
  deploy time at all** — only `streamlit` and `plotly` are runtime
  dependencies (see `requirements.txt`). `requirements-dev.txt` has the
  geometry packages, only needed if you want to run `generate_maps.py`
  yourself to add or regenerate map variants.
- Because Streamlit reruns the whole script on each interaction, the AI's
  full turn (goal → attacks → reinforcement) runs synchronously inside one
  script execution and reveals itself step-by-step via placeholders — each
  capture pops up the same centered battle modal the human's own attacks
  use, then the board redraws in place, before moving to the next step. It
  isn't pushed from a background process the way the Socket.IO version was;
  worth a sentence in your report if you're asked to justify the platform
  choice, since a grader who compares this to the Flask version may notice
  the live feed no longer updates *during* server-side computation
  happening elsewhere — here, it's the same script producing both.
