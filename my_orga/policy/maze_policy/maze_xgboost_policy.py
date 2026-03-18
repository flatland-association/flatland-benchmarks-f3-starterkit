"""Maze XGBoost submission policy implementation."""

from __future__ import annotations

import os
from typing import Any, Dict

from maze_flatland.agents.xgboost_policy import XGBoostPolicy as MazeFlatlandXGBoostPolicy

from my_orga.policy.maze_policy.maze_submission_policy import MazeSubmissionPolicy


class MazeXGBoostPolicy(MazeSubmissionPolicy):
    """Submission policy using Maze-Flatland XGBoost model inference.


    :param args: Positional arguments forwarded to ``MazeSubmissionPolicy``.
    :param kwargs: Keyword arguments forwarded to ``MazeSubmissionPolicy``.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, experiment="multi_train/rollout/xgboost", **kwargs)
        self.maze_policy = self._load_maze_policy()

    @staticmethod
    def _load_maze_policy() -> MazeFlatlandXGBoostPolicy:
        """Load Maze XGBoost model from current policy directory.

        :return: Instantiated Maze XGBoost policy.
        """
        policy_dir = os.path.dirname(os.path.abspath(__file__))
        cwd = os.getcwd()
        try:
            os.chdir(policy_dir)
            return MazeFlatlandXGBoostPolicy(use_masking=False)
        finally:
            os.chdir(cwd)

    def _compute_action_value(self, observation: Dict[str, Any], deterministic: bool) -> int:
        """Compute action with Maze XGBoost policy.

        :param observation: Maze observation for current actor.
        :param deterministic: Whether deterministic action selection is requested.
        :return: Integer Flatland action value.
        """
        maze_state = self.base_maze_env.get_maze_state()
        maze_action = self.maze_policy.compute_action(
            observation=observation,
            maze_state=maze_state,
            actor_id=self.base_maze_env.actor_id(),
            env=self.base_maze_env,
            deterministic=deterministic,
        )
        if isinstance(maze_action, dict):
            return int(maze_action["train_move"])
        return int(maze_action)
