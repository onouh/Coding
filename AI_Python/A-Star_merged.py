"""
A* (A-Star) Search Algorithm
Implements A* with Manhattan / Euclidean / Octile heuristics, a priority queue,
a goal-direction filter for guided exploration, and rich matplotlib visualisation.

Supports:
  • 2-D weighted grids  (astar_grid)
  • Arbitrary weighted graphs  (astar_graph)
  • Static snapshot visualisation  (visualize_grid_result, visualize_graph_result)
  • Step-by-step animated exploration  (visualize_grid_process)
"""

from __future__ import annotations

import heapq
import math
import time
from dataclasses import dataclass
from itertools import count
from typing import Callable, Dict, Hashable, Iterable, List, Optional, Sequence, Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
#  TYPE ALIASES
# ─────────────────────────────────────────────────────────────────────────────

Node               = Hashable
GridNode           = Tuple[int, int]
NeighborFunction   = Callable[[Node], Iterable[Tuple[Node, float]]]
HeuristicFunction  = Callable[[Node, Node], float]
NeighborFilter     = Callable[
    [Node, List[Tuple[Node, float]], Node, HeuristicFunction],
    List[Tuple[Node, float]],
]


# ─────────────────────────────────────────────────────────────────────────────
#  RESULT DATACLASS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AStarResult:
    path:           List[Node]
    cost:           float
    explored_order: List[Node]


# ─────────────────────────────────────────────────────────────────────────────
#  HEURISTIC FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def manhattan_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Manhattan distance – admissible for 4-directional grids."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Euclidean straight-line distance."""
    return math.dist(a, b)


def octile_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Octile distance – admissible for 8-directional grids."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)


def zero_heuristic(_: Node, __: Node) -> float:
    """Degenerate heuristic that turns A* into Dijkstra's algorithm."""
    return 0.0


def _grid_heuristic(name: str) -> Callable[[GridNode, GridNode], float]:
    """Return the named grid heuristic function."""
    opt = name.lower()
    if opt == "manhattan":
        return manhattan_distance
    if opt == "euclidean":
        return euclidean_distance
    if opt == "octile":
        return octile_distance
    raise ValueError("Unsupported heuristic. Choose 'manhattan', 'euclidean', or 'octile'.")


# ─────────────────────────────────────────────────────────────────────────────
#  GOAL-DIRECTION FILTER  (from astar.py)
# ─────────────────────────────────────────────────────────────────────────────

def grid_direction_filter(
    current:   GridNode,
    neighbors: List[Tuple[GridNode, float]],
    goal:      GridNode,
    heuristic: HeuristicFunction,
) -> List[Tuple[GridNode, float]]:
    """
    Prefer neighbors that move toward (or stay neutral to) the goal.

    A neighbor is classified as "away" when:
      1. Its heuristic distance to the goal is greater than the current node's, AND
      2. The step direction has a negative dot-product with the goal vector.

    When at least one "toward-or-neutral" neighbor exists, away-neighbours are
    suppressed.  If ALL neighbours are away (e.g. the agent is boxed in), the
    full candidate set is used so completeness is preserved.

    Notes
    -----
    This filter biases the search without sacrificing optimality on admissible
    heuristics, because the discarded neighbors would only be reconsidered if
    they later appeared with a genuinely lower g-score.
    """
    current_h  = heuristic(current, goal)
    goal_vec   = (goal[0] - current[0], goal[1] - current[1])

    toward, away = [], []
    for neighbor, cost in neighbors:
        next_h   = heuristic(neighbor, goal)
        move_vec = (neighbor[0] - current[0], neighbor[1] - current[1])
        dot      = move_vec[0] * goal_vec[0] + move_vec[1] * goal_vec[1]
        is_away  = (next_h > current_h) and (dot < 0)
        (away if is_away else toward).append((neighbor, cost))

    return toward if toward else (toward + away)


# ─────────────────────────────────────────────────────────────────────────────
#  PATH RECONSTRUCTION
# ─────────────────────────────────────────────────────────────────────────────

def reconstruct_path(
    came_from: Dict[Node, Node],
    start:     Node,
    goal:      Node,
) -> List[Node]:
    """Walk the came_from map backwards from goal to start."""
    if goal == start:
        return [start]
    if goal not in came_from:
        return []

    path, current = [goal], goal
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


# ─────────────────────────────────────────────────────────────────────────────
#  CORE A* ALGORITHM
# ─────────────────────────────────────────────────────────────────────────────

def astar(
    start:           Node,
    goal:            Node,
    neighbors:       NeighborFunction,
    heuristic:       HeuristicFunction,
    neighbor_filter: Optional[NeighborFilter] = None,
) -> AStarResult:
    """
    Generic A* search.

    Parameters
    ----------
    start           : starting node (any hashable)
    goal            : target node
    neighbors       : callable(node) → iterable of (neighbor, step_cost)
    heuristic       : callable(node, goal) → estimated remaining cost
    neighbor_filter : optional callable that prunes the raw neighbor list
                      before updating g-scores; receives
                      (current, raw_neighbors, goal, heuristic) and returns
                      a filtered list.  Pass ``grid_direction_filter`` for
                      guided grid search.

    Returns
    -------
    AStarResult with .path, .cost, and .explored_order
    """
    frontier:   List[Tuple[float, int, Node]] = []
    tie_breaker = count()
    heapq.heappush(frontier, (heuristic(start, goal), next(tie_breaker), start))

    came_from:      Dict[Node, Node]  = {}
    g_score:        Dict[Node, float] = {start: 0.0}
    closed_set:     set               = set()
    explored_order: List[Node]        = []

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current in closed_set:
            continue
        closed_set.add(current)
        explored_order.append(current)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            return AStarResult(
                path=path,
                cost=g_score[goal],
                explored_order=explored_order,
            )

        # Collect raw neighbours, then optionally apply goal-direction filter.
        raw = list(neighbors(current))
        if neighbor_filter is not None:
            raw = neighbor_filter(current, raw, goal, heuristic)

        for neighbor, step_cost in raw:
            if step_cost < 0:
                raise ValueError("A* requires non-negative edge costs.")
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + step_cost
            if tentative_g < g_score.get(neighbor, math.inf):
                came_from[neighbor] = current
                g_score[neighbor]   = tentative_g
                f_score             = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(frontier, (f_score, next(tie_breaker), neighbor))

    return AStarResult(path=[], cost=math.inf, explored_order=explored_order)


# ─────────────────────────────────────────────────────────────────────────────
#  GRID HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _is_blocked(cell: object) -> bool:
    """Return True when a grid cell is impassable."""
    return cell is None or (isinstance(cell, (int, float)) and cell < 0)


# ─────────────────────────────────────────────────────────────────────────────
#  GRID SEARCH  (astar_grid)
# ─────────────────────────────────────────────────────────────────────────────

def astar_grid(
    grid:           Sequence[Sequence[Optional[float]]],
    start:          GridNode,
    goal:           GridNode,
    heuristic_name: str  = "manhattan",
    allow_diagonal: bool = False,
    use_direction_filter: bool = True,
) -> AStarResult:
    """
    A* on a 2-D grid.

    Grid encoding
    -------------
    None or negative  →  impassable obstacle
    positive number   →  traversable; the value is used as the terrain cost
                         multiplier (1.0 = free, 2.0 = twice as costly, etc.)

    Parameters
    ----------
    grid                 : 2-D sequence (rows × cols)
    start                : (row, col) of the starting cell
    goal                 : (row, col) of the target cell
    heuristic_name       : 'manhattan', 'euclidean', or 'octile'
    allow_diagonal       : enable 8-directional movement
    use_direction_filter : apply goal-direction filter (recommended; default True)
    """
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    if not rows or not cols:
        raise ValueError("Grid must be non-empty.")

    def in_bounds(node: GridNode) -> bool:
        r, c = node
        return 0 <= r < rows and 0 <= c < cols

    if not in_bounds(start) or not in_bounds(goal):
        raise ValueError("Start and goal must be inside the grid.")
    if _is_blocked(grid[start[0]][start[1]]) or _is_blocked(grid[goal[0]][goal[1]]):
        raise ValueError("Start and goal must be on traversable cells.")

    # Build movement directions: cardinal + optional diagonals.
    moves: List[Tuple[int, int, float]] = [
        (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
    ]
    if allow_diagonal:
        d = math.sqrt(2)
        moves.extend([(1, 1, d), (1, -1, d), (-1, 1, d), (-1, -1, d)])

    def neighbors(node: GridNode) -> Iterable[Tuple[GridNode, float]]:
        r, c = node
        for dr, dc, base_mult in moves:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if not in_bounds(nxt):
                continue
            cell = grid[nr][nc]
            if _is_blocked(cell):
                continue
            terrain = float(cell) if isinstance(cell, (int, float)) else 1.0
            yield nxt, terrain * base_mult

    heuristic = _grid_heuristic(heuristic_name)
    flt       = grid_direction_filter if use_direction_filter else None

    return astar(start, goal, neighbors, heuristic, neighbor_filter=flt)


# ─────────────────────────────────────────────────────────────────────────────
#  GRAPH SEARCH  (astar_graph)
# ─────────────────────────────────────────────────────────────────────────────

def astar_graph(
    graph:          Dict[Node, Sequence[Tuple[Node, float]]],
    start:          Node,
    goal:           Node,
    positions:      Optional[Dict[Node, Tuple[float, float]]] = None,
    heuristic_name: str = "euclidean",
) -> AStarResult:
    """
    A* on an arbitrary weighted graph.

    Parameters
    ----------
    graph          : adjacency dict  {node: [(neighbor, cost), ...]}
    start          : starting node
    goal           : target node
    positions      : optional {node: (x, y)} for spatial heuristics;
                     falls back to zero heuristic (Dijkstra) when absent
    heuristic_name : 'manhattan' or 'euclidean' (only used with positions)
    """
    if start not in graph or goal not in graph:
        raise ValueError("Start and goal must exist in the graph.")

    opt = heuristic_name.lower()
    if positions is None:
        heuristic: HeuristicFunction = zero_heuristic
    elif opt == "manhattan":
        heuristic = lambda a, b: manhattan_distance(positions[a], positions[b])
    elif opt == "euclidean":
        heuristic = lambda a, b: euclidean_distance(positions[a], positions[b])
    else:
        raise ValueError("Unsupported heuristic. Choose 'manhattan' or 'euclidean'.")

    def neighbors(node: Node) -> Iterable[Tuple[Node, float]]:
        return graph.get(node, ())

    # Direction filter is grid-specific; graphs use the plain search.
    return astar(start, goal, neighbors, heuristic, neighbor_filter=None)


# ─────────────────────────────────────────────────────────────────────────────
#  VISUALISATION – STATIC SNAPSHOT  (grid)
# ─────────────────────────────────────────────────────────────────────────────

# RGB colour palette (values in [0, 1])
_FREE     = [1.00, 1.00, 1.00]   # white         – traversable cell
_OBSTACLE = [0.20, 0.20, 0.20]   # dark grey      – blocked cell
_TERRAIN  = [0.85, 0.75, 0.50]   # tan            – weighted terrain (cost > 1)
_EXPLORED = [0.70, 0.85, 1.00]   # light blue     – explored by A*
_PATH_CLR = [0.10, 0.70, 0.30]   # green          – shortest path
_START_CL = [0.95, 0.60, 0.10]   # orange         – start cell
_GOAL_CLR = [0.90, 0.15, 0.15]   # red            – goal cell


def _build_base_image(
    grid: Sequence[Sequence[Optional[float]]],
) -> np.ndarray:
    """Rasterise the raw grid into an RGB numpy array."""
    rows, cols = len(grid), len(grid[0])
    img = np.zeros((rows, cols, 3))
    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if _is_blocked(cell):
                img[r, c] = _OBSTACLE
            elif isinstance(cell, (int, float)) and float(cell) > 1.0:
                img[r, c] = _TERRAIN
            else:
                img[r, c] = _FREE
    return img


def visualize_grid_result(
    grid:   Sequence[Sequence[Optional[float]]],
    result: AStarResult,
    start:  GridNode,
    goal:   GridNode,
    title:  str,
) -> None:
    """
    Render a static grid snapshot showing explored cells and the final path.

    Colours
    -------
    White       free cell       Dark grey  obstacle
    Tan         weighted cell   Light blue explored by A*
    Green       shortest path   Orange     start     Red  goal
    """
    rows, cols = len(grid), len(grid[0])
    img = _build_base_image(grid)

    # Paint explored nodes (skip start / goal – they get their own colour).
    for node in result.explored_order:
        r, c = node
        if img[r, c].tolist() == _FREE:
            img[r, c] = _EXPLORED

    # Paint path.
    for r, c in result.path:
        img[r, c] = _PATH_CLR

    # Always draw start / goal on top.
    img[start[0], start[1]] = _START_CL
    img[goal[0],  goal[1]]  = _GOAL_CLR

    fig, ax = plt.subplots(figsize=(max(6, cols * 0.6), max(5, rows * 0.6)))
    ax.imshow(img, interpolation="nearest")

    # Fine grid lines.
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which="minor", color="#cccccc", linewidth=0.5)
    ax.tick_params(which="minor", size=0)
    ax.set_xticks(range(cols)); ax.set_xticklabels(range(cols), fontsize=7)
    ax.set_yticks(range(rows)); ax.set_yticklabels(range(rows), fontsize=7)

    # S / G labels.
    ax.text(start[1], start[0], "S", ha="center", va="center",
            fontweight="bold", fontsize=9, color="white")
    ax.text(goal[1],  goal[0],  "G", ha="center", va="center",
            fontweight="bold", fontsize=9, color="white")

    legend = [
        mpatches.Patch(color=_START_CL, label="Start"),
        mpatches.Patch(color=_GOAL_CLR, label="Goal"),
        mpatches.Patch(color=_PATH_CLR, label="Path"),
        mpatches.Patch(color=_EXPLORED, label="Explored"),
        mpatches.Patch(color=_OBSTACLE, label="Obstacle"),
        mpatches.Patch(color=_TERRAIN,  label="Weighted terrain"),
    ]
    ax.legend(handles=legend, loc="upper right",
              fontsize=7, framealpha=0.9, bbox_to_anchor=(1.28, 1.0))

    ax.set_title(title, fontsize=11, fontweight="bold")
    plt.tight_layout()


# ─────────────────────────────────────────────────────────────────────────────
#  VISUALISATION – ANIMATED PROCESS  (grid)
# ─────────────────────────────────────────────────────────────────────────────

def visualize_grid_process(
    grid:           Sequence[Sequence[Optional[float]]],
    result:         AStarResult,
    start:          GridNode,
    goal:           GridNode,
    title:          str = "A* Process Visualisation",
    step_delay:     float = 0.03,
) -> None:
    """
    Animate node exploration followed by path reconstruction step-by-step.

    Each explored node is revealed in the exact order A* visited it, then the
    final path is drawn cell-by-cell.
    """
    rows, cols = len(grid), len(grid[0])
    img = _build_base_image(grid)

    fig, ax = plt.subplots(figsize=(max(6, cols * 0.6), max(5, rows * 0.6)))
    im = ax.imshow(img, interpolation="nearest")

    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which="minor", color="#cccccc", linewidth=0.5)
    ax.tick_params(which="minor", size=0)
    ax.set_xticks(range(cols)); ax.set_xticklabels(range(cols), fontsize=7)
    ax.set_yticks(range(rows)); ax.set_yticklabels(range(rows), fontsize=7)
    ax.set_title(title, fontsize=11, fontweight="bold")

    img[start[0], start[1]] = _START_CL
    img[goal[0],  goal[1]]  = _GOAL_CLR
    im.set_data(img)
    plt.pause(step_delay)

    # Animate exploration.
    for r, c in result.explored_order:
        if (r, c) in (start, goal):
            continue
        if img[r, c].tolist() == _FREE:
            img[r, c] = _EXPLORED
        im.set_data(img)
        plt.pause(step_delay)

    # Animate path.
    for r, c in result.path:
        if (r, c) in (start, goal):
            continue
        img[r, c] = _PATH_CLR
        im.set_data(img)
        plt.pause(step_delay)

    # Restore start / goal colours.
    img[start[0], start[1]] = _START_CL
    img[goal[0],  goal[1]]  = _GOAL_CLR
    im.set_data(img)
    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────────────────────────────────────
#  VISUALISATION – GRAPH
# ─────────────────────────────────────────────────────────────────────────────

def visualize_graph_result(
    graph:     Dict[Node, Sequence[Tuple[Node, float]]],
    positions: Dict[Node, Tuple[float, float]],
    result:    AStarResult,
    start:     Node,
    goal:      Node,
    title:     str,
) -> None:
    """Draw an arbitrary weighted graph with the A* result overlaid."""
    fig, ax = plt.subplots(figsize=(7, 4))

    # Draw all edges with weight labels.
    for src, edges in graph.items():
        x1, y1 = positions[src]
        for dst, weight in edges:
            x2, y2 = positions[dst]
            ax.plot([x1, x2], [y1, y2], color="lightgray", linewidth=1.4)
            mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            ax.text(mx, my + 0.05, f"{weight:g}", color="dimgray", fontsize=8)

    # Colour explored nodes by visit order.
    for idx, node in enumerate(result.explored_order):
        x, y = positions[node]
        ax.scatter([x], [y], c=[[idx]], cmap="viridis", s=200, alpha=0.6)

    # Draw all node markers with labels.
    for node, (x, y) in positions.items():
        clr  = "skyblue"
        size = 450
        if node == start: clr, size = "lime",  520
        if node == goal:  clr, size = "gold",  520
        ax.scatter([x], [y], c=clr, edgecolors="black", s=size)
        ax.text(x, y, str(node), ha="center", va="center",
                fontsize=10, fontweight="bold")

    # Highlight shortest path edges.
    if result.path:
        for i in range(len(result.path) - 1):
            a, b   = result.path[i], result.path[i + 1]
            x1, y1 = positions[a]
            x2, y2 = positions[b]
            ax.plot([x1, x2], [y1, y2], color="red", linewidth=3)

    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()


# ─────────────────────────────────────────────────────────────────────────────
#  TEST SUITE
# ─────────────────────────────────────────────────────────────────────────────

def run_test_cases(show_plots: bool = True) -> None:
    """Run all built-in test cases and print a comparison report."""

    # ── Test 1: Unweighted grid with obstacles ──────────────────────────────
    print("\nTest Case 1: Unweighted grid with obstacles")
    grid1 = [
        [1, 1, 1, 1, 1],
        [1, None, None, None, 1],
        [1, 1, 1, None, 1],
        [None, None, 1, 1, 1],
    ]
    start1, goal1 = (0, 0), (3, 4)
    result1 = astar_grid(grid1, start1, goal1, heuristic_name="manhattan")
    print(f"  Path     : {result1.path}")
    print(f"  Cost     : {result1.cost}")
    print(f"  Explored : {len(result1.explored_order)}")
    assert result1.path, "Case 1 failed: no path found"

    # ── Test 2: Weighted grid with obstacles ────────────────────────────────
    print("\nTest Case 2: Weighted grid with obstacles")
    grid2 = [
        [1, 1, 5, 1, 1],
        [1, None, 5, None, 1],
        [1, 1, 1, 1, 1],
        [4, None, 2, None, 1],
        [1, 1, 1, 1, 1],
    ]
    start2, goal2 = (0, 0), (4, 4)
    result2 = astar_grid(grid2, start2, goal2, heuristic_name="euclidean")
    print(f"  Path     : {result2.path}")
    print(f"  Cost     : {result2.cost}")
    print(f"  Explored : {len(result2.explored_order)}")
    assert result2.path, "Case 2 failed: no path found"

    # ── Test 3: Weighted general graph ──────────────────────────────────────
    print("\nTest Case 3: Weighted general graph")
    graph = {
        "A": (("B", 1), ("C", 4)),
        "B": (("A", 1), ("C", 2), ("D", 5)),
        "C": (("A", 4), ("B", 2), ("D", 1), ("E", 7)),
        "D": (("B", 5), ("C", 1), ("E", 3)),
        "E": (("C", 7), ("D", 3)),
    }
    positions = {
        "A": (0, 0), "B": (1, 1), "C": (2, 0), "D": (3, 1), "E": (4, 0),
    }
    result3 = astar_graph(graph, "A", "E", positions, heuristic_name="euclidean")
    print(f"  Path     : {result3.path}")
    print(f"  Cost     : {result3.cost}")
    print(f"  Explored : {len(result3.explored_order)}")
    assert result3.path == ["A", "B", "C", "D", "E"], "Case 3 failed: wrong path"
    assert abs(result3.cost - 7.0) < 1e-9,            "Case 3 failed: wrong cost"

    # ── Test 4: No-path grid ────────────────────────────────────────────────
    print("\nTest Case 4: No-path grid")
    grid4 = [
        [1, 1, 1, 1, 1],
        [None, None, None, None, None],
        [1, 1, 1, 1, 1],
        [1, None, None, None, 1],
        [1, 1, 1, 1, 1],
    ]
    start4, goal4 = (0, 0), (4, 4)
    result4 = astar_grid(grid4, start4, goal4, heuristic_name="manhattan")
    print(f"  Path     : {result4.path}")
    print(f"  Cost     : {result4.cost}")
    print(f"  Explored : {len(result4.explored_order)}")
    assert result4.path == [],          "Case 4 failed: path should not exist"
    assert math.isinf(result4.cost),    "Case 4 failed: cost should be infinity"
    print("  ✓ Correct: no valid path exists.")

    # ── Test 5: 8-directional movement with octile heuristic ────────────────
    print("\nTest Case 5: Diagonal movement (8-directional)")
    grid5 = [
        [1, 1, 1, 1, 1, 1],
        [1, None, None, None, None, 1],
        [1, None, 1, 2, None, 1],
        [1, None, 1, 1, None, 1],
        [1, 1, 1, 1, 1, 1],
    ]
    start5, goal5 = (0, 0), (4, 5)
    result5 = astar_grid(
        grid5, start5, goal5,
        heuristic_name="octile",
        allow_diagonal=True,
    )
    print(f"  Path     : {result5.path}")
    print(f"  Cost     : {result5.cost:.2f}")
    print(f"  Explored : {len(result5.explored_order)}")
    assert result5.path, "Case 5 failed: no path found"

    # ── Plots ───────────────────────────────────────────────────────────────
    if show_plots:
        try:
            visualize_grid_result(
                grid1, result1, start1, goal1,
                "Case 1: Unweighted Grid (A* + Manhattan)",
            )
            visualize_grid_result(
                grid2, result2, start2, goal2,
                "Case 2: Weighted Grid (A* + Euclidean)",
            )
            visualize_graph_result(
                graph, positions, result3, "A", "E",
                "Case 3: Weighted Graph (A* + Euclidean)",
            )
            visualize_grid_result(
                grid4, result4, start4, goal4,
                "Case 4: No Path Scenario",
            )
            visualize_grid_result(
                grid5, result5, start5, goal5,
                "Case 5: Diagonal Movement (A* + Octile)",
            )
            plt.show()
        except ImportError:
            print("matplotlib / numpy not installed.  "
                  "Run: pip install matplotlib numpy")

    # ── Comparison report ───────────────────────────────────────────────────
    print("\nComparison Report")
    print("-" * 78)
    print(f"{'Setup':<26} {'Cost':>8} {'PathLen':>8} {'Explored':>10} {'Time(ms)':>10}")
    print("-" * 78)

    report_grid = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, None, None, None, 1, 2, 1],
        [1, 1, 1, None, 1, 2, 1],
        [1, None, 1, 1, 1, 2, 1],
        [1, None, 1, None, None, 2, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    report_start, report_goal = (0, 0), (5, 6)

    setups = [
        ("4-dir + Manhattan", "manhattan", False),
        ("4-dir + Euclidean", "euclidean", False),
        ("8-dir + Euclidean", "euclidean", True),
        ("8-dir + Octile",    "octile",    True),
    ]
    for label, h_name, diagonal in setups:
        t0 = time.perf_counter()
        res = astar_grid(
            report_grid, report_start, report_goal,
            heuristic_name=h_name, allow_diagonal=diagonal,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        print(
            f"{label:<26} {res.cost:>8.2f} {len(res.path):>8} "
            f"{len(res.explored_order):>10} {elapsed_ms:>10.3f}"
        )

    print("\nAll test cases passed.")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_test_cases(show_plots=True)
