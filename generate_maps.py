"""
Map Generator for Dice Wars Clone
-----------------------------------
Generates organic, hand-drawn-looking territory maps (NOT node graphs) by:
  1. Building an irregular island silhouette (randomized radial polygon, smoothed)
  2. Scattering seed points inside it (rejection-sampled for even spacing) --
     more seeds than the target territory count, so step 6 has slack to work with
  3. Computing a Voronoi diagram over the seeds
  4. Clipping each Voronoi cell to the island silhouette with Shapely
  5. Deriving adjacency directly from Voronoi ridge pairs
  6. Carving random "holes" (gaps/lakes) out of the interior by discarding a
     handful of cells -- each discard is only kept if the remaining cells are
     still a single connected landmass, so the territory graph never gets cut
     in two. This is what gives the board the irregular, gap-riddled look of
     the original Dice Wars board instead of a seamless tiling.
  7. Re-indexing down to exactly the requested territory count.

Several randomized variants are generated per map size (different seed each
time, different hole pattern each time); the app picks one at random -- via
the match's own seed, so a given match is still reproducible -- every time a
new game starts. Territory *count* is always exactly the size's target; only
the layout, coastline, and hole pattern vary.

Output: JSON files in game/data/, named "<map_id>_<variant>.json", consumed
by board_renderer.py. Each file is fully self-contained (no runtime geometry
dependency -- numpy/scipy/shapely are dev-only, used solely by this script).
"""
import json
import math
import random
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, Point


def make_island_silhouette(cx, cy, base_radius, n_points=24, jitter=0.35, seed=0):
    rnd = random.Random(seed)
    # Randomized radii per angle, then smoothed with a moving average so the
    # coastline looks hand-drawn rather than spiky/noisy.
    raw_radii = [base_radius * (1 + rnd.uniform(-jitter, jitter)) for _ in range(n_points)]
    smoothed = []
    for i in range(n_points):
        window = [raw_radii[(i + k) % n_points] for k in (-1, 0, 1)]
        smoothed.append(sum(window) / len(window))
    pts = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        r = smoothed[i]
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return Polygon(pts)


def poisson_ish_points(poly, n_target, min_dist, seed=0, max_attempts=12000):
    rnd = random.Random(seed)
    minx, miny, maxx, maxy = poly.bounds
    pts = []
    attempts = 0
    while len(pts) < n_target and attempts < max_attempts:
        attempts += 1
        x = rnd.uniform(minx, maxx)
        y = rnd.uniform(miny, maxy)
        p = Point(x, y)
        if not poly.contains(p):
            continue
        if all((x - qx) ** 2 + (y - qy) ** 2 >= min_dist ** 2 for qx, qy in pts):
            pts.append((x, y))
    return pts


def bounded_voronoi_regions(points, bounding_box):
    # Add far-away "ghost" points so every real cell is a closed, finite polygon.
    minx, miny, maxx, maxy = bounding_box
    span = max(maxx - minx, maxy - miny) * 10
    ghosts = [
        (minx - span, miny - span), (maxx + span, miny - span),
        (minx - span, maxy + span), (maxx + span, maxy + span),
        ((minx + maxx) / 2, miny - span), ((minx + maxx) / 2, maxy + span),
        (minx - span, (miny + maxy) / 2), (maxx + span, (miny + maxy) / 2),
    ]
    all_points = np.array(list(points) + ghosts)
    vor = Voronoi(all_points)
    return vor, len(points)


def _is_connected(neighbor_sets, keep_ids):
    """BFS connectivity check over the subgraph induced by keep_ids."""
    keep_ids = set(keep_ids)
    if not keep_ids:
        return True
    start = next(iter(keep_ids))
    seen = {start}
    stack = [start]
    while stack:
        cur = stack.pop()
        for n in neighbor_sets[cur]:
            if n in keep_ids and n not in seen:
                seen.add(n)
                stack.append(n)
    return seen == keep_ids


def carve_holes(territories, n_holes, rnd):
    """Randomly discard up to n_holes cells (becoming blank map gaps), only
    ever accepting a removal that leaves the remaining cells fully connected.
    Interior cells (more neighbors = less likely to be a coastal sliver) are
    preferred so holes read as lakes rather than bites out of the coastline,
    though coastal removals are allowed too for a rougher, less uniform edge."""
    neighbor_sets = {t["id"]: set(t["neighbors"]) for t in territories}
    alive = set(neighbor_sets.keys())
    candidates = sorted(alive, key=lambda tid: -len(neighbor_sets[tid]))  # most-connected first
    rnd.shuffle(candidates)
    # bias toward well-connected cells by trying higher-degree ones first most of the time
    candidates.sort(key=lambda tid: len(neighbor_sets[tid]), reverse=True)

    removed = set()
    for tid in candidates:
        if len(removed) >= n_holes:
            break
        if tid not in alive or len(neighbor_sets[tid]) < 3:
            continue  # keep low-degree (coastal/corner) cells to avoid fragmenting easily
        trial = alive - {tid}
        if _is_connected(neighbor_sets, trial):
            alive = trial
            removed.add(tid)

    kept = [t for t in territories if t["id"] in alive]
    for t in kept:
        t["neighbors"] = [n for n in t["neighbors"] if n in alive]
    return kept


def build_map(name, cx, cy, base_radius, n_territories, seed, hole_fraction=0.14, min_dist_factor=0.22):
    rnd = random.Random(seed)
    extra = max(2, round(n_territories * hole_fraction))
    seed_count = n_territories + extra

    island = make_island_silhouette(cx, cy, base_radius, seed=seed)
    min_dist = base_radius * min_dist_factor / math.sqrt(seed_count / 20)
    seeds = poisson_ish_points(island, seed_count, min_dist, seed=seed)
    vor, n_real = bounded_voronoi_regions(seeds, island.bounds)

    territories = []
    valid_index_map = {}  # original point index -> territory id (only for those that survive clipping)
    for i in range(n_real):
        region_index = vor.point_region[i]
        region = vor.regions[region_index]
        if -1 in region or len(region) == 0:
            continue
        cell_pts = [tuple(vor.vertices[v]) for v in region]
        try:
            cell_poly = Polygon(cell_pts)
            clipped = cell_poly.intersection(island)
        except Exception:
            continue
        if clipped.is_empty or clipped.area < 5:
            continue
        if clipped.geom_type == "MultiPolygon":
            clipped = max(clipped.geoms, key=lambda g: g.area)
        clipped_simplified = clipped.simplify(1.5, preserve_topology=True)
        coords = list(clipped_simplified.exterior.coords)
        tid = len(territories)
        valid_index_map[i] = tid
        centroid = clipped.centroid
        territories.append({
            "id": tid,
            "polygon": [[round(x, 1), round(y, 1)] for x, y in coords],
            "centroid": [round(centroid.x, 1), round(centroid.y, 1)],
            "neighbors": set(),
        })

    for (p1, p2) in vor.ridge_points:
        if p1 in valid_index_map and p2 in valid_index_map:
            a, b = valid_index_map[p1], valid_index_map[p2]
            territories[a]["neighbors"].add(b)
            territories[b]["neighbors"].add(a)

    for t in territories:
        t["neighbors"] = sorted(t["neighbors"])

    territories = [t for t in territories if t["neighbors"]]
    old_to_new = {t["id"]: i for i, t in enumerate(territories)}
    for t in territories:
        t["neighbors"] = sorted(old_to_new[n] for n in t["neighbors"] if n in old_to_new)
    for i, t in enumerate(territories):
        t["id"] = i

    # --- carve random holes/gaps, then trim (or accept a slightly smaller
    # board, if the generator ran short) down to exactly n_territories -------
    n_before_holes = len(territories)
    n_to_remove = max(0, n_before_holes - n_territories)
    territories = carve_holes(territories, n_to_remove, rnd)

    # If we still have more than the target (holes couldn't remove enough
    # without disconnecting the map), trim the extras from the lowest-degree
    # (least structurally important) cells, re-checking connectivity each time.
    while len(territories) > n_territories:
        neighbor_sets = {t["id"]: set(t["neighbors"]) for t in territories}
        alive = set(neighbor_sets.keys())
        by_degree = sorted(alive, key=lambda tid: len(neighbor_sets[tid]))
        trimmed_one = False
        for tid in by_degree:
            trial = alive - {tid}
            if trial and _is_connected(neighbor_sets, trial):
                territories = [t for t in territories if t["id"] != tid]
                for t in territories:
                    t["neighbors"] = [n for n in t["neighbors"] if n != tid]
                trimmed_one = True
                break
        if not trimmed_one:
            break  # can't safely trim further without disconnecting

    # final clean re-index
    old_to_new = {t["id"]: i for i, t in enumerate(territories)}
    for t in territories:
        t["neighbors"] = sorted(old_to_new[n] for n in t["neighbors"])
    for i, t in enumerate(territories):
        t["id"] = i

    minx, miny, maxx, maxy = island.bounds
    return {
        "name": name,
        "width": round(maxx - minx + 40, 1),
        "height": round(maxy - miny + 40, 1),
        "offset": [round(-minx + 20, 1), round(-miny + 20, 1)],
        "island_outline": [[round(x, 1), round(y, 1)] for x, y in island.exterior.coords],
        "territories": territories,
        "count": len(territories),
    }


def offset_map(m):
    ox, oy = m["offset"]
    for t in m["territories"]:
        t["polygon"] = [[x + ox, y + oy] for x, y in t["polygon"]]
        t["centroid"] = [t["centroid"][0] + ox, t["centroid"][1] + oy]
    m["island_outline"] = [[x + ox, y + oy] for x, y in m["island_outline"]]
    return m


VARIANT_LETTERS = "abcd"

if __name__ == "__main__":
    # (map_id, cx, cy, base_radius, target_territory_count, base_seed)
    specs = [
        ("skirmish_isle", 400, 300, 260, 18, 7),
        ("twin_peninsulas", 450, 320, 300, 28, 21),
        ("grand_continent", 500, 360, 340, 40, 99),
    ]
    for map_id, cx, cy, r, n, base_seed in specs:
        for vi, letter in enumerate(VARIANT_LETTERS):
            variant_seed = base_seed * 1000 + vi * 37 + 11
            # small random jitter to center/radius per variant for extra layout variety
            vrnd = random.Random(variant_seed)
            vcx = cx + vrnd.uniform(-20, 20)
            vcy = cy + vrnd.uniform(-20, 20)
            vr = r * vrnd.uniform(0.95, 1.05)
            m = build_map(map_id, vcx, vcy, vr, n, variant_seed)
            m = offset_map(m)
            path = f"/home/claude/dicewars/dicewars_streamlit/game/data/{map_id}_{letter}.json"
            with open(path, "w") as f:
                json.dump(m, f)
            print(f"{map_id}_{letter}: {m['count']} territories (target {n}) -> {path}")
