from flatland.core.env_observation_builder import ObservationBuilder, AgentHandle, ObservationType
from flatland.envs.rail_env import RailEnv


class FullEnvObservation(ObservationBuilder[RailEnv]):
    """
    Returns full env as observation.
    """
    def __init__(self):
        pass

    def get(self, handle: AgentHandle = 0) -> ObservationType:
        return self.env

    def reset(self):
        pass

    def set_env(self,env):
        print("set_env")
        self.env = env
