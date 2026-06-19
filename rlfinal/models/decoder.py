import torch
import torch.nn as nn


class SSLEncoder(nn.Module):
    """Trainable encoder M -> 64 (bottleneck)."""

    def __init__(self, input_dim: int, bottleneck_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, bottleneck_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class SSLDecoder(nn.Module):
    """Decoder 64 -> M (reconstruct observation)."""

    def __init__(self, bottleneck_dim: int = 64, output_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(bottleneck_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class Autoencoder(nn.Module):
    """Full autoencoder: M -> 64 -> M."""

    def __init__(self, input_dim: int, bottleneck_dim: int = 64):
        super().__init__()
        self.encoder = SSLEncoder(input_dim, bottleneck_dim)
        self.decoder = SSLDecoder(bottleneck_dim, input_dim)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.encoder(x)
        recon = self.decoder(z)
        return z, recon

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)
