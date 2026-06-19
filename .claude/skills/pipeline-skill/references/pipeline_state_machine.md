# Pipeline State Machine — Complete Reference

All legal state transitions, preconditions, actions, and edge cases for the pipeline-skill orchestrator.

## States

| State | Description |
|-------|-------------|
| `INIT` | Pipeline started, intake in progress |
| `RESEARCH` | Stage 1: literature search & analysis |
| `EXPERIMENT` | Stage 2: GPU experiment execution (local or remote) |
| `WRITE` | Stage 3: CCF-A LaTeX paper writing |
| `REVIEW` | Stage 4: dual-source paper review |
| `VERDICT_GATE` | Evaluating whether to stop or continue |
| `COMPRESS` | Context compression before next iteration |
| `DONE` | Paper accepted (weak accept or better) |
| `PAUSED` | User interrupted, state saved |
| `FAILED` | Unrecoverable error |

## Transition Table

| From | To | Condition | Action |
|------|----|-----------|--------|
| `INIT` | `RESEARCH` | No literature found in workspace | Dispatch search-skill (lit-search) |
| `INIT` | `EXPERIMENT` | Literature exists, no experiments | Dispatch experiment-skill |
| `INIT` | `WRITE` | Literature + experiments exist, no paper | Dispatch write-skill |
| `INIT` | `REVIEW` | Paper exists, no review for current version | Dispatch review-skill |
| `INIT` | `PAUSED` | Pipeline state file found | Load state, ask user to resume |
| `RESEARCH` | `EXPERIMENT` | Research complete, user confirmed | Handoff: lit review + bib → experiment context |
| `RESEARCH` | `WRITE` | Research complete, experiment skipped | Handoff: lit review + bib → write context |
| `EXPERIMENT` | `WRITE` | Experiment complete (or skipped) | Handoff: experiment results + lit review → write context |
| `WRITE` | `REVIEW` | Paper compiled, user confirmed | Handoff: paper PDF + .tex → review context |
| `REVIEW` | `VERDICT_GATE` | Both external and internal reviews complete | Extract verdicts, compute decision |
| `VERDICT_GATE` | `DONE` | External verdict ∈ {accept, weak accept} | Save final state, produce summary |
| `VERDICT_GATE` | `COMPRESS` | External verdict ∉ {accept, weak accept} AND iteration < max | Compress context before loop |
| `VERDICT_GATE` | `DONE` | iteration ≥ max (regardless of verdict) | Forced stop, report best result |
| `COMPRESS` | `WRITE` | Compression complete | Start new iteration from Stage 3 with review feedback |
| `WRITE` | `PAUSED` | User interrupts | Save state, report resume command |
| Any | `PAUSED` | User interrupts | Save state with current stage |
| Any | `FAILED` | Unrecoverable error | Save state with error note, report |

## Verdict Gate Decision Matrix

```python
def verdict_gate(external_verdict: str, internal_avg: float, iteration: int, max_iterations: int) -> str:
    if iteration >= max_iterations:
        return "DONE"  # forced stop
    
    if external_verdict in ("accept", "weak accept"):
        return "DONE"
    
    if external_verdict == "borderline" and internal_avg >= 6.0:
        # Offer choice — one more iteration or stop
        return "USER_CHOICE"
    
    # All other cases: continue
    return "COMPRESS"
```

## Handoff Materials Per Transition

### RESEARCH → EXPERIMENT
```
- literature_review.md (path)
- references.bib (path)
- gap_analysis.md (path, if available)
- Key research question (text)
```

### RESEARCH → WRITE (experiment skipped)
```
- All RESEARCH → EXPERIMENT materials
- Note: "No experiments — theoretical/ survey paper or user skipped"
```

### EXPERIMENT → WRITE
```
- All RESEARCH materials
- Experiment results path (AFS or local)
- Execution run ID + status
- Key metrics summary
- Experiment plan (experiment_plan.md path)
```

### WRITE → REVIEW
```
- paper.pdf (path)
- paper.tex (path)
- Target venue
```

### REVIEW → VERDICT_GATE
```
- external.md path + verdict
- internal/merged_internal_review.md path + avg score
- synthesis.md path
```

### COMPRESS → WRITE (next iteration)
```
- resume_packet.md or iteration_N_brief.md
- Latest review files
- Previous paper.tex
- List of issues to address (from synthesis.md revision roadmap)
```

## Edge Cases

### E1: Experiment Fails All Retries
- Condition: Experiment failed 3+ times, user doesn't want to retry
- Action: Skip Stage 2 for this iteration. Write with available data. Flag "experiments pending" in paper.

### E2: paperreview.ai Timeout
- Condition: External review not ready after 2 hours
- Action: Save token. Offer: (a) wait longer, (b) use internal-only review, (c) check manually later.
- If internal-only: verdict = internal consensus mapped to external scale

### E3: Internal and External Verdicts Radically Disagree
- Condition: External says "accept", internal avg < 4.0, or vice versa
- Action: Flag the discrepancy. Trust external (paperreview.ai) for stop/go decision, but present internal critique for revision.

### E4: Context Compression Produces Too-Large Resume Packet
- Condition: After many iterations, even the resume packet is too large
- Action: Trim to essentials only — topic, latest verdict, top 3 issues, file paths. Drop iteration history detail.

### E5: User Wants to Change Direction Mid-Pipeline
- Condition: User says "actually, change the research question to X"
- Action: Hard reset (Level 2). Start fresh from Stage 1 with new topic. Archive old workspace.

### E6: Multiple Rapid Iterations with No Improvement
- Condition: 3+ consecutive iterations with same verdict and similar scores
- Action: Alert user. "Pipeline may be stuck — same verdict for 3 iterations. Consider: (a) major restructuring, (b) accepting current quality, (c) adding new experiments."
