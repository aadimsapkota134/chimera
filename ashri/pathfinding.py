from __future__ import annotations

from collections import deque
from typing import Callable, Iterable

from .actions import DIR_DELTAS

Pos = tuple[int, int]


def neighbors(pos: Pos) -> list[Pos]:
    return [(pos[0] + dr, pos[1] + dc) for dr, dc in DIR_DELTAS.values()]


def bfs_path(start: Pos, goals: Iterable[Pos],
             passable: Callable[[Pos], bool]) -> list[Pos] | None:
    """Shortest path from start to any goal. Returns positions incl. start and goal."""
    goals = set(goals)
    if start in goals:
        return [start]
    prev: dict[Pos, Pos | None] = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for nxt in neighbors(cur):
            if nxt in prev or not passable(nxt):
                continue
            prev[nxt] = cur
            if nxt in goals:
                path = [nxt]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                return path[::-1]
            queue.append(nxt)
    return None
