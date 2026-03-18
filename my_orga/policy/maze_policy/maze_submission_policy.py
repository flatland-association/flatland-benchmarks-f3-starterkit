"""Parent class bridging Flatland submission API to Maze observation/action plumbing."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import flatland
print(f'Flatland version: {flatland.__version__}')
from flatland.envs.RailEnvPolicy import RailEnvPolicy
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_env_action import RailEnvActions
from maze.core.utils.config_utils import make_env_from_hydra
from maze_flatland.env.maze_action import FlatlandMazeAction
from maze_flatland.env.maze_env import FlatlandEnvironment
from maze_flatland.env.maze_state import FlatlandMazeState
from maze_flatland.wrappers.masking_wrapper import FlatlandMaskingWrapper

logging.basicConfig(level=logging.INFO)


class MazeSubmissionPolicy(RailEnvPolicy, ABC):
    """Base policy mirroring ``RailEnv`` state into Maze for inference.

    Child policies only implement model-specific action inference while this
    base class handles env setup, state synchronization and observation
    conversion/masking.

    :param action_size: Flatland action-space size (compatibility only).
    :param seed: Optional external seed argument (compatibility only).
    :param reset_at: Optional reset marker (compatibility only).
    :param deterministic: Whether to request deterministic policy actions.
    :param config_module: Hydra config module for Maze env construction.
    :param config_name: Hydra root config name for Maze env construction.
    :param experiment: Maze experiment override to load env/wrapper setup.
    """

    def __init__(
        self,
        experiment: str,
        action_size: int = 5,
        seed: Optional[int] = None,
        reset_at: Optional[int] = None,
        deterministic: bool = True,
        config_module: str = "maze_flatland.conf",
        config_name: str = "conf_rollout",
    ):
        super().__init__()
        self.action_size = action_size
        self.seed = seed
        self.reset_at = reset_at
        self.deterministic = deterministic
        self.config_module = config_module
        self.config_name = config_name
        self.experiment = experiment

        self.maze_env = None
        self.base_maze_env: Optional[FlatlandEnvironment] = None
        self.masking_wrapper: Optional[FlatlandMaskingWrapper] = None

        self._last_modifying_actions: Dict[int, FlatlandMazeAction] = {}
        self._last_seen_num_resets: Optional[int] = None
        self._last_seen_elapsed_steps: Optional[int] = None
        self._n_agents = 0

        logging.info(f'Initialized policy "{self.__class__.__name__}" with experiment "{experiment}".')
        logging.info(f'Flatland version: {flatland.__version__}')

    @staticmethod
    def _unwrap_to_type(obj: Any, cls: type) -> Optional[Any]:
        """Traverse wrapper stack and return first object matching ``cls``.

        :param obj: Root object, potentially a wrapper stack.
        :param cls: Type to search for.
        :return: First matching object, otherwise ``None``.
        """
        cur = obj
        while cur is not None:
            if isinstance(cur, cls):
                return cur
            if not hasattr(cur, "env"):
                return None
            cur = cur.env
        return None

    def _setup_maze_env(self, rail_env: RailEnv) -> None:
        """Create Maze environment with dynamic shape/agent overrides.

        :param rail_env: Flatland backend env used for dimensions/agent count.
        """
        self.maze_env = make_env_from_hydra(
            self.config_module,
            self.config_name,
            **{
                "+experiment": self.experiment,
                "env._.n_trains": str(rail_env.number_of_agents),
                "env._.map_height": str(rail_env.height),
                "env._.map_width": str(rail_env.width),
            },
        )
        self.base_maze_env = self._unwrap_to_type(self.maze_env, FlatlandEnvironment)
        if self.base_maze_env is None:
            raise RuntimeError("Could not find FlatlandEnvironment in Maze wrapper stack.")
        self.masking_wrapper = self._unwrap_to_type(self.maze_env, FlatlandMaskingWrapper)

    def _reset_episode_state(self, rail_env: RailEnv) -> None:
        """Reset policy-side episode state tracking.

        :param rail_env: Current Flatland backend env.
        """
        self._n_agents = rail_env.number_of_agents
        self._last_modifying_actions = {
            i: FlatlandMazeAction.STOP_MOVING for i in range(self._n_agents)
        }
        if self.base_maze_env is not None:
            self.base_maze_env._reset_obs_conv()

    def _maybe_reset_episode_state(self, rail_env: RailEnv) -> None:
        """Detect new Flatland episode and reset cached policy state.

        :param rail_env: Current Flatland backend env.
        """
        num_resets = getattr(rail_env, "num_resets", None)
        elapsed_steps = getattr(rail_env, "_elapsed_steps", None)

        reset_detected = False
        if self._last_seen_num_resets is None:
            reset_detected = True
        elif num_resets is not None and num_resets != self._last_seen_num_resets:
            reset_detected = True
        elif elapsed_steps == 0 and self._last_seen_elapsed_steps not in (None, 0):
            reset_detected = True
        elif self._n_agents != rail_env.number_of_agents:
            reset_detected = True

        self._last_seen_num_resets = num_resets
        self._last_seen_elapsed_steps = elapsed_steps

        if reset_detected:
            self._reset_episode_state(rail_env)

    def _sync_maze_backend(self, rail_env: RailEnv) -> None:
        """Mirror Flatland backend references and Maze state before inference.

        :param rail_env: Current Flatland backend env.
        """
        assert self.base_maze_env is not None
        core = self.base_maze_env.core_env

        self.base_maze_env._reset_obs_conv()
        core._rail_env = rail_env
        core.n_trains = rail_env.number_of_agents
        core._current_train_id = 0
        core._actions = {}
        core._last_modifying_actions = dict(self._last_modifying_actions)

        if core._current_maze_state is None:
            core._current_maze_state = FlatlandMazeState(0, core._last_modifying_actions, rail_env)
        else:
            core._current_maze_state.reset_maze_state(0, core._last_modifying_actions, rail_env)

    def _set_current_train(self, train_id: int) -> None:
        """Set Maze sub-step context to a given train id.

        :param train_id: Train handle/sub-step id.
        """
        assert self.base_maze_env is not None
        core = self.base_maze_env.core_env
        maze_state = core._current_maze_state

        core._current_train_id = train_id
        if train_id == 0:
            maze_state.reset_maze_state(0, core._last_modifying_actions, core.rail_env)
            return

        maze_state.current_train_id = train_id
        maze_state.trains[train_id - 1].last_action = core._last_modifying_actions[train_id - 1]

    def _build_observation(self) -> Dict[str, Any]:
        """Build Maze observation (including mask if wrapper is present).

        :return: Observation dictionary in Maze policy input format.
        """
        assert self.base_maze_env is not None
        maze_state = self.base_maze_env.get_maze_state()
        observation = self.base_maze_env.observation_conversion.maze_to_space(maze_state)
        if self.masking_wrapper is not None:
            observation = self.masking_wrapper.observation(observation)
        return observation

    @abstractmethod
    def _compute_action_value(self, observation: Dict[str, Any], deterministic: bool) -> int:
        """Compute flatland-compatible action value for current actor.

        :param observation: Maze observation for current actor.
        :param deterministic: Determinism flag forwarded from policy config.
        :return: Integer action value in Flatland action encoding.
        """

    def act_many(self, handles: List[int], observations: List[Any], **kwargs) -> Dict[int, RailEnvActions]:
        """Compute actions for all requested handles.

        :param handles: Handles requested by Flatland runner.
        :param observations: Flatland observations (expects ``RailEnv`` values).
        :param kwargs: Forward-compatibility placeholder.
        :return: Mapping from handle to ``RailEnvActions``.
        """
        _ = kwargs
        if len(handles) == 0:
            return {}

        rail_env = observations[0]
        if not isinstance(rail_env, RailEnv):
            raise TypeError(f"Expected RailEnv observations, got {type(rail_env)}.")

        if self.maze_env is None:
            self._setup_maze_env(rail_env)
        elif self._n_agents not in (0, rail_env.number_of_agents):
            self._setup_maze_env(rail_env)

        self._maybe_reset_episode_state(rail_env)
        self._sync_maze_backend(rail_env)

        requested_handles = set(handles)
        actions: Dict[int, RailEnvActions] = {}

        for train_id in range(rail_env.number_of_agents):
            self._set_current_train(train_id)
            observation = self._build_observation()
            action_value = self._compute_action_value(observation, deterministic=self.deterministic)

            if action_value != FlatlandMazeAction.DO_NOTHING.value:
                self._last_modifying_actions[train_id] = FlatlandMazeAction(action_value)
                self.base_maze_env.core_env._last_modifying_actions[train_id] = self._last_modifying_actions[train_id]

            if train_id in requested_handles:
                actions[train_id] = RailEnvActions(action_value)

        return actions

    def act(self, observation: Any, **kwargs) -> RailEnvActions:
        """Single-agent fallback required by base policy interface.

        :param observation: Unused.
        :param kwargs: Unused.
        :return: ``DO_NOTHING`` action.
        """
        _ = observation, kwargs
        return RailEnvActions.DO_NOTHING
