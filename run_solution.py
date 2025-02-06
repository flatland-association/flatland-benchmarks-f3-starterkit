from flatland.envs.rail_env import RailEnv
from flatland.evaluators.client import FlatlandRemoteClient

from src.observation.dummy_observation import FlatlandDummyObservation
from src.policy.deadlock_avoidance_policy import DeadLockAvoidancePolicy
from src.policy.random_policy import RandomPolicy
from src.utils.progress_bar import ProgressBar

remote_client = FlatlandRemoteClient()

# -------------------  user code  -------------------------
my_observation_builder = FlatlandDummyObservation()
flatlandSolver = DeadLockAvoidancePolicy()

use_random_policy = False
if use_random_policy:
    flatlandSolver = RandomPolicy()
# ---------------------------------------------------------

episode = 0

while True:
    print("/ start {}".format(flatlandSolver.get_name()), flush=True)
    episode += 1
    print("[INFO] EPISODE_START : {}".format(episode))
    # NO WAY TO CHECK service/self.evaluation_done in client

    observations, info = remote_client.env_create(obs_builder_object=my_observation_builder)
    if isinstance(observations, bool):
        if not observations:
            """
            The remote env returns False as the first obs
            when it is done evaluating all the individual episodes
            """
            print("[INFO] DONE ALL, BREAKING")
            break

    # -------------------  user code  -------------------------
    # init the policy
    env: RailEnv = remote_client.env
    flatlandSolver.reset(env)
    flatlandSolver.start_episode(False)
    # ---------------------------------------------------------

    pbar = ProgressBar()
    total_reward = 0
    nbr_done = 0
    while True:
        try:
            # -------------------  user code  -------------------------
            # call the policy to act
            flatlandSolver.start_step(False)
            # ---------------------------------------------------------

            # -------------------  user code  -------------------------
            actions = {}
            eps = 0
            for handle in env.get_agent_handles():
                # choose action for agent (handle)
                action = flatlandSolver.act(handle, observations[handle])
                actions.update({handle: action})
            # ---------------------------------------------------------

            observations, all_rewards, done, info = remote_client.env_step(actions)
            total_reward += sum(list(all_rewards.values()))
            if env._elapsed_steps < env._max_episode_steps:
                nbr_done = sum(list(done.values())[:-1])

            # -------------------  user code  -------------------------
            flatlandSolver.end_step(False)
            # ---------------------------------------------------------

        except:
            print("[ERR] DONE BUT step() CALLED")

        if (True):  # debug
            if done['__all__']:
                pbar.console_print(nbr_done, env.get_num_agents(), 'Nbr of done agents: {}'.format(len(done) - 1), '')

        # break
        if done['__all__']:
            print("[INFO] TOTAL_REW: ", total_reward)
            print("[INFO] EPISODE_DONE : ", episode)
            break

    # -------------------  user code  -------------------------
    # do clean up
    flatlandSolver.end_episode(False)
    # ---------------------------------------------------------

print("Evaluation Complete...")
print(remote_client.submit())
print("\\ end random_agent", flush=True)
