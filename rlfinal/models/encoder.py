import torch
import torch.nn as nn


class RandomEncoder(nn.Module):
    """Frozen random projection 64 -> M (pure linear, no activation)."""

    def __init__(self, input_dim: int = 64, output_dim: int = 128, seed: int = 0):
        super().__init__()
        torch.manual_seed(seed)
        self.linear = nn.Linear(input_dim, output_dim)
        # Freeze immediately
        for p in self.parameters():
            p.requires_grad_(False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)


class IdentityEncoder(nn.Module):
    """Identity passthrough for the baseline."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x
