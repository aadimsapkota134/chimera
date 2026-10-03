"""A tiny deterministic grid world: walls, one key, one door, one charger, one agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .actions import Action, Direction, DIR_DELTAS, DIR_ARROWS

# Tile symbols
WALL, FLOOR, KEY, DOOR, OPEN_DOOR, CHARGER = "#", ".", "K", "D", "O", "C"
AGENT = "A"  # only used in level files; the agent is tracked separately

Pos = tuple[int, int]


@dataclass(frozen=True)
class Observation:
    """What the agent gets each step. v0.1 is symbolic: it sees the whole grid."""
    grid: tuple[str, ...]
    agent_pos: Pos
    agent_dir: Direction
    has_key: bool
    step_count: int

    def find(self, tile: str) -> Pos | None:
        for r, row in enumerate(self.grid):
            c = row.find(tile)
            if c != -1:
                return (r, c)
        return None


@dataclass
class StepResult:
    obs: Observation
    done: bool
    success: bool
    info: dict = field(default_factory=dict)


class GridWorld:
    def __init__(self, layout: str, max_steps: int = 500):
        rows = [line.replace(" ", FLOOR) for line in layout.strip("\n").splitlines()]
        if len({len(r) for r in rows}) != 1:
            raise ValueError("All rows in a level must have the same width.")
        agent_pos = None
        grid = []
        for r, row in enumerate(rows):
            if AGENT in row:
                agent_pos = (r, row.index(AGENT))
                row = row.replace(AGENT, FLOOR)
            grid.append(list(row))
        if agent_pos is None:
            raise ValueError("Level has no agent ('A').")
        self._start_grid, self._start_pos = grid, agent_pos
        self.max_steps = max_steps
        self.reset()

    @classmethod
    def from_file(cls, path: str | Path, **kw) -> "GridWorld":
        return cls(Path(path).read_text(), **kw)

    # ---- lifecycle -------------------------------------------------
    def reset(self) -> Observation:
        self.grid = [row[:] for row in self._start_grid]
        self.agent_pos = self._start_pos
        self.agent_dir = Direction.EAST
        self.has_key = False
        self.step_count = 0
        self.done = False
        return self.observe()

    def observe(self) -> Observation:
        return Observation(
            grid=tuple("".join(r) for r in self.grid),
            agent_pos=self.agent_pos,
            agent_dir=self.agent_dir,
            has_key=self.has_key,
            step_count=self.step_count,
        )

    # ---- helpers ---------------------------------------------------
    def tile(self, pos: Pos) -> str:
        r, c = pos
        if 0 <= r < len(self.grid) and 0 <= c < len(self.grid[0]):
            return self.grid[r][c]
        return WALL

    def front(self) -> Pos:
        dr, dc = DIR_DELTAS[self.agent_dir]
        return (self.agent_pos[0] + dr, self.agent_pos[1] + dc)

    @staticmethod
    def is_walkable(tile: str) -> bool:
        return tile in (FLOOR, OPEN_DOOR, CHARGER)

    # ---- dynamics --------------------------------------------------
    def step(self, action: Action) -> StepResult:
        if self.done:
            raise RuntimeError("Episode finished; call reset().")
        invalid, event = False, ""

        if action == Action.TURN_LEFT:
            self.agent_dir = Direction((self.agent_dir - 1) % 4)
        elif action == Action.TURN_RIGHT:
            self.agent_dir = Direction((self.agent_dir + 1) % 4)
        elif action == Action.MOVE_FORWARD:
            target = self.front()
            if self.is_walkable(self.tile(target)):
                self.agent_pos = target
            else:
                invalid, event = True, "blocked"
        elif action == Action.PICK_UP:
            r, c = self.front()
            if self.tile((r, c)) == KEY and not self.has_key:
                self.grid[r][c] = FLOOR
                self.has_key = True
                event = "picked up key"
            else:
                invalid, event = True, "nothing to pick up"
        elif action == Action.OPEN:
            r, c = self.front()
            if self.tile((r, c)) == DOOR and self.has_key:
                self.grid[r][c] = OPEN_DOOR
                event = "opened door"
            else:
                invalid, event = True, "cannot open"
        elif action == Action.WAIT:
            pass

        self.step_count += 1
        success = self.tile(self.agent_pos) == CHARGER
        self.done = success or self.step_count >= self.max_steps
        return StepResult(self.observe(), self.done, success,
                          {"invalid": invalid, "event": event})

    # ---- display ---------------------------------------------------
    def render(self) -> str:
        rows = ["".join(r) for r in self.grid]
        r, c = self.agent_pos
        rows[r] = rows[r][:c] + DIR_ARROWS[self.agent_dir] + rows[r][c + 1:]
        return "\n".join(rows)
