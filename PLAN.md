# 期末报告研究计划

**课题**：观测维度对 DQN 样本效率的影响，及自监督预训练 encoder 的作用
**作者**：中国国家人工智能学院博士生
**硬件**：H100 80GB GPU（环境搭建使用 uv 管理虚拟环境）

---

## 一、研究问题

| 维度 | 问题 |
|---|---|
| **主问题** | 状态编码维度 M ∈ {128, 256, 512, 1024} 对 DQN 样本效率（达到目标成功率所需 episode 数）的影响 |
| **副问题** | 相同维度下，**自监督预训练 encoder** vs **随机冻结 encoder**，哪个样本效率更高 |
| **参照基线** | Identity（DQN 直接用 64 维 one-hot）作为理论上限 |

---

## 二、关键设计：真实状态在训练中不可见

**核心约束**：agent 在训练的任何阶段都看不到真实的 64 维 one-hot 状态 `s`。`s` 仅作为环境的"内部状态"存在，通过随机 MLP 投影为 M 维观测后才被算法使用。

### 数据流

```
真实状态 s (64 维 one-hot)         ← 只在环境内部存在，训练不可见
        │
        │  冻结的随机 MLP E
        ▼
观测 obs (M 维)                    ← agent 唯一能"看到"的东西
        │
   ┌────┴────────────────┐
   │ 管线 1 (SSL→DQN)    │  管线 2 (DQN only)
   │                    │
   │  SSL Encoder       │  (没有 SSL)
   │  E_ssl: M → 64     │
   │  (训练得到)         │
   │                    │
   │  训练信号：         │
   │  Decoder D_ssl:    │
   │  64 → M            │
   │  Loss = ||obs -    │
   │    D_ssl(E_ssl(obs))||²
   │                    │
   ▼                    ▼
   z (64 维)            obs (M 维)
   (learned latent,     (原始随机投影)
    不等于 s！)
   │                    │
   └────┬───────────────┘
        ▼
       DQN 输入
```

**关键点**：
- `s` 在训练中**永远不出现**——只用来生成 obs（环境接口）
- SSL encoder 的 64 维输出 **不是** `s`，是从 obs 学到的降维表示
- SSL 训练用的是 **M 维重建损失**（自监督，不依赖 `s`，也不依赖 reward）
- DQN 输入是 `z`（管线 1）或 `obs`（管线 2）
- 64 维这个数等于状态空间基数只是巧合，实际值是连续向量

---

## 三、两条管线 + Identity baseline

| 管线 | Encoder 阶段 | SSL 阶段 | DQN 输入 |
|---|---|---|---|
| **SSL→DQN** | 随机 MLP `E: 64→M`（冻结） | 训 autoencoder `(M→64→M)`，冻结 encoder | SSL encoder 输出的 64 维 latent |
| **DQN-only** | 随机 MLP `E: 64→M`（冻结） | 无 | M 维原始观测 |
| **Identity** | 无（直接用 one-hot） | 无 | 64 维 one-hot |

**统一 DQN 架构**：`input_dim → 256 → 256 → 4`，仅输入维度变化。

---

## 四、代码结构

```
rlfinal/
├── env/
│   └── gridworld.py            # 8×8 Gym-like 环境 + BFS 最短路
├── models/
│   ├── encoder.py              # RandomEncoder / Identity
│   ├── decoder.py              # SSL Encoder (M→64) + Decoder (64→M)
│   └── q_network.py            # 统一 DQN 架构
├── algorithms/
│   ├── ssl_pretrain.py         # Autoencoder 训练
│   ├── dqn.py                  # Double DQN 训练
│   ├── replay_buffer.py        # 经验回放
│   └── evaluate.py             # Greedy 评估 + 路径长度统计
├── experiments/
│   ├── run_ssl_dqn.py          # 管线 1
│   ├── run_random_dqn.py       # 管线 2
│   └── run_identity.py         # baseline
├── analysis/
│   ├── plot_curves.py          # 学习曲线 (success rate vs episode)
│   └── plot_efficiency.py      # 样本效率 (episodes to 90% success)
├── utils/
│   ├── seed.py
│   ├── logger.py
│   └── config.py
├── configs/default.yaml
├── train.py                    # 主入口
├── PLAN.md                     # 本文件
└── README.md
```

---

## 五、关键实现细节

### 5.1 GridWorld

- 状态 one-hot(64)，动作 4（撞墙不移动，不终止）
- 奖励：goal +1，其他 0
- Episode 终止：到达 goal 或 64 步
- BFS 算真实最短路，评估时统计实际路径长度
- 最优路径长度 = 14 步

### 5.2 随机 Encoder（E: 64→M）

- 线性层 + ReLU + 线性层
- 固定 seed 初始化，**冻结不训**
- 同一 seed 下生成的 E 对所有实验组保持一致

### 5.3 Autoencoder (SSL)

- 结构：Encoder `M→64` + Decoder `64→M`
- 训练数据：随机 rollout 收集 `obs = E(s)`（贴近真实场景）
- 损失：`L = ||obs - D_ssl(E_ssl(obs))||²`（M 维重建）
- Adam, lr=1e-3
- 训到 reconstruction loss 收敛后冻结 E_ssl
- 注：64 维是瓶颈，不是真实状态；reconstruction 质量用 `||obs - obs_recon||` 评估，**不涉及 `s`**

### 5.4 Double DQN

| 超参 | 值 |
|---|---|
| 折扣因子 γ | 0.99 |
| 学习率 | 1e-3 |
| Batch size | 64 |
| Replay buffer | 10000 |
| ε-greedy | 1.0 → 0.05，前 20% episode 线性衰减 |
| Target network | 每 100 步硬更新 |
| 总 episode | 5000 |
| 评估频率 | 每 100 episode 跑 1 次 greedy 评估（10 episode 平均） |

### 5.5 实验矩阵

- 4 (M) × 3 (管线) × 5 (seeds) = **60 组**
- 单组预计 1–3 分钟（H100 实际利用率极低，主要在 CPU rollout）

### 5.6 评估指标

- **样本效率**：达到 90% 成功率所需 episode 数
- **最终性能**：训练结束后的平均回报
- **最终路径长度**：实际路径长度 vs BFS 最短路（14 步）
- **收敛稳定性**：跨 seed 的方差

### 5.7 种子策略

- 固定 base seed，派生 60 个 seed 序列
- Random encoder 的初始化、SSL 训练、RL 训练三者种子独立可追溯

---

## 六、GPU 使用策略

虽然 H100 80GB 远超本任务需求（8×8 网格 64 状态），但统一在 GPU 上跑：
- 模型权重、replay buffer 采样 batch、前向/反向都放 GPU
- Rollout 阶段在 CPU（`s → obs` 通过冻结 MLP 一次性 batch 计算后传 GPU）
- 单组实验 1–3 分钟，60 组串行约 1.5–3 小时

---

## 七、实施阶段（任务清单）

1. **环境搭建**：uv 创建 venv，安装 PyTorch (cu128/cu124) + numpy + matplotlib + pyyaml + tqdm，验证 H100 可用
2. **GridWorld + 单元测试**
3. **Encoder / Decoder / Autoencoder + 单元测试**
4. **Autoencoder SSL 预训练**（验证 obs 重建质量）
5. **Double DQN 跑通 Identity baseline**
6. **三个 runner 跑通**（管线 1、2、Identity）
7. **全量实验矩阵**（60 组，H100）
8. **可视化**：每个 M 一张学习曲线（Random/SSL 叠加）+ 样本效率 vs M 折线图
9. **README + 报告骨架**

---

## 八、报告大纲

- **背景**：观测维度对 RL 样本效率的影响，自监督预训练的动机
- **方法**：
  - 8×8 GridWorld 设定
  - 随机投影 encoder 作为"不可逆传感器"
  - 两条训练管线 + Identity baseline
  - Double DQN + Autoencoder SSL
- **实验**：
  - 实验设置（超参、seeds）
  - 样本效率 vs M
  - 学习曲线对比
  - SSL encoder 重建质量分析
- **分析**：
  - SSL 在小 M（高压缩）下优势是否更显著
  - SSL encoder 是否学到类似 one-hot 的稀疏表示
  - 失败 case 分析
- **结论**：
  - SSL 改善样本效率的条件
  - M 的选择对最终性能的影响
  - 局限与未来工作

---

## 九、已确认的设计决策

| 决策 | 选择 |
|---|---|
| 训练算法 | Double DQN（不是 DPO） |
| 真实状态 s 是否可见 | **完全不可见**，仅作环境内部状态 |
| 64 维 latent 含义 | M 维观测的降维表示，**不是** 真实状态 |
| DQN 输入 | SSL 重建 64 维（管线 1）/ M 维（管线 2）/ 64 维 one-hot（Identity） |
| SSL 方法 | 标准 autoencoder（M→64→M 重建 obs） |
| DQN 架构 | 统一 `input→256→256→4` |
| 每组 episode | 5000 |
| 实验矩阵 | 4M × 3 管线 × 5 seeds = 60 组 |
| GPU | H100 80GB |
| 环境管理 | uv（首选） → conda → pyenv/venv |

---

## 十、待办（实施阶段前可继续讨论）

- [ ] Autoencoder 训练数据：用随机 rollout 收集（贴近真实）vs **枚举 64 状态**（更稳定，SSL 阶段零随机性）— 倾向枚举
- [ ] Random encoder 内部是否有激活函数（目前规划为 Linear+ReLU+Linear）— 倾向于无激活的纯线性投影，让 64 维状态在 M 维空间保持线性可分性
- [ ] 是否记录 SSL encoder 输出 `z` 的可视化（t-SNE / PCA）— 倾向记录
- [ ] 是否引入梯度分析（SSL encoder 的梯度如何回传到 DQN）— 暂不引入，保持干净
