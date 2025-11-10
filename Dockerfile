# TODO use released version
# https://docs.docker.com/reference/build-checks/invalid-default-arg-in-from/
ARG TAG=entrypoint-refactoring
FROM ghcr.io/flatland-association/flatland-baselines:${TAG}

# HERE: ADD your code and checkpoints etc.
COPY my_orga/ my_orga/

# HERE: ADD your policy and obs builder (must be on PYTHONPATH)
ENV POLICY=my_orga.random_policy.RandomPolicy
ENV OBS_BUILDER=flatland.core.env_observation_builder.DummyObservationBuilder

# fail fast (verirfy at build time that POLICY and OBS_BUILDER are on PYTHONPATH)
RUN echo "from flatland.utils.cli_utils import resolve_type" > test.py && \
  echo "assert resolve_type('${POLICY}') is not None" >> test.py && \
  echo "assert resolve_type('${OBS_BUILDER}') is not None" >> test.py
RUN bash entrypoint_generic.sh python test.py


