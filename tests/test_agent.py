from pathlib import Path
import pytest

from ashri.agent_rules import RuleBasedAgent
from ashri.run import run_episode
from ashri.world import GridWorld

LEVELS = sorted((Path(__file__).parent.parent / "levels").glob("level_*.txt"))


@pytest.mark.parametrize("level", LEVELS, ids=lambda p: p.name)
def test_agent_solves_level_with_no_invalid_actions(level):
    stats = run_episode(GridWorld.from_file(level), RuleBasedAgent(), verbose=False)
    assert stats["success"]
    assert stats["invalid_actions"] == 0
