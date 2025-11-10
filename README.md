# Flatland Benchmarks Flatland 3 starterkit

This repo is a starterkit for participating in the Flatland 3 Benchmarks hosted at [fab.flatland.cloud](https://fab.flatland.cloud).

[Flatland Benchmarks](https://github.com/flatland-association/flatland-benchmarks) (FAB) is an open-source web-based platform for running Benchmarks to foster
Open Research.

Flatland 3 Benchmarks follow up on the [Flatland 3 Challenge](https://flatland-association.github.io/flatland-book/challenges/flatland3.html).
More precisely, Flatland 3 Benchmarks follow Flatland 3 Challenge's
[Round 2 Environment Configurations](https://flatland-association.github.io/flatland-book/challenges/flatland3/envconfig.html#round-2), having the same
environment configuration but generated with different seeds.

This starterkit features a random agent [random_agent.py](random_agent.py)

## TL;DR; aka. First Submission

1. Fork this repo and code. See [existing forks](https://github.com/flatland-association/flatland-benchmarks-f3-starterkit/forks) for illustration.
2. Manually trigger gh action `docker`  under `https://github.com/<user/orga>/<forked repo name>/actions/`
3. Copy the docker image URL from `https://github.com/<user/orga>/<forked repo name>/pkgs/container/<forked repo name>`
4. Go to https://fab.flatland.cloud and enter the docker image URL when creating a submission.

![Workflow.drawio.png](docs/Workflow.drawio.png)

See [STEP-BY-STEP_GUIDE](STEP-BY-STEP_GUIDE.md) contributed by  <a href="https://github.com/aiAdrian" target="_blank">aiAdrian</a> :partying_face:

## Local Testing

Single episode:

```bash
docker build  -t myorga/mysolution .
docker run -v ./data/:/tmp myorga/mysolution --data-dir /tmp --callbacks-pkg flatland.callbacks.generate_movie_callbacks --callbacks-cls GenerateMovieCallbacks
find ./data
```

Test set from metadata:

```bash
docker run -v ./debug-environments/:/inputs -v ./outputs:/outputs --entrypoint bash myorga/mysolution /home/conda/entrypoint_generic.sh flatland-trajectory-generate-from-metadata --metadata-csv /inputs/metadata.csv --data-dir /outputs
```

Get report

```shell
flatland-trajectory-analysis --root-data-dir outputs --output-dir analysis
```

### Further CLI options

See the options for number of agents, grid size etc.:

```bash
conda env update -f environment.yml
conda activate flatland-baselines
flatland-trajectory-generate-from-policy --help
flatland-trajectory-generate-from-metadata --help
```

## Further Information

See [FAB User Guide](https://github.com/flatland-association/flatland-benchmarks/blob/main/docs/USER_GUIDE.md).