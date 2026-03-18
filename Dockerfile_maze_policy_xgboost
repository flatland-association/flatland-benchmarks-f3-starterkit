# https://docs.docker.com/reference/build-checks/invalid-default-arg-in-from/
ARG TAG=pin-4.2.3
FROM ghcr.io/flatland-association/flatland-baselines:${TAG}

# HERE: ADD your code and checkpoints etc.
COPY my_orga/ my_orga/

RUN conda env list
RUN /bin/bash -c "source activate /opt/conda/envs/flatland-baselines && pip install git+https://github.com/enlite-ai/maze.git@dev && pip install git+https://github.com/enlite-ai/maze-flatland.git@main && pip install xgboost && pip install scikit-learn && pip list"

#RUN pip install maze-rl
#RUN pip install git+https://github.com/enlite-ai/maze-flatland.git@main
#
#RUN /bin/bash -c "pip list"

# HERE: ADD your policy and obs builder (must be on PYTHONPATH)
ENV POLICY=my_orga.policy.maze_policy.maze_xgboost_policy.MazeXGBoostPolicy
ENV OBS_BUILDER=flatland.envs.observations.FullEnvObservation
