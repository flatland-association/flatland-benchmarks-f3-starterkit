from flatland.ml.ray.wrappers import ray_policy_wrapper_from_rllib_checkpoint


def policy_from_checkpoint():
    return ray_policy_wrapper_from_rllib_checkpoint("checkpoint_000199", "p0")
