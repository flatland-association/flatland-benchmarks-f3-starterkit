import os
import torch
import torch.nn as nn
import numpy as np
from typing import Any, Tuple, List, Dict

from flatland.envs.rail_env_action import RailEnvActions


class ActorCritic(nn.Module):
    def __init__(
        self,
        obs_size: int = 36,
        n_actions: int = 5,
        hidden_size: int = 128,
        num_hidden_layers: int = 3,
        checkpoint_path: str | None = "./my_orga/checkpoint.pt",
    ):
        super().__init__()
        self.obs_size = obs_size
        self.n_actions = n_actions
        layers: list[nn.Module] = [nn.Linear(obs_size, hidden_size), nn.Tanh()]
        for _ in range(num_hidden_layers - 1):
            layers += [nn.Linear(hidden_size, hidden_size), nn.Tanh()]
        self.trunk = nn.Sequential(*layers)
        self.policy_head = nn.Linear(hidden_size, n_actions)
        self.value_head = nn.Linear(hidden_size, 1)

        if checkpoint_path is not None and os.path.exists(checkpoint_path):
            ckpt = torch.load(checkpoint_path, weights_only=False, map_location="cpu")
            self.load_state_dict(ckpt["model"])
            self.eval()
        else:
            """Orthogonal init for an ActorCritic-style net with trunk + policy/value heads."""
            for module in self.trunk:
                if isinstance(module, nn.Linear):
                    nn.init.orthogonal_(module.weight, gain=np.sqrt(2))
                    nn.init.zeros_(module.bias)
            nn.init.orthogonal_(self.policy_head.weight, gain=0.01)
            nn.init.zeros_(self.policy_head.bias)
            nn.init.orthogonal_(self.value_head.weight, gain=1.0)
            nn.init.zeros_(self.value_head.bias)

    def forward(self, obs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.trunk(obs)
        return self.policy_head(features), self.value_head(features).squeeze(-1)

    def act_many(
        self, handles: List[int], observations: List[Any], **kwargs
    ) -> Dict[int, RailEnvActions]:
        return {
            handle: self.act(obs, **kwargs)
            for handle, obs in zip(handles, observations)
        }

    def act(self, observation: Any, **kwargs) -> RailEnvActions:
        obs_t = torch.from_numpy(observation)
        features = obs_t[: self.obs_size]
        mask = obs_t[self.obs_size : self.obs_size + self.n_actions]
        logits, _ = self(features)
        logits = logits.masked_fill(mask < 0.5, float("-inf"))
        return logits.argmax(dim=-1).item()


MyPolicy = ActorCritic
