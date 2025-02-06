from flatland.envs.rail_env import RailEnv
from flatland.evaluators.client import FlatlandRemoteClient

from src.observation.dummy_observation import FlatlandDummyObservation
from src.policy.deadlock_avoidance_policy import \
    DeadLockAvoidancePolicy

remote_client = FlatlandRemoteClient()

my_observation_builder = FlatlandDummyObservation()

episode = 0

while True:
    print("/ start random_agent", flush=True)
    print("==============")
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
    flatlandSolver = DeadLockAvoidancePolicy(env)
    flatlandSolver.start_episode(False)
    # ---------------------------------------------------------

    while True:
        try:
            # -------------------  user code  -------------------------
            # call the policy to act
            flatlandSolver.start_step(False)
            actions = {}
            eps = 0
            print(observations)
            for handle in env.get_agent_handles():
                # choose action for agent (handle)
                action = flatlandSolver.act(handle, observations[handle])
                actions.update({handle: action})
            flatlandSolver.end_step(False)
            # ---------------------------------------------------------

            observations, all_rewards, done, info = remote_client.env_step(actions)
        except:
            print("[ERR] DONE BUT step() CALLED")

        if (True):  # debug
            print("-----")
            # print(done)
            print("[DEBUG] REW: ", all_rewards)

        # break
        if done['__all__']:
            print("[INFO] EPISODE_DONE : ", episode)
            print("[INFO] TOTAL_REW: ", sum(list(all_rewards.values())))
            break

    # -------------------  user code  -------------------------
    # do clean up
    flatlandSolver.end_episode(False)
    # ---------------------------------------------------------

print("Evaluation Complete...")
print(remote_client.submit())
print("\\ end random_agent", flush=True)
