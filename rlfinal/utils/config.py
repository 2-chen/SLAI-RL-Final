from dataclasses import dataclass, field


@dataclass
class SSLConfig:
    lr: float = 1e-3
    epochs: int = 500
    batch_size: int = 64


@dataclass
class DQNConfig:
    lr: float = 1e-3
    gamma: float = 0.99
    batch_size: int = 64
    replay_capacity: int = 10000
    eps_start: float = 1.0
    eps_end: float = 0.05
    eps_decay_frac: float = 0.2
    target_update_freq: int = 100
    hidden_dim: int = 256
    total_episodes: int = 5000
    max_steps_per_episode: int = 64
    eval_freq: int = 50
    eval_episodes: int = 10


@dataclass
class ExperimentConfig:
    M: int = 128
    pipeline: str = "ssl_dqn"  # "ssl_dqn", "random_dqn", "compress_dqn", "identity"
    seed: int = 0
    device: str = "cuda"
