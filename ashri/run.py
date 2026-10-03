"""Run the fixed-rule agent on a level.   python -m ashri.run levels/level_01.txt"""
from __future__ import annotations

import argparse
import time

from .agent_rules import RuleBasedAgent
from .world import GridWorld


def run_episode(world: GridWorld, agent: RuleBasedAgent, delay: float = 0.0,
                verbose: bool = True) -> dict:
    obs = world.reset()
    agent.reset()
    invalid = 0
    result = None
    if verbose:
        print(world.render(), "\n")
    while True:
        action = agent.act(obs)
        result = world.step(action)
        obs = result.obs
        invalid += result.info["invalid"]
        if verbose:
            print(f"step {obs.step_count:>3} | {agent.subgoal.value:<14} | "
                  f"{action.name:<12} {result.info['event']}")
            print(world.render(), "\n")
            if delay:
                time.sleep(delay)
        if result.done:
            break
    return {"success": result.success, "steps": obs.step_count, "invalid_actions": invalid}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("level")
    p.add_argument("--delay", type=float, default=0.0)
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()
    stats = run_episode(GridWorld.from_file(args.level), RuleBasedAgent(),
                        delay=args.delay, verbose=not args.quiet)
    print("RESULT:", stats)


if __name__ == "__main__":
    main()
