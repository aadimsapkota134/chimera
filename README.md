# Project Chimera

### Autonomous System for Holistic Reasoning, Interaction, Knowledge, and Action

> A progressive learning project exploring how an agent can **see**, **plan**, **act**, and eventually **evolve** — all inside a tiny procedurally generated world.

---

## What is this?

I'm building an autonomous agent that lives inside a small 2D grid world. The world has walls, keys, doors, and a charging station. The agent's job is simple: **find the key, open the door, and reach the charger**.

What makes this interesting is *how* the system does it. Right now it uses hand-written rules and a pathfinding algorithm. But the long-term goal is to layer in vision, language understanding, agentic planning, memory, and eventually an evolutionary training loop — piece by piece, without throwing away the work from any previous step.

The inspiration comes from neuroevolution research — the idea that a controller can improve through selection and mutation, not just gradient descent. Instead of a self-driving car, I wanted something more general: a little explorer in a game-like world that needs to reason, navigate, and adapt.

---

## What's implemented right now

This is the very first working piece. I built the full **observe → act → new observation** loop and proved it works reliably before adding any AI on top of it.

Specifically, I did:

- A **grid world simulator** that handles walls, a key, a locked door, and a charging station
- A **rule-based agent** that uses BFS pathfinding and a simple subgoal state machine
- A set of **hand-crafted levels** to test the agent against
- A **test suite** that verifies the agent solves every level with zero invalid actions

No vision. No language. No learning. Just a clean, deterministic loop that works — and that every future layer will build on top of.

---

## How the world works

The environment is a text grid. Each character in the file is one tile:

| Symbol | Meaning |
|--------|---------|
| `#` | Wall — blocks all movement |
| `.` or space | Floor — walkable |
| `A` | Agent starting position (always faces East at the start) |
| `K` | Key — must be picked up before the door can be opened |
| `D` | Locked door — opens when the agent faces it and uses `OPEN` while holding the key |
| `O` | Open door — walkable after the door has been unlocked |
| `C` | Charging station — reaching this tile ends the episode as a success |

A simple level looks like this:

```
##########
#A   K   #
#  ###   #
#        #
####D#####
#       C#
##########
```

The agent starts at `A`, finds the key `K`, navigates through the door `D`, and reaches the charger `C`.

---

## How the agent works

The agent has six possible actions:

| Action | What it does |
|--------|-------------|
| `TURN_LEFT` | Rotates the agent 90° counter-clockwise |
| `TURN_RIGHT` | Rotates the agent 90° clockwise |
| `MOVE_FORWARD` | Moves one tile in the direction the agent is currently facing |
| `PICK_UP` | Picks up whatever is on the tile the agent is facing |
| `OPEN` | Opens the door on the tile the agent is facing (requires the key) |
| `WAIT` | Does nothing — used when the agent is blocked or has no valid move |

`PICK_UP` and `OPEN` both act on the tile *directly in front of* the agent, not the tile the agent is standing on.

The agent follows three fixed rules, in order:

1. **No key yet** → use BFS to find a walkable tile next to the key, face the key, then `PICK_UP`
2. **Have key, door still locked** → use BFS to find a walkable tile next to the door, face the door, then `OPEN`
3. **Door is open** → walk straight to the charging station

Each of these is a *subgoal*. The agent updates its current subgoal every step based on what it observes, then executes the right movement primitive. There is no learning involved at this stage — the rules are entirely hand-written.

---

## Project structure

```
ashri/
├── ashri/
│   ├── __init__.py        # package entry point
│   ├── actions.py         # Action and Direction enums, movement deltas
│   ├── world.py           # GridWorld simulator + Observation + StepResult
│   ├── agent_rules.py     # RuleBasedAgent — the fixed-rule controller
│   ├── pathfinding.py     # BFS shortest-path implementation
│   └── run.py             # CLI entry point: run a single episode
├── levels/
│   ├── level_01.txt       # simple open room
│   ├── level_02.txt       # multi-room with winding path
│   ├── level_03.txt       # larger maze layout
│   └── level_04.txt       # custom layout
├── tests/
│   ├── test_world.py      # unit tests for the simulator mechanics
│   └── test_agent.py      # parametrised test: agent must solve every level file
│   
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting started

### Prerequisites

- **Python 3.10 or newer** (the code uses `X | Y` union type hints)
- `git` installed on your machine

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/aadimsapkota134/chimera.git
cd ashri
```

---

### Step 2 — Create a virtual environment

It is strongly recommended to keep dependencies isolated.

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` appear at the start of your terminal prompt once the environment is active.

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This only installs `pytest` for now. There are no heavy ML dependencies at this stage — the system is pure Python.

---

### Step 4 — Run the agent

All run commands are executed from inside the `ashri/` subdirectory (the one that contains `levels/`):

```bash
cd ashri
```

**Run on level 1 and watch it step by step (0.2 second delay between steps):**
```bash
python -m ashri.run levels/level_01.txt --delay 0.2
```

**Run on level 2 silently (no step-by-step output):**
```bash
python -m ashri.run levels/level_02.txt --quiet
```

**Run on level 3 with a short delay:**
```bash
python -m ashri.run levels/level_03.txt --delay 0.1
```

Each step prints the current subgoal, the action taken, any event that happened (e.g. `picked up key`, `opened door`, `blocked`), and a fresh render of the grid.

**Example output:**

```
##########
#>   K   #
#  ###   #
#        #
####D#####
#       C#
##########

step   1 | get_key       | MOVE_FORWARD
step   2 | get_key       | MOVE_FORWARD
...
step  12 | get_key       | PICK_UP      picked up key
...
step  20 | open_door     | OPEN         opened door
...
step  35 | go_to_charger | MOVE_FORWARD
RESULT: {'success': True, 'steps': 35, 'invalid_actions': 0}
```

The arrow (`>`, `^`, `v`, `<`) shows the agent's current facing direction.

---

### Step 5 — Run the tests

From inside the `ashri/` directory:

```bash
pytest
```

The test suite does two things:

1. **`test_world.py`** — unit tests for the simulator: confirms that walls block movement, keys must be picked up before the door works, reaching the charger ends the episode, and turning wraps correctly
2. **`test_agent.py`** — parametrised test that runs the agent on every `level_*.txt` file in `levels/` and asserts `success=True` and `invalid_actions=0`

All tests should pass with no warnings.

---

## Adding your own level

Drop a new file named `level_05.txt` (or any `level_*.txt`) into `levels/` using the tile symbols above:

```
###########
#A        #
#   K     #
#    D    #
#    C    #
###########
```

**Three hard rules:**
- Every row must be the **same width** — use `#` to pad rows that are too short
- There must be exactly **one** each of `A`, `K`, `D`, and `C`
- The key, door, and charger must all be reachable from the agent's starting position

The test suite picks up every `level_*.txt` file automatically. Running `pytest` after adding a level tells you immediately whether the agent can solve it.

**If your rows are uneven**, use the `fix_level.py` utility. It lives one directory above the repo root (in `project_ashrika/`), not inside the repo itself:

```python
# edit this line inside fix_level.py first:
path = Path("ashri/levels/level_05.txt")
```

Then run it from the `project_ashrika/` directory (the parent of the repo):

```bash
python fix_level.py
```

It pads every row to the width of the longest row using `#`.

---

## What's coming

Right now the system navigates entirely by fixed hand-written rules. It has no sense of vision, no understanding of language, and no ability to learn from experience.

Upcoming updates will eventually bring things like:

- a **perception layer** where the system looks at a rendered image of the environment and identifies objects rather than reading raw tile symbols
- **natural language instructions** — so you can tell the system *"find the key and open the door"* instead of hard-coding the goal
- a proper **agentic planning loop** where the system breaks a high-level goal into subgoals and updates its plan as it observes the results of its actions
- **short-term memory** so the system remembers what it found in a previous room and doesn't have to re-explore
- a **vision-language action model** that takes a rendered image and a text instruction as input and outputs an action
- an **evolutionary training component** that scores agents by task performance, keeps the better ones, mutates their parameters, and repeats — no gradient descent involved

The architecture is already designed to make these additions clean. The `Observation` dataclass is the single interface between the world and the agent, so plugging in a perception module later only changes what that object contains. The subgoal logic is already separated from movement, which makes replacing the planner straightforward.

---

## The bigger picture

The long-term question this project is trying to answer is:

> **Can a relatively small vision-language agent learn to adapt its actions to new environments, rather than memorising a particular layout?**

This connects directly to the generalisation problem in reinforcement learning and neuroevolution. A model that only memorises training environments is useless in the real world. The evolutionary component will eventually let us test this properly: train on one set of procedurally generated levels, evaluate on completely unseen ones, and measure whether the system generalises.

For now, step one is done. The loop works. The agent is reliable. Everything else builds on top of this.

---

## Tech stack

| Layer | What I'm using |
|-------|----------------|
| Language | Python 3.10+ |
| Simulator | Pure Python (zero external dependencies) |
| Pathfinding | BFS — hand-written in `pathfinding.py` |
| Testing | `pytest >= 7` |
| Future: vision | PyTorch + a pretrained vision-language model |
| Future: visual simulator | Pygame or a rendered grid-world library |
| Future: planning | LLM-based planner |
| Future: evolution | Custom evolutionary loop over action policy weights |

---

## License

MIT — do whatever you want with it.

---

*Built as a learning project to understand Vision-Language-Action systems, agentic AI, and neuroevolution from the ground up.*

