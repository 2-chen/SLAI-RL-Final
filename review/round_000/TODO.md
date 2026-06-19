# Revision TODO — Round 000

## Critical (blocks resubmission)

- [ ] [I-001] Zero citations / No Related Work section — Write a comprehensive Related Work section with ≥25 references covering: DQN (Mnih+2015), Double DQN (van Hasselt+2016), CURL (Srinivas+2020), DrQ (Yarats+2020), RAD (Laskin+2020), SPR (Schwarzer+2021), ATC (Stooke+2021), autoencoder (Hinton & Salakhutdinov 2006), Atari (Bellemare+2013). See related_work_reviewer.md for full list.
- [ ] [I-002] SSL pretraining information advantage — Autoencoder uses all 64 states offline. Add an "online SSL" baseline where autoencoder trains on replay buffer data, or clearly acknowledge and discuss this limitation.
- [ ] [I-003] M=128 SSL→DQN data contradiction — SSL→DQN M=128 shows 250 ep to 90% but final success rate only 60%. Investigate root cause: (a) check if evaluation method is correct, (b) mark "ep to 90%" as N/A when final <90%, (c) increase seeds, (d) analyze why SSL fails at low M.
- [ ] [I-004] Figure 2 vs text episode count mismatch — Figure shows 2000 episodes, text says 1000. Align them and clarify evaluation vs. training episode counting methodology.

## Major (significantly weakens paper)

- [ ] [I-005] No statistical significance tests — Add t-tests or bootstrap CIs for key comparisons (especially DQN-only vs SSL→DQN at each M). Increase to ≥10 seeds.
- [ ] [I-006] No ablation study — Add: (a) bottleneck dimension sweep [8, 16, 32, 96, 128], (b) random untrained encoder control, (c) PCA dimensionality reduction baseline.
- [ ] [I-007] No computation cost analysis — Report wall-clock time and FLOPs for each pipeline×M combination. Compare fair-budget (equal compute) rather than equal-episode.
- [ ] [I-008] Missing baselines — Add: (a) non-deep-RL baseline (e.g., tile coding + linear Q-learning), (b) random agent lower bound.
- [ ] [I-009] Remove "特征线性化" paragraph self-contradiction — "随机投影 W 是非线性的（no，纯线性）" — fix or remove the parenthetical note.
- [ ] [I-010] Clarify "维度灾难" usage — Replace with more precise terminology: "观测空间膨胀带来的表示学习困难" or similar.

## Minor (cosmetic / clarity)

- [ ] [I-011] Define SSL acronym on first use
- [ ] [I-012] Unify Chinese/English terminology style throughout
- [ ] [I-013] Add error bars to Figure 1 (sample efficiency bar chart)
- [ ] [I-014] Add BFS optimal path reference line (14 steps) to path length figures
- [ ] [I-015] Report specific random seed values for reproducibility
- [ ] [I-016] Consider adding a figure showing SSL reconstruction quality (original vs reconstructed observations)

---

**Label convention**: [I-NNN] = internal reviewer issue. Numbers match reviewer detailed issues.

**Progress**: 0/16 items completed
