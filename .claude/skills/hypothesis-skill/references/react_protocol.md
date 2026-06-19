# ReAct Protocol — Hypothesis Generation Loop

## Overview

The ReAct (Reasoning + Acting) protocol drives the hypothesis generation loop. It interleaves analytical reasoning with literature search actions, progressively refining the understanding of research gaps.

## Algorithm

```
max_rounds = 3
verified_gaps = []
hypotheses = []
papers_read = []

for round in 1..max_rounds:
    # ── REASONING ──
    1. Analyze current literature coverage:
       - What approaches exist?
       - What are the SOTA results?
       - What are the stated limitations in key papers?

    2. Identify candidate gaps:
       - Performance plateaus (no improvement in 2+ years on metric X)
       - Unexplored combinations (method A + domain B not tried)
       - Assumption violations (real-world doesn't match lab conditions)
       - Scaling failures (method works at small scale but not large)
       - Missing evaluation dimensions (fairness, robustness, efficiency)

    3. Prioritize gaps for verification:
       - Impact: if solved, would it matter?
       - Verifiability: can we check if it's a real gap?
       - Actionability: can we design an experiment?

    # ── ACTING ──
    4. For each priority gap:
       a. Formulate targeted search query:
          - "Has [approach] been applied to [domain]?"
          - "Recent papers on [limitation mentioned in key paper]"
          - "[method] + [problem setting] + benchmark"
       b. Search academic APIs (arXiv + Semantic Scholar + OpenAlex)
       c. For top K results:
          - Download PDF
          - Read abstract, introduction, method, and conclusion
          - Extract: does this paper fill the gap?
       d. Update gap status:
          - CONFIRMED: no paper fills this gap → add to verified_gaps
          - FILLED: paper X fills this gap → update literature map
          - PARTIAL: partially addressed → refine gap definition

    5. Generate new search queries from gap refinements:
       - "What if we remove assumption X?"
       - "Alternative evaluation protocol for [task]"
       - "Failure cases of [best method]"

    # ── STOPPING CONDITIONS ──
    - No new verified gaps in this round
    - All priority gaps confirmed or filled
    - Max rounds reached
    - Search returns <3 new papers (literature saturation)

# ── HYPOTHESIS GENERATION ──
For each verified_gap:
    6. Formulate hypothesis:
       - What: specific claim (falsifiable)
       - Why: evidence from literature supporting the gap
       - How: proposed approach (method sketch)
       - Metrics: how to measure success
       - Baselines: what to compare against

    7. Literature grounding (minimum 3 papers per hypothesis):
       - Gap evidence: paper(s) showing the gap exists
       - Method inspiration: paper(s) with related techniques
       - Baseline reference: paper(s) defining SOTA to beat

    8. Score hypothesis (see scoring_rubric.md)
```

## Round-Specific Guidance

### Round 1: Broad Exploration
- Search broadly (general topic keywords)
- Read 5 papers deeply
- Goal: build the research landscape map
- Expected output: 10-15 candidate gaps (unverified)

### Round 2: Targeted Verification
- Search specifically for gap-related terms
- Read 5 papers deeply (focused on gap verification)
- Goal: confirm or refute candidate gaps
- Expected output: 3-7 verified gaps

### Round 3: Depth & Refinement
- Search for edge cases, alternative approaches
- Read 3-5 papers deeply
- Goal: refine hypotheses, add evidence
- Expected output: final hypothesis set with strong grounding

## Search Query Patterns

| Gap Type | Query Pattern |
|----------|--------------|
| Performance plateau | "[task] benchmark [year]" or "state of the art [task] [year]" |
| Unexplored combination | "[method A] for [domain B]" or "[method A] [domain B]" |
| Assumption violation | "limitation of [method]" or "[method] fails when" |
| Scaling failure | "[method] large scale" or "scaling [method]" |
| Missing evaluation | "[task] fairness" or "[task] robustness evaluation" |

## PDF Deep-Reading Strategy

For each paper selected for deep reading:

1. **Abstract** (30s): Does this paper claim to solve the gap?
2. **Introduction** (2min): What problem do they address? What are their contributions?
3. **Method** (3min): Is their approach similar to what we'd propose?
4. **Experiments** (2min): What datasets, metrics, baselines? Are the results convincing?
5. **Conclusion/Limitations** (1min): What do they admit they didn't solve?

Record in `pdf_notes/<paper_key>.md`:
- Key findings relevant to our gap
- Whether this paper fills, partially fills, or doesn't fill the gap
- Useful references from their bibliography
- Potential methodological inspiration
