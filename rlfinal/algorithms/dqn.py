import torch
import torch.nn as nn
import numpy as np

from rlfinal.algorithms.replay_buffer import ReplayBuffer
from rlfinal.models.q_network import QNetwork
from rlfinal.utils.config import DQNConfig


def train_dqn(
    env,
    q_net: QNetwork,
    config: DQNConfig,
    device: str = "cuda",
    seed: int = 0,
    preprocess_fn=None,
    verbose: bool = True,
) -> dict:
    """Train Double DQN. preprocess_fn transforms observation before Q-network."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    q_net = q_net.to(device)
    target_net = QNetwork(q_net.net[0].in_features, 4, config.hidden_dim).to(device)
    target_net.load_state_dict(q_net.state_dict())
    target_net.eval()

    optimizer = torch.optim.Adam(q_net.parameters(), lr=config.lr)
    criterion = nn.MSELoss()
    replay = ReplayBuffer(config.replay_capacity)

    eps_decay_episodes = int(config.total_episodes * config.eps_decay_frac)
    total_steps = 0

    eval_success_rates = []
    eval_avg_returns = []
    eval_avg_path_lengths = []

    for ep in range(config.total_episodes):
        obs = env.reset()
        if preprocess_fn is not None:
            obs = preprocess_fn(obs)
        ep_reward = 0.0

        # Epsilon
        if ep < eps_decay_episodes:
            eps = config.eps_start - (config.eps_start - config.eps_end) * (ep / eps_decay_episodes)
        else:
            eps = config.eps_end

        for step in range(config.max_steps_per_episode):
            # Select action
            if np.random.random() < eps:
                action = np.random.randint(0, 4)
            else:
                with torch.no_grad():
                    obs_t = torch.FloatTensor(obs).unsqueeze(0).to(device)
                    q_vals = q_net(obs_t)
                    action = q_vals.argmax(dim=1).item()

            next_obs, reward, done, info = env.step(action)
            if preprocess_fn is not None:
                next_obs_processed = preprocess_fn(next_obs)
            else:
                next_obs_processed = next_obs

            replay.push(obs, action, reward, next_obs_processed, done)

            obs = next_obs_processed
            ep_reward += reward
            total_steps += 1

            # Train step
            if len(replay) >= config.batch_size:
                b_obs, b_act, b_rew, b_next, b_done = replay.sample(config.batch_size)
                b_obs = torch.FloatTensor(b_obs).to(device)
                b_act = torch.LongTensor(b_act).unsqueeze(1).to(device)
                b_rew = torch.FloatTensor(b_rew).unsqueeze(1).to(device)
                b_next = torch.FloatTensor(b_next).to(device)
                b_done = torch.FloatTensor(b_done).unsqueeze(1).to(device)

                # Double DQN
                with torch.no_grad():
                    next_actions = q_net(b_next).argmax(dim=1, keepdim=True)
                    next_q = target_net(b_next).gather(1, next_actions)
                    target = b_rew + config.gamma * (1 - b_done) * next_q

                current_q = q_net(b_obs).gather(1, b_act)
                loss = criterion(current_q, target)

                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(q_net.parameters(), 10.0)
                optimizer.step()

            # Update target network
            if total_steps % config.target_update_freq == 0:
                target_net.load_state_dict(q_net.state_dict())

            if done:
                break

        # Evaluation
        if (ep + 1) % config.eval_freq == 0:
            sr, ar, pl = evaluate(env, q_net, config, device, preprocess_fn)
            eval_success_rates.append((ep + 1, sr))
            eval_avg_returns.append((ep + 1, ar))
            eval_avg_path_lengths.append((ep + 1, pl))
            if verbose:
                print(f"  Eval @ episode {ep+1}: success={sr:.2f}, return={ar:.2f}, path_len={pl:.1f}")

    return {
        "eval_success_rates": eval_success_rates,
        "eval_avg_returns": eval_avg_returns,
        "eval_avg_path_lengths": eval_avg_path_lengths,
    }


@torch.no_grad()
def evaluate(env, q_net: QNetwork, config: DQNConfig, device: str, preprocess_fn=None) -> tuple[float, float, float]:
    """Greedy evaluation over eval_episodes. Returns (success_rate, avg_return, avg_path_length)."""
    q_net.eval()
    total_return = 0.0
    successes = 0
    path_lengths = 0

    for _ in range(config.eval_episodes):
        obs = env.reset()
        if preprocess_fn is not None:
            obs = preprocess_fn(obs)
        ep_return = 0.0

        for step in range(config.max_steps_per_episode):
            obs_t = torch.FloatTensor(obs).unsqueeze(0).to(device)
            action = q_net(obs_t).argmax(dim=1).item()
            next_obs, reward, done, info = env.step(action)
            if preprocess_fn is not None:
                obs = preprocess_fn(next_obs)
            else:
                obs = next_obs
            ep_return += reward
            if done:
                if reward > 0:
                    successes += 1
                    path_lengths += step + 1
                else:
                    path_lengths += config.max_steps_per_episode
                break

        total_return += ep_return

    q_net.train()
    n = config.eval_episodes
    return successes / n, total_return / n, path_lengths / n
