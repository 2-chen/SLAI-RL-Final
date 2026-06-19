import torch
import torch.nn as nn


class QNetwork(nn.Module):
    """DQN: input_dim -> 256 -> 256 -> n_actions."""

    def __init__(self, input_dim: int, n_actions: int = 4, hidden_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_actions),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
