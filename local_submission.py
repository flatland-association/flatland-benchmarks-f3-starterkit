import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator
from flatland.envs.line_generators import sparse_line_generator

import flatland.envs.observations
from flatland.utils.rendertools import RenderLocal
from matplotlib import pyplot as plt

import my_orga.policy.maze_policy.maze_xgboost_policy

AGENT = my_orga.policy.maze_policy.maze_xgboost_policy.MazeXGBoostPolicy
OBS_BUILDER = flatland.envs.observations.FullEnvObservation

N_AGENTS = 15
WIDTH = 35
HEIGHT = 35
N_CITIES = 2
MAX_RAILS_BETWEEN_CITIES = 2
MAX_RAIL_IN_CITY = 3
SEED = 42
MAX_STEPS = 200
RENDER = True
OUTPUT_DIR = Path(__file__).resolve().parent / "my_output"


def _prepare_output_dir(output_dir: Path) -> None:
    """Delete and recreate output directory.

    :param output_dir: Directory used for rendered frames and video output.
    """
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def _create_video_from_frames(output_dir: Path) -> None:
    """Create ``output.mp4`` from rendered PNG frames.

    :param output_dir: Directory containing ``render_%05d.png`` frames.
    """
    output_video = output_dir / "output.mp4"
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        "10",
        "-i",
        str(output_dir / "render_%05d.png"),
        "-vf",
        "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_video),
    ]
    print(f"✓ Creating video via ffmpeg: {' '.join(ffmpeg_cmd)}")
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"✓ Video written: {output_video}")
    except FileNotFoundError:
        print("✗ ffmpeg not found on PATH. Frames are available in my_output/ for manual conversion.")
    except subprocess.CalledProcessError as exc:
        print(f"✗ ffmpeg failed with return code {exc.returncode}.")


def run_local_submission():
    """Run a local Flatland episode for submission-policy debugging.

    The function creates a deterministic Flatland environment, runs the local
    policy until termination (or ``MAX_STEPS``), prints summary metrics and
    optionally renders frames and an ``mp4`` video.
    """
    print("=" * 60)
    print("Starting Local Submission Test")
    print("=" * 60)

    obs_builder = OBS_BUILDER()
    print(f"✓ Observation Builder: {obs_builder.__class__.__name__}")

    env = RailEnv(
        width=WIDTH,
        height=HEIGHT,
        rail_generator=sparse_rail_generator(
            max_num_cities=N_CITIES,
            seed=SEED,
            grid_mode=False,
            max_rails_between_cities=MAX_RAILS_BETWEEN_CITIES,
            max_rail_pairs_in_city=MAX_RAIL_IN_CITY,
        ),
        line_generator=sparse_line_generator(seed=SEED),
        number_of_agents=N_AGENTS,
        obs_builder_object=obs_builder,
        random_seed=SEED,
    )
    print(f"✓ Environment created: {N_AGENTS} agents, {WIDTH}x{HEIGHT} grid")

    agent = AGENT(action_size=5, seed=SEED)
    print(f"✓ Agent initialized: {agent.__class__.__name__}")

    if RENDER:
        _prepare_output_dir(OUTPUT_DIR)
        print(f"✓ Render output dir prepared: {OUTPUT_DIR}")

    obs, info = env.reset(regenerate_rail=True, regenerate_schedule=True)
    print(f"✓ Environment reset complete")
    print(f"  Number of agents: {env.get_num_agents()}")

    total_reward = 0
    steps = 0
    agents_done = {i: False for i in range(N_AGENTS)}
    agent_rewards = {i: 0 for i in range(N_AGENTS)}

    print("\n" + "=" * 60)
    print("Running Episode")
    print("=" * 60)

    renderer = RenderLocal(env)

    done = {"__all__": False}
    while not done["__all__"] and steps < MAX_STEPS:
        actions = agent.act_many(list(range(env.get_num_agents())), obs)

        obs, rewards, done, info = env.step(actions)

        for agent_id in range(env.get_num_agents()):
            if agent_id in rewards:
                agent_rewards[agent_id] += rewards[agent_id]
                total_reward += rewards[agent_id]
            if agent_id in done and done[agent_id]:
                agents_done[agent_id] = True

        steps += 1

        if steps % 10 == 0:
            n_done = sum(agents_done.values())
            print(f"Step {steps:3d}: {n_done}/{N_AGENTS} agents done, "
                  f"Total reward: {total_reward:.2f}")

        if RENDER:
            img = renderer.render_env(show=True, return_image=True, show_observations=False)
            fig, ax = plt.subplots()
            ax.imshow(img, aspect='auto', interpolation='nearest')
            ax.axis('off')
            fig.savefig(OUTPUT_DIR / f"render_{steps:05d}.png", bbox_inches="tight", pad_inches=0)
            plt.close(fig)

    if RENDER and steps > 0:
        _create_video_from_frames(OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("Episode Complete - Final Metrics")
    print("=" * 60)
    print(f"Total steps: {steps}")
    print(f"Total reward: {total_reward:.2f}")
    print(f"Average reward per agent: {total_reward / N_AGENTS:.2f}")
    print(f"Agents completed: {sum(agents_done.values())}/{N_AGENTS}")
    print(f"Completion rate: {sum(agents_done.values()) / N_AGENTS * 100:.1f}%")
    
    print("\nPer-agent rewards:")
    for agent_id, reward in agent_rewards.items():
        status = "✓ Done" if agents_done[agent_id] else "✗ Not done"
        print(f"  Agent {agent_id}: {reward:7.2f} [{status}]")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == '__main__':
    run_local_submission()
