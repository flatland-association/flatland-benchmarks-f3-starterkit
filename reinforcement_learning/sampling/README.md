# Random Sampling for Competition Training

Use `sampling_env_generator` to generate new lines and timetables on the [competition grid](../COMPETITION-TOPOLOGY-DESCRIPTION.md). 

You can specify the maximum line length (`line_length`) as well as the region on the [map](../COMPETITION-TOPOLOGY-DESCRIPTION.md) (`scene`). 

Example: 
```
from flatland.envs.persistence import RailEnvPersister
from flatland.envs.rewards import ECML2026Rewards
from sampling_env_generator import sampling_env_generator

env = RailEnvPersister.load_new(("level_0_scenario_1.pkl"), obs_builder=obs_builder,
                                rewards=ECML2026Rewards())[0]

sampled_env = sampling_env_generator(env, line_length=3, scene="scene_1")

obs, info = sampled_env.reset()
```

