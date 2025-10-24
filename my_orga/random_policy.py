from typing import Any, List, Dict

from flatland.envs.RailEnvPolicy import RailEnvPolicy
from flatland.envs.rail_env_action import RailEnvActions
from flatland.utils.seeding import np_random


class RandomPolicy(RailEnvPolicy):
    """
    Random action with reset of random sequence to allow synchronization with partial trajectory.
    """

    def __init__(self, action_size: int = 5, seed=42, reset_at: int = None):
        """

        Parameters
        ----------
        reset_at : Optional[int] actions applied in env step reset_at+1 (e.g. reset at 7 to start at step 8)
        """
        super(RandomPolicy, self).__init__()
        self.action_size = action_size
        self._seed = seed
        self.reset_at = reset_at
        self.np_random, _ = np_random(seed=self._seed)

    def act_many(self, handles: List[int], observations: List[Any], **kwargs) -> Dict[int, RailEnvActions]:
        if self.reset_at is not None and observations[0] == self.reset_at:
            self.np_random, _ = np_random(seed=self._seed)
        return super().act_many(handles, observations)

    def act(self, observation: Any, **kwargs) -> RailEnvActions:
        return self.np_random.choice(self.action_size)