# TODO use released version
FROM ghcr.io/flatland-association/flatland-baselines:latest

# HERE: ADD your code and checkpoints etc.
COPY my_orga/ my_orga/

# TODO pull up to flatland-baselines image incl. ml
USER root
RUN apt-get update && apt-get install gcc build-essential wget zip ffmpeg -y
USER conda
RUN source /home/conda/.bashrc && \
    source activate base && \
    conda activate flatland-rl && \
    python -m pip install -U git+https://github.com/flatland-association/flatland-rl.git@main

# TODO get rid of entrypoint_generic in base image
# HERE: customize with your own policy and observation builder args
# N.B. further options like --data-dir will be added during evaluation, so make sure not to add conflicting options.
# TODO flatland-trajectory-generate-from-policy should not be part of the entrypoint, but the policy and observation args -> move to env var to separate?
ENTRYPOINT ["bash", "/home/conda/entrypoint_generic.sh", "flatland-trajectory-generate-from-policy", "--policy-pkg", "my_orga.random_policy", "--policy-cls", "RandomPolicy", "--obs-builder-pkg", "flatland.core.env_observation_builder", "--obs-builder-cls", "DummyObservationBuilder"]

# TODO add example from checkpoint