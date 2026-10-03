# ashri Roadmap

| Version | Goal | Status |
|---------|------|--------|
| **v0.1** | Navigate using fixed rules | current |
| v0.2 | Vision understands the environment (image -> object labels) | |
| v0.3 | Language instructions | |
| v0.4 | Agentic planning + tool/action loop | |
| v0.5 | Memory | |
| v0.6 | Vision-language -> action | |
| v0.7 | Evolutionary action policy | |
| v1.0 | Test on unseen procedurally generated environments | |

## Hooks v0.1 leaves for later versions
- `Observation` is the single interface between world and agent. v0.2 swaps its symbolic grid for a rendered image + a perception module that rebuilds the grid.
- `Subgoal` + `_update_subgoal` is a hard-coded planner. v0.3/v0.4 replace it with one driven by a parsed instruction.
- `StepResult.info["invalid"]` is already tracked - v0.7's fitness function (-5 per invalid action) needs it.
- `GridWorld(layout)` takes any text layout, so a procedural generator (v1.0) only has to emit strings.
