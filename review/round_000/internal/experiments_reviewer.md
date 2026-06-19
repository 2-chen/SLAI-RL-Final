# Internal Review: Experiments Reviewer

## Experimental Review

### Strengths (3-5)

1. **实验矩阵设计规范**：4 (M) × 3 (pipeline) × 5 (seeds) = 60 组实验（实际为 45 组，因 Identity baseline 不随 M 变化）。多种子策略对 RL 实验至关重要，5 个种子是合理的最低标准。

2. **评估指标选择合理**：成功率、回报、路径长度三个指标从不同维度衡量性能。特别是路径长度作为衡量策略最优性的指标，在 GridWorld 场景下非常恰当。

3. **报告了标准差**：表 1 中所有指标均报告了 ± 标准差，这是负责任的实验报告方式。

4. **实验发现具有清晰的模式**：DQN-only 性能随 M 单调递减，SSL→DQN 性能保持稳定，这一模式在不同指标间一致，增强了结论的可信度。

### Weaknesses (3-5)

1. **统计假设检验完全缺失**：论文未报告任何统计显著性检验（如 t-test 或 bootstrap 置信区间）。例如，M=128 时 DQN-only (160 ep) 是否显著优于 SSL→DQN (250 ep)？标准差分别为 37 和 55，重叠较大，需要进行统计检验才能下结论。

2. **实验结果内部不一致**：表 1 中 SSL→DQN 在 M=128 时最终成功率仅为 0.60 ± 0.49，但在 M=256 时反而达到 1.00。这与"SSL 预训练使样本效率几乎与 M 无关"的核心声明矛盾。如果在低维度（M=128）时 SSL 表现很差，那么"接近无关"的说法不成立。

3. **训练 episode 数不足**：仅训练 1000 episode 就做结论可能有误导。从图 2 学习曲线看，M=128 和 M=256 时 DQN-only 的学习曲线仍在上升趋势，更多的训练可能改变 DQN-only vs SSL→DQN 的相对排序。作者在局限部分承认了这一点但未做任何补救措施（如报告 2000 episode 的结果作为对照）。

4. **缺少 ablation study**：论文声称证明了 SSL 预训练的价值，但未分离 autoencoder 的各个组件：
   - Bottleneck 维度（固定 64）vs 变化的影响
   - Encoder 架构（深度、宽度）的影响
   - SSL 训练数据量（当前使用全部 64 个状态 vs 部分状态）的影响
   - 关键消融：如果 encoder 是随机初始化的（未训练），DQN 在此随机潜在空间中表现如何？

5. **计算成本未报告**：SSL→DQN 比 DQN-only 多了 SSL 预训练步骤。当 M=1024 时 SSL→DQN 的收敛时间 vs DQN-only 的收敛时间？总计算成本（wall-clock time 或 FLOPs）的比较对实际应用选择至关重要，但完全缺失。

### Missing Baselines / Metrics

1. **缺少非深度 RL baseline**：例如使用 tile coding + linear function approximation 的 Q-learning，或基于 k-NN 的状态聚合方法。这些简单的 baseline 可以揭示 DQN 是否过度复杂。

2. **缺少其他 SSL 方法**：仅评估了标准 autoencoder。VAE、contrastive learning (SimCLR-style)、或更简单的 PCA 降维作为 baseline 会非常 informative。

3. **缺少状态表示质量的直接度量**：除了下游 DQN 性能外，应报告潜在表示对真实状态的线性可分性（linear probing accuracy）或 k-NN 分类准确率。这可以直接量化 SSL encoder 学到的表示质量。

4. **缺少 Random agent baseline**：一个随机动作的 agent 在 GridWorld 中的表现（成功率、路径长度）可以作为一个有用的下界。

### Statistical Issues

1. **仅 5 个种子，未报告标准差之外的不确定性度量**：对于样本效率（达到 90% 所需 ep），标准差非常大（如 DQN-only M=512: ±389）。这意味着种子的随机性对结果影响极大。应至少报告 95% bootstrap 置信区间，并且应讨论是否某些管线对种子特别敏感。

2. **"达到 90% 成功率"这一阈值的任意性**：为什么选择 90% 而不是 95% 或 80%？应进行灵敏度分析。特别是 M=128 SSL→DQN 的最终成功率只有 60%，按照定义它永远达不到 90% 阈值——表格中报告的值 250 ep 是如何计算的？

3. **成功率的二值化损失了信息**：episode 内的渐进改善（如路径长度逐步缩短）被掩盖。应报告最终的连续性能分布而非仅 0/1 成功率。

### Detailed Issues (with PROBLEM→IMPACT→FIX format)

**[PROBLEM 1] M=128 SSL→DQN 最终成功率仅 60%，低于 DQN-only 的 100% → [IMPACT]** 这一结果直接挑战了论文的核心叙述"SSL 预训练有帮助"。在最低的观测维度下 SSL 预训练反而有害，论文将其归因于"计算开销"但这不能解释为什么成功率受到根本性影响（如果 bottleneck 维度匹配且 SSL 收敛，应该表现得至少和 DQN-only 一样好）。**→ [FIX]** 深入分析 M=128 的失败原因：(a) 检查 SSL 重建质量是否真的收敛（loss 值 vs epoch）;(b) 比较 SSL encoder 输出的潜在表示与真实 one-hot 状态的结构相似性;(c) 尝试不同的 SSL 训练 epoch 数。

**[PROBLEM 2] 表 1 中 M=128 SSL→DQN 的"达到 90% 所需 Ep"为 250，但最终成功率仅 60% → [IMPACT]** 如果最终成功率只有 60%，怎么可能曾经"达到 90%"？这是逻辑矛盾，表明数据报告有误或评估方法存在问题。**→ [FIX]** 修正数据：(a) 如果最终成功率 < 90%，"达到 90% 所需 Ep"应标记为 N/A;(b) 或在评估时不使用 greedy evaluation（当前方法），改用训练中的平滑成功率。

**[PROBLEM 3] 跨 M 的实验结果存在系统性不一致 → [IMPACT]** SSL→DQN 在 M=128 成功率 60%、M=256 成功率 100%、M=512 成功率 80%、M=1024 成功率 100%。这一非单调模式表明存在未控制的混淆变量（如随机种子的偶然效应、autoencoder 训练的不稳定性）。当前 5 个种子可能不足以获得稳定估计。**→ [FIX]** 将种子数增至至少 10，并对关键对比进行 bootstrap 重采样分析。

**[PROBLEM 4] 学习曲线图 (图 2) 的 x 轴到 2000 但正文说只训练 1000 episode → [IMPACT]** 图 2 的学习曲线 x 轴显示到 2000 episode，但方法部分明确说明"总训练 episode 数 1,000"。这是一个严重的不一致。**→ [FIX]** 澄清实际训练的 episode 数，修正图表或修正正文。

**[PROBLEM 5] 缺少 cross-validation 式的验证 → [IMPACT]** 每个配置 5 个种子提供了点估计和方差，但未报告：(a) 每个种子内部的最佳 checkpoint（而非固定 1000 ep 的最终值）;(b) 不同超参数设置的结果（如学习率的 sensitivity analysis）。**→ [FIX]** 增加学习率和网络架构的超参数敏感性分析。

### Score (1-10)
**3 / 10**

### Recommendation: Reject
实验部分存在致命的数据一致性问题（学习曲线 episode 数与正文矛盾，M=128 SSL→DQN 的 90% 阈值数据与最终成功率逻辑冲突）。缺少统计检验、消融实验和计算成本分析。仅 5 个种子不足以支撑稳健结论。建议大幅修订实验方案并重新收集数据后再投稿。
