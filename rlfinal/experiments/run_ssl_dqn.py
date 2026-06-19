import json
import os
import time

import torch
import numpy as np

from rlfinal.env.gridworld import GridWorld
from rlfinal.models.encoder import RandomEncoder
from rlfinal.models.decoder import Autoencoder
from rlfinal.models.q_network import QNetwork
from rlfinal.algorithms.ssl_pretrain import train_ssl
from rlfinal.algorithms.dqn import train_dqn
from rlfinal.utils.config import SSLConfig, DQNConfig
from rlfinal.utils.seed import set_seed


def _build_lookup(encodings: np.ndarray) -> callable:
    """Return a preprocess function that does O(1) lookup."""
    def preprocess(obs_np: np.ndarray) -> np.ndarray:
        idx = int(np.argmax(obs_np))
        return encodings[idx].copy()
    return preprocess


def run_ssl_dqn(M: int, seed: int, device: str, results_dir: str) -> dict:
    """Pipeline 1: SSL pretrain -> DQN with SSL encoder output (64-dim)."""
    set_seed(seed)
    run_name = f"ssl_dqn_M{M}_seed{seed}"
    print(f"\n{'='*60}")
    print(f"[SSL→DQN] M={M}, seed={seed}")
    print(f"{'='*60}")

    env = GridWorld()

    # 1. Random encoder: 64 -> M (frozen)
    rand_enc = RandomEncoder(64, M, seed=seed).to(device)

    # 2. Collect SSL training data: enumerate all 64 states
    all_states = env.all_states  # (64, 64) one-hot
    all_states_t = torch.FloatTensor(all_states).to(device)
    with torch.no_grad():
        all_obs = rand_enc(all_states_t).cpu().numpy()
    train_data = torch.FloatTensor(all_obs)

    # 3. Train autoencoder: M -> 64 -> M
    print("  Training SSL autoencoder...")
    autoencoder = Autoencoder(M, 64)
    ssl_metrics = train_ssl(autoencoder, train_data, SSLConfig(), device, verbose=True)

    # Freeze SSL encoder
    for p in autoencoder.encoder.parameters():
        p.requires_grad_(False)
    autoencoder.encoder.eval()

    # 4. Precompute encodings for all 64 states (one-time GPU batch)
    with torch.no_grad():
        all_projected = rand_enc(all_states_t)
        all_latents = autoencoder.encode(all_projected).cpu().numpy()
    # (64, 64) - precomputed latent encodings

    preprocess = _build_lookup(all_latents)

    # 5. Train DQN (input dim = 64)
    dqn_config = DQNConfig()
    q_net = QNetwork(64, 4, dqn_config.hidden_dim)
    dqn_metrics = train_dqn(env, q_net, dqn_config, device, seed, preprocess, verbose=True)

    results = {**ssl_metrics, **dqn_metrics, "M": M, "pipeline": "ssl_dqn", "seed": seed}
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, f"{run_name}.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results


def run_random_dqn(M: int, seed: int, device: str, results_dir: str) -> dict:
    """Pipeline 2: DQN directly on M-dim random projection (no SSL)."""
    set_seed(seed)
    run_name = f"random_dqn_M{M}_seed{seed}"
    print(f"\n{'='*60}")
    print(f"[DQN-only] M={M}, seed={seed}")
    print(f"{'='*60}")

    env = GridWorld()
    rand_enc = RandomEncoder(64, M, seed=seed).to(device)

    # Precompute projected observations for all 64 states (one-time GPU batch)
    all_states_t = torch.FloatTensor(env.all_states).to(device)
    with torch.no_grad():
        all_projected = rand_enc(all_states_t).cpu().numpy()
    # (64, M) - each row is the M-dim observation for that state

    preprocess = _build_lookup(all_projected)

    dqn_config = DQNConfig()
    q_net = QNetwork(M, 4, dqn_config.hidden_dim)
    dqn_metrics = train_dqn(env, q_net, dqn_config, device, seed, preprocess, verbose=True)

    results = {**dqn_metrics, "M": M, "pipeline": "random_dqn", "seed": seed}
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, f"{run_name}.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results


def run_compress_dqn(seed: int, device: str, results_dir: str, bottleneck_dim: int = 16) -> dict:
    """Pipeline 3: Train autoencoder 64→D→64 on one-hot states, then DQN on D-dim bottleneck."""
    set_seed(seed)
    run_name = f"compress_dqn_d{bottleneck_dim}_seed{seed}"
    print(f"\n{'='*60}")
    print(f"[Compress→DQN] dim={bottleneck_dim}, seed={seed}")
    print(f"{'='*60}")

    env = GridWorld()

    # 1. Collect all 64 one-hot states
    all_states = env.all_states  # (64, 64) one-hot
    train_data = torch.FloatTensor(all_states)

    # 2. Train autoencoder: 64 → D → 64
    print(f"  Training compress autoencoder (64→{bottleneck_dim}→64)...")
    autoencoder = Autoencoder(64, bottleneck_dim)
    ssl_metrics = train_ssl(autoencoder, train_data, SSLConfig(), device, verbose=True)

    # Freeze encoder
    for p in autoencoder.encoder.parameters():
        p.requires_grad_(False)
    autoencoder.encoder.eval()

    # 3. Precompute D-dim encodings for all 64 states
    all_states_t = torch.FloatTensor(all_states).to(device)
    with torch.no_grad():
        all_latents = autoencoder.encode(all_states_t).cpu().numpy()
    # (64, D) - precomputed latent encodings

    preprocess = _build_lookup(all_latents)

    # 4. Train DQN (input dim = bottleneck_dim)
    dqn_config = DQNConfig()
    q_net = QNetwork(bottleneck_dim, 4, dqn_config.hidden_dim)
    dqn_metrics = train_dqn(env, q_net, dqn_config, device, seed, preprocess, verbose=True)

    results = {**ssl_metrics, **dqn_metrics, "M": bottleneck_dim, "pipeline": "compress_dqn", "seed": seed}
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, f"{run_name}.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results


def run_identity(seed: int, device: str, results_dir: str) -> dict:
    """Baseline: DQN directly on 64-dim one-hot state."""
    set_seed(seed)
    run_name = f"identity_seed{seed}"
    print(f"\n{'='*60}")
    print(f"[Identity] seed={seed}")
    print(f"{'='*60}")

    env = GridWorld()
    dqn_config = DQNConfig()
    q_net = QNetwork(64, 4, dqn_config.hidden_dim)
    dqn_metrics = train_dqn(env, q_net, dqn_config, device, seed, preprocess_fn=None, verbose=True)

    results = {**dqn_metrics, "M": 64, "pipeline": "identity", "seed": seed}
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, f"{run_name}.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results
