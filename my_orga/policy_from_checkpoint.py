from flatland.ml.ray.wrappers import ray_policy_wrapper_from_rllib_checkpoint


# TODO add example from checkpoint

def policy_from_checkpoint():
    # TODO can we do more elegantly?
    return ray_policy_wrapper_from_rllib_checkpoint("/home/conda/checkpoint_000199", "p0")
