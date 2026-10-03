from enum import IntEnum


class Action(IntEnum):
    TURN_LEFT = 0
    TURN_RIGHT = 1
    MOVE_FORWARD = 2
    PICK_UP = 3
    OPEN = 4
    WAIT = 5


class Direction(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


# (row, col) offsets
DIR_DELTAS = {
    Direction.NORTH: (-1, 0),
    Direction.EAST: (0, 1),
    Direction.SOUTH: (1, 0),
    Direction.WEST: (0, -1),
}

DIR_ARROWS = {
    Direction.NORTH: "^",
    Direction.EAST: ">",
    Direction.SOUTH: "v",
    Direction.WEST: "<",
}
