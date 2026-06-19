# Hypothesis Scoring Rubric

## Dimensions

Each hypothesis is scored on three dimensions (1-10), then combined into a composite score.

### 1. Novelty (Weight: 40%)

How original and non-obvious is the hypothesis?

| Score | Description |
|-------|-------------|
| 9-10 | Truly novel — no prior work exists in this direction. Opens a new sub-area. |
| 7-8 | Strong novelty — combines ideas in a non-obvious way. Clearly differentiated from prior work. |
| 5-6 | Moderate novelty — incremental improvement on known approach. Similar to existing work but with a twist. |
| 3-4 | Weak novelty — largely replicates existing approaches. Minor variation on well-explored idea. |
| 1-2 | Not novel — already published with similar results. Would be desk-rejected. |

**Evidence required**:
- Literature search confirms no paper proposes the same solution
- ≥3 papers document the gap but don't propose the solution

### 2. Feasibility (Weight: 35%)

Can this hypothesis be tested with available resources?

| Score | Description |
|-------|-------------|
| 9-10 | Immediately testable — standard datasets, standard compute, clear protocol. |
| 7-8 | Feasible — requires moderate resources (multi-GPU training, public datasets). |
| 5-6 | Challenging — needs specialized hardware, large-scale data, or long training time. |
| 3-4 | Difficult — requires resources not commonly available (TPU pods, proprietary data). |
| 1-2 | Infeasible — requires resources or data that don't exist or are inaccessible. |

**Evidence required**:
- Datasets are publicly available and standard for the task
- Compute requirements are within scope (single-node GPU or small cluster)
- Method can be implemented with standard tools (PyTorch, TensorFlow, JAX)

### 3. Impact (Weight: 25%)

If successful, how significant would this contribution be?

| Score | Description |
|-------|-------------|
| 9-10 | Field-changing — would shift research direction. CCF-A oral / best paper potential. |
| 7-8 | High impact — significant improvement on important problem. Strong conference publication. |
| 5-6 | Moderate impact — useful contribution to a specific sub-area. Solid workshop or conference paper. |
| 3-4 | Limited impact — narrow scope, small community. May still be publishable. |
| 1-2 | Minimal impact — too narrow or solved problem. Difficult to publish. |

**Evidence required**:
- Problem is actively researched (≥10 papers in last 2 years)
- Improvement would be meaningful to practitioners or theorists
- Venue fit is clear (can name specific conferences)

## Composite Score

```
composite = 0.40 × novelty + 0.35 × feasibility + 0.25 × impact
```

## Interpretation

| Composite | Label | Action |
|-----------|-------|--------|
| ≥ 8.0 | Excellent | Strong candidate — pursue immediately |
| 7.0 – 7.9 | Good | Good candidate — refine and pursue |
| 6.0 – 6.9 | Fair | Viable — need more evidence or refine scope |
| 5.0 – 5.9 | Marginal | Risky — only pursue if other options exhausted |
| < 5.0 | Poor | Skip — find a better research direction |

## Scoring Example

**Hypothesis**: "Adaptive prompt selection based on input complexity can improve few-shot performance without increasing model size"

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Novelty | 8.0 | Zhang et al. 2023 showed prompt quality varies by input, but no one has built adaptive selection. Not directly published. |
| Feasibility | 7.5 | GLUE/SuperGLUE are standard. Prompt tuning is well-understood. Needs 4× GPU for tuning. |
| Impact | 8.0 | Few-shot learning is hot (50+ papers in 2024). 15-20% improvement without more parameters would be significant. ACL/EMNLP material. |

**Composite**: 0.40 × 8.0 + 0.35 × 7.5 + 0.25 × 8.0 = **7.82 → Good**

## Anti-Patterns (Automatically Downgrade)

- Hypothesis contains "we will show" without specifying metrics → -1 feasibility
- Gap supported by <3 specific papers → -1 novelty
- No dataset identified → -2 feasibility
- Claims to beat SOTA without naming specific baselines → -1 impact
- "Revolutionary" / "first-ever" / "game-changing" language without proportional evidence → -1 novelty
