# TODO use released version
# https://docs.docker.com/reference/build-checks/invalid-default-arg-in-from/
ARG TAG=latest
FROM ghcr.io/flatland-association/flatland-baselines:${TAG}


COPY my_orga/ my_orga/

ENV POLICY=my_orga.my_policy.MyPolicy
ENV OBS_BUILDER=my_orga.my_observation_builder.MyObservationBuilder

RUN python -m pip install -U -r my_orga/requirements.txt