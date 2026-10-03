from ashri.actions import Action, Direction
from ashri.world import GridWorld

LAYOUT = """
######
#AKDC#
######
"""


def test_wall_blocks_and_counts_invalid():
    w = GridWorld(LAYOUT)
    w.step(Action.TURN_LEFT)  # face north (wall)
    r = w.step(Action.MOVE_FORWARD)
    assert r.info["invalid"] and w.agent_pos == (1, 1)


def test_key_blocks_until_picked_up():
    w = GridWorld(LAYOUT)
    assert w.step(Action.MOVE_FORWARD).info["invalid"]
    assert w.step(Action.PICK_UP).info["event"] == "picked up key"
    assert not w.step(Action.MOVE_FORWARD).info["invalid"]


def test_door_needs_key():
    w = GridWorld(LAYOUT)
    w.step(Action.PICK_UP); w.step(Action.MOVE_FORWARD)
    assert w.has_key
    assert w.step(Action.OPEN).info["event"] == "opened door"


def test_reaching_charger_succeeds():
    w = GridWorld(LAYOUT)
    for a in [Action.PICK_UP, Action.MOVE_FORWARD, Action.OPEN,
              Action.MOVE_FORWARD, Action.MOVE_FORWARD]:
        r = w.step(a)
    assert r.success and r.done


def test_turning_wraps():
    w = GridWorld(LAYOUT)
    for _ in range(4):
        w.step(Action.TURN_RIGHT)
    assert w.agent_dir == Direction.EAST
