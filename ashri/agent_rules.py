"""Fixed-rule agent: a hand-written subgoal state machine. No learning."""
from __future__ import annotations

from enum import Enum

from .actions import Action, Direction, DIR_DELTAS
from .pathfinding import bfs_path, neighbors
from .world import Observation, GridWorld, KEY, DOOR, CHARGER, Pos


class Subgoal(str, Enum):
    GET_KEY = "get_key"
    OPEN_DOOR = "open_door"
    GO_TO_CHARGER = "go_to_charger"


class RuleBasedAgent:
    """
    Rules:
      1. No key yet      -> go next to the key, face it, PICK_UP
      2. Door still shut -> go next to the door, face it, OPEN
      3. Otherwise       -> walk to the charger
    """

    def __init__(self):
        self.subgoal = Subgoal.GET_KEY

    def reset(self):
        self.subgoal = Subgoal.GET_KEY

    def act(self, obs: Observation) -> Action:
        self._update_subgoal(obs)
        if self.subgoal == Subgoal.GET_KEY:
            return self._interact(obs, obs.find(KEY), Action.PICK_UP)
        if self.subgoal == Subgoal.OPEN_DOOR:
            return self._interact(obs, obs.find(DOOR), Action.OPEN)
        return self._walk_to(obs, obs.find(CHARGER))

    # ---- subgoal logic --------------------------------------------
    def _update_subgoal(self, obs: Observation):
        if not obs.has_key:
            self.subgoal = Subgoal.GET_KEY
        elif obs.find(DOOR) is not None:
            self.subgoal = Subgoal.OPEN_DOOR
        else:
            self.subgoal = Subgoal.GO_TO_CHARGER

    # ---- movement primitives --------------------------------------
    @staticmethod
    def _passable(obs: Observation):
        return lambda p: (0 <= p[0] < len(obs.grid) and 0 <= p[1] < len(obs.grid[0])
                          and GridWorld.is_walkable(obs.grid[p[0]][p[1]]))

    def _interact(self, obs: Observation, target: Pos | None, action: Action) -> Action:
        """Stand next to `target`, face it, then perform `action`."""
        if target is None:
            return Action.WAIT
        passable = self._passable(obs)
        stand_cells = [n for n in neighbors(target) if passable(n)]
        if obs.agent_pos in stand_cells:
            needed = self._direction_to(obs.agent_pos, target)
            return action if obs.agent_dir == needed else self._turn_toward(obs.agent_dir, needed)
        return self._follow_path(obs, stand_cells)

    def _walk_to(self, obs: Observation, target: Pos | None) -> Action:
        if target is None:
            return Action.WAIT
        return self._follow_path(obs, [target])

    def _follow_path(self, obs: Observation, goals: list[Pos]) -> Action:
        path = bfs_path(obs.agent_pos, goals, self._passable(obs))
        if path is None or len(path) < 2:
            return Action.WAIT  # unreachable (rules can't solve this level)
        needed = self._direction_to(path[0], path[1])
        return Action.MOVE_FORWARD if obs.agent_dir == needed else self._turn_toward(obs.agent_dir, needed)

    @staticmethod
    def _direction_to(a: Pos, b: Pos) -> Direction:
        delta = (b[0] - a[0], b[1] - a[1])
        return next(d for d, v in DIR_DELTAS.items() if v == delta)

    @staticmethod
    def _turn_toward(current: Direction, needed: Direction) -> Action:
        return Action.TURN_LEFT if (current - needed) % 4 == 1 else Action.TURN_RIGHT
