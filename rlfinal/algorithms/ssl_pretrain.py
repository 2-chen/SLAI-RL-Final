import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from rlfinal.models.decoder import Autoencoder
from rlfinal.utils.config import SSLConfig


def train_ssl(
    autoencoder: Autoencoder,
    train_data: torch.Tensor,
    config: SSLConfig,
    device: str = "cuda",
    verbose: bool = True,
) -> dict:
    """Train autoencoder on pre-collected observations. Returns training metrics."""
    autoencoder = autoencoder.to(device)
    optimizer = torch.optim.Adam(autoencoder.parameters(), lr=config.lr)
    criterion = nn.MSELoss()

    dataset = TensorDataset(train_data, train_data)
    loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)

    losses = []
    for epoch in range(config.epochs):
        epoch_loss = 0.0
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            _, recon = autoencoder(batch_x)
            loss = criterion(recon, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * batch_x.size(0)

        avg_loss = epoch_loss / len(train_data)
        losses.append(avg_loss)

        if verbose and (epoch + 1) % 500 == 0:
            print(f"  SSL epoch {epoch + 1}/{config.epochs}, loss={avg_loss:.6f}")

    final_loss = losses[-1]
    if verbose:
        print(f"  SSL training done, final loss={final_loss:.6f}")

    return {"ssl_train_loss": losses, "ssl_final_loss": final_loss}
