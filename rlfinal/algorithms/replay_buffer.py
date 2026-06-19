import random
from collections import deque

import numpy as np


class ReplayBuffer:
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, obs, action, reward, next_obs, done):
        self.buffer.append((obs, action, reward, next_obs, done))

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        obs, act, rew, next_obs, done = zip(*batch)
        return (
            np.stack(obs),
            np.array(act),
            np.array(rew, dtype=np.float32),
            np.stack(next_obs),
            np.array(done, dtype=np.float32),
        )

    def __len__(self):
        return len(self.buffer)
