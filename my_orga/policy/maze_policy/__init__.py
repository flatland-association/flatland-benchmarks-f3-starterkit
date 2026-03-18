"""Maze-based submission policies."""

from my_orga.policy.maze_policy.maze_submission_policy import MazeSubmissionPolicy
from my_orga.policy.maze_policy.maze_xgboost_policy import MazeXGBoostPolicy

__all__ = ["MazeSubmissionPolicy", "MazeXGBoostPolicy"]
