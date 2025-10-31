from pathlib import Path

from flatland.env_generation.env_generator import env_generator
from flatland.envs.predictions import ShortestPathPredictorForRailEnv
from flatland.ml.observations.flatten_tree_observation_for_rail_env import FlattenedNormalizedTreeObsForRailEnv
from flatland.ml.ray.wrappers import ray_policy_wrapper_from_rllib_checkpoint
from flatland.trajectories.policy_runner import PolicyRunner


def policy_from_checkpoint():
    # TGDO can we do more elegantly?
    return ray_policy_wrapper_from_rllib_checkpoint("/home/conda/checkpoint_000199", "p0")


# TODO make test instead
if __name__ == '__main__':
    # TODO do it rllib way with .evaluation instead?
    PolicyRunner.create_from_policy(
        policy=ray_policy_wrapper_from_rllib_checkpoint("/Users/che/workspaces/flatland-benchmarks-f3-starterkit/checkpoint_000199", "p0"),
        data_dir=Path("./outputs"),
        # snapshot_interval=snapshot_interval,
        ep_id="first",
        # TODO how to pass obs builder
        env=env_generator(obs_builder_object=FlattenedNormalizedTreeObsForRailEnv(max_depth=2, predictor=ShortestPathPredictorForRailEnv(max_depth=50)))[0],
        # callbacks=callbacks,
    )
