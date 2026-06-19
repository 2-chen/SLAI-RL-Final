# Academic Writing Patterns for CCF-A Papers

Section-level architecture patterns drawn from curated Nature/Nature Communications and top AI conference papers. Structural patterns, not wording templates.

## The Central Argument Chain

Before any drafting, reduce the paper to one chain:

```
field-scale need → unresolved bottleneck → proposed move → decisive evidence → broader implication → boundary
```

If any link is missing, mark it as missing. Do not write around it.

---

## Abstract Patterns

### Pattern A: Challenge-Contribution (most common for method papers)

```
[1-2 sentences context/problem]
[1 sentence gap — why current work doesn't solve it]
[1 sentence approach — what we do]
[1-2 sentences result — strongest quantitative finding]
[1 sentence implication — what this enables]
[Optional: 1 sentence boundary]
```

**Diagnostic checklist**:
- Begins with context, not "Here, we" (missing context flag)
- Contains at least one number or comparison (anchoring)
- Ends with what the work enables, not generic importance
- No citations (most conferences forbid them in abstracts)

### Pattern B: Challenge-Insight-Contribution

For papers where the core insight is the contribution:
```
[problem context] → [why it's hard] → [key insight] → [how insight leads to method] → [result + implication]
```

### Pattern C: Multiple Contributions

For papers with 2-3 distinct contributions:
```
[overall problem] → [gap 1 + contribution 1] → [gap 2 + contribution 2] → [combined result]
```

---

## Introduction Architecture

### Standard Funnel (5 paragraphs for 8-page papers)

**Paragraph 1 — Field Stake** (3-4 sentences):
- Open with the domain and its importance
- End with a sense of momentum: "Recent advances in X have enabled Y, but Z remains challenging."

**Paragraph 2 — Bottleneck** (4-5 sentences):
- Describe the specific technical challenge
- Explain why existing approaches handle it poorly
- Use concrete examples, not abstract claims
- End with: "This limitation motivates the need for [capability]."

**Paragraph 3 — Prior Work Gap** (4-5 sentences):
- Treat prior work fairly: acknowledge what they achieve
- Then identify the unresolved gap
- "While [method A] addresses [aspect], it [remaining limitation]."
- Do NOT claim novelty by dismissing prior work — that signals insecurity

**Paragraph 4 — Present Study** (3-4 sentences):
- "In this paper, we [action]."
- Describe the approach: key idea, not implementation details
- Preview the strongest result

**Paragraph 5 — Contributions** (numbered list, 3-4 items):
- Each item: what we contribute + why it matters
- Use parallel structure
- "1. We propose [X], which [Y]."
- "2. We demonstrate that [finding] on [benchmarks]."
- "3. We release [code/dataset/model] to facilitate [Z]."

### Common Introduction Failures

| Failure | Fix |
|---------|-----|
| Literature list without narrowing logic | Group by topic, end each paragraph with remaining gap |
| Novelty claims without evidence | Replace "We are the first to" with what you actually show |
| Results announced before reader understands question | Move results preview to paragraph 4 |
| Opening too narrow ("We propose a novel...") | Start with the problem, not your solution |
| Vague urgency ("X is important") | Quantify the importance or state a concrete consequence |

---

## Related Work Architecture

**Rule**: Topic synthesis, NOT paper-by-paper catalog.

### Pattern: Topic → Methods → Limitation → Distinction

```
Paragraph structure:
  [Topic scope] → [2-3 representative methods + what they achieve] → [shared limitation relevant to this paper] → [how our work differs]

Repeat for 3-4 topic clusters.
```

**Sentence templates** (not wording, but structural patterns):
- Topic opening: "Research on [X] has explored [direction A], [direction B], and [direction C]."
- Method grouping: "[Author1] ([year]) and [Author2] ([year]) independently showed that [finding]."
- Limitation pivot: "However, these methods [shared limitation], because [reason]."
- Distinction: "Unlike [existing approach] which [mechanism], our method [key difference]."

**Anti-patterns to avoid**:
- "There is extensive work on [X]. [Paper1] proposed [A]. [Paper2] proposed [B]. [Paper3] proposed [C]." — No synthesis; reads like a student survey.
- "No prior work has addressed [X]." — Almost certainly wrong and signals incomplete literature search.
- "To the best of our knowledge, we are the first..." — Hedge better or just state the gap.

---

## Method Architecture

### Overview-First Pattern

```
[Figure 1: architecture overview]
  ↓
[One-paragraph pipeline summary]
  ↓
[Module 1: motivation → design → technical advantage → implementation]
  ↓
[Module 2: ...]
  ↓
[Training objective / optimization]
```

### Module Writing Triad

For each module, answer three questions:
1. **Motivation**: Why is this module needed? (一兩句話說清楚這個模塊要解決的問題)
2. **Design**: How does it work? (數學公式 + 文字說明)
3. **Advantage**: Why is this design better than alternatives? (和其他可能的做法比較)

**Example structure**:
```
[3.1 Module Name]
Motivation: "Standard [approach] suffers from [problem] because [reason].
            To address this, we introduce [module name]."

Design: "As shown in Figure 2, [module] takes [input] and produces [output].
        Formally, [equation]. The key insight is that [why this works]."

Advantage: "Compared to [alternative], [module] achieves [benefit]
           while maintaining [property]."
```

---

## Experiments Architecture

### Evidence Ladder

```
[Setup] → [Main Comparison] → [Ablation] → [Analysis] → [Generalization / Stress Test]
```

### Setup Section
- Datasets: name, size, source, split
- Baselines: group by type, note why each was chosen
- Metrics: primary + secondary, with justification
- Implementation: framework, hardware, hyperparameters (can be in appendix)

### Main Results Section

Table pattern:
```latex
\begin{table}[t]
\centering
\caption{Main results on [dataset]. Best results in \textbf{bold}, second-best \underline{underlined}.}
\begin{tabular}{@{}lcccc@{}}
\toprule
Method & Metric1 $\uparrow$ & Metric2 $\uparrow$ & Metric3 $\downarrow$ & Avg \\
\midrule
Baseline A (year) & 72.3 & 68.1 & 0.42 & 73.9 \\
Baseline B (year) & 74.1 & 70.3 & 0.38 & 75.6 \\
\addlinespace
\textbf{Ours (variant 1)} & 77.5 & 73.0 & 0.31 & 78.8 \\
\textbf{Ours (variant 2)} & \textbf{78.9} & \textbf{74.2} & \textbf{0.28} & \textbf{79.4} \\
\bottomrule
\end{tabular}
\end{table}
```

Narrative after table:
- Start with the strongest finding: "Our method outperforms all baselines by at least X% on metric Y."
- Then compare to specific baselines: "Compared to [strongest baseline], our approach improves [metric] from [old] to [new]."
- Explain why: "We attribute this improvement to [component] which [mechanism]."

### Ablation Section

Structure:
- Component ablations: remove one component at a time
- Design choice ablations: compare alternative designs for key hyperparameters
- One table per ablation study
- End with: which components matter most, ranked by impact

### Analysis Section

Options (pick 1-2 most informative for your work):
- Qualitative examples (figure with success + failure cases)
- Error analysis (where does the method fail? why?)
- Efficiency analysis (training time, inference speed, memory)
- Robustness analysis (domain shift, noise, hyperparameter sensitivity)
- Case study (deep dive on a single representative example)

---

## Conclusion Architecture

### Bounded Conclusion (1 paragraph, ~150 words)

```
[1 sentence: central advance]
[1-2 sentences: key evidence summary]
[1 sentence: limitation]
[1 sentence: future direction]
```

**Do NOT**:
- Restate the abstract
- Introduce new claims not supported in the paper
- End with "Future work will explore..." without a specific direction
- Overclaim: "Our method solves X" → "Our method advances X by demonstrating Y"

---

## Language & Style Guide

### Claim Calibration

| Evidence Strength | Appropriate Verbs |
|-------------------|-------------------|
| Statistically significant on 3+ datasets | show, demonstrate, establish |
| Statistically significant on 1-2 datasets | demonstrate, indicate |
| Ablation only (no comparison to SOTA) | suggest, indicate |
| Qualitative only | may suggest, appears to |
| Single case study | illustrate, exemplify |

### Conciseness Rules

**Remove**:
- "It is worth noting that..." → (delete, just state the point)
- "It can be seen that..." → (delete)
- "We believe that..." → (delete, unless genuinely subjective)
- "Interestingly, ..." → (let the reader decide what's interesting)
- "To the best of our knowledge..." → (state the gap or remove)
- "delve into", "leverage" (overused), "furthermore" (use sparingly), "moreover" (use sparingly)

**Replace**:
- "in order to" → "to"
- "a number of" → "several" or state the number
- "due to the fact that" → "because"
- "has the capability to" → "can"
- "in the context of" → "in" or "for"

### Paragraph Flow Check

After drafting, run for each paragraph:
1. What is the one message of this paragraph? (Write it in the margin.)
2. Does the first sentence announce that message?
3. Does every subsequent sentence support it?
4. Is the relationship between consecutive sentences clear? (cause → effect, claim → evidence, general → specific)

If you can't answer #1, the paragraph needs restructuring.

### AI-Writing Markers to Avoid

Patterns that signal LLM-generated text to reviewers:
- Excessive hedging: "may potentially", "could possibly", "might perhaps"
- Formulaic transitions: every paragraph starts with "Furthermore," "Moreover," "Additionally,"
- Vague grandeur: "groundbreaking", "revolutionary", "paradigm-shifting"
- Generic conclusions: "opens up exciting avenues for future research"
- Definition stacking: opening with 3+ sentences that each define a term
- Absent voice: "One may consider" instead of "We consider"
