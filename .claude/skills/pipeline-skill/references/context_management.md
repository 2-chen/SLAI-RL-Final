# Context Management Protocol

How the pipeline manages Claude Code's finite context window across multiple iterations.

## Why This Matters

Each pipeline iteration involves:
- Loading skill definitions (SKILL.md, references, agents)
- Reading research materials (literature reviews, experiment logs)
- Writing/reading paper drafts (potentially long .tex files)
- Processing review feedback (multiple reviewer files)

After 2-3 full iterations, the accumulated conversation context can easily exceed 100K+ tokens. Without active management, Claude Code will exhibit:
- **Context truncation**: early instructions silently dropped
- **Forgetting**: losing track of the research question or earlier decisions
- **Degraded output**: shorter, less coherent sections
- **Hallucination**: filling gaps with fabricated content when source material is truncated

## Compression Levels

### Level 1: Soft Compression (Iteration Brief)

**When**: Iterations 2-5, context health is good (>30% free).

**What it does**:
1. Summarize the just-completed iteration into a compact brief
2. The brief becomes the "memory" of that iteration — the full conversation is discarded
3. The next iteration starts by reading: the brief + the latest review files + the current paper

**Iteration Brief Template**:
```markdown
# Iteration N Brief
**Date**: YYYY-MM-DD HH:MM
**Verdict**: [external verdict] / [internal avg]/10

## Top Issues from Review
### External (paperreview.ai)
1. [Issue] — Priority: [Critical / High / Medium]
2. [Issue] — Priority: [...]
3. [Issue] — Priority: [...]

### Internal Consensus
1. [Issue] (flagged by [N]/5 reviewers)
2. [Issue] (flagged by [N]/5 reviewers)

## Changes Made This Iteration
- [Change 1]
- [Change 2]
- ...

## Experiment Results (if any)
- Experiment Run: [run_id] — [status]
- Key metrics: [summary]

## Files to Load Next Iteration
- Paper: workspace/<topic>/paper/paper.tex
- Latest review: workspace/<topic>/review/round_NNN/
- References: workspace/<topic>/literature/references.bib
- Resume packet: pipeline_state/resume_packet.md
```

**Soft Compression Script** (what the orchestrator tells Claude Code):
```
CONTEXT COMPRESSION — LEVEL 1

You have just completed iteration N. Before starting iteration N+1, 
please compress:

1. Read the review files at workspace/<topic>/review/round_NNN/
2. Write an iteration brief to pipeline_state/iteration_N_brief.md 
   using the template in pipeline-skill/references/context_management.md
3. When iteration N+1 begins, you will start fresh. Your only context 
   will be:
   - pipeline_state/resume_packet.md
   - pipeline_state/iteration_N_brief.md
   - The latest paper.tex
   - The latest review files
4. Do NOT reference the full conversation history — it will not be available.

After writing the brief, I will start a new session for iteration N+1.
```

### Level 2: Hard Reset (Resume Packet)

**When**: Iteration 6+, context visibly degraded, or user requests.

**What it does**:
1. Write a comprehensive Resume Packet containing ALL essential state
2. Save all working files to disk
3. Start a completely fresh Claude Code session
4. The fresh session's initial prompt is: "Read pipeline_state/resume_packet.md and continue the pipeline"

**Resume Packet Template**:
```markdown
# Pipeline Resume Packet
**Generated**: YYYY-MM-DD HH:MM
**Next Iteration**: N+1
**Target**: weak accept

## Research Identity
- **Topic**: [full research topic]
- **Research Question**: [one-sentence RQ]
- **Hypothesis**: [core hypothesis]
- **Venue**: [target CCF-A conference]

## Current Paper State
- **Draft**: workspace/<topic>/paper/paper.tex
- **Compiled PDF**: workspace/<topic>/paper/paper.pdf
- **Page count**: [N] / [limit]
- **Key claims**:
  1. [claim 1]
  2. [claim 2]
  3. [claim 3]

## Literature Foundation
- **Review**: workspace/<topic>/literature/literature_review.md
- **BibTeX**: workspace/<topic>/literature/references.bib
- **Key papers** (top 5):
  1. [citation] — relevance: [why]
  2. ...
- **Research gaps identified**: [1-2 sentences]

## Experiment Results
- **Experiment Run**: [run_id] — [status]
- **Key metrics**: 
  - Metric A: [value] (baseline: [value])
  - Metric B: [value] (baseline: [value])
- **Results location**: [results path]

## Review History
| Iter | External Verdict | Internal Avg | Top Critical Issue | Round Dir |
|------|-----------------|--------------|-------------------|-----------|
| 1 | reject | 4.2/10 | [issue] | round_000 |
| 2 | weak reject | 5.8/10 | [issue] | round_001 |
| ... | ... | ... | ... | ... |

## Revision Roadmap (Next Iteration)
### Must Fix (from latest review synthesis)
1. [Issue] — [specific action]
2. [Issue] — [specific action]

### Should Fix
1. [Issue] — [specific action]

### Already Fixed
1. [Issue] — fixed in iteration N

## Complete File Map
```
workspace/<topic>/
├── literature/
│   ├── literature_review.md
│   ├── references.bib
│   └── gap_analysis.md
├── experiment/
│   ├── run_experiment.sh
│   ├── experiment.log
│   └── results/
├── paper/
│   ├── paper.tex
│   ├── references.bib
│   ├── figures/
│   │   ├── method_overview.pdf
│   │   ├── main_results.pdf
│   │   └── ablation.pdf
│   └── paper.pdf
├── review/
│   ├── round_000/
│   ├── round_001/
│   └── ...
└── pipeline_state/
    ├── state.json
    ├── resume_packet.md
    ├── verdict_history.md
    └── iteration_*_brief.md
```

## Pipeline-Specific Notes
- [Any special instructions for the next session]
- [Known quirks about this particular paper/project]
```

**Hard Reset Procedure**:
```
CONTEXT COMPRESSION — LEVEL 2 (HARD RESET)

1. Write the Resume Packet:
   - Read ALL current state files
   - Fill in the template completely
   - Save to pipeline_state/resume_packet.md

2. Verify all files are saved:
   - paper.tex is committed to disk
   - All review files exist
   - state.json is up to date

3. Prepare the new-session prompt:
   "You are continuing the chen-research-skills pipeline for paper:
    [topic]. Read pipeline_state/resume_packet.md for full context.
    Then continue from Stage 3 (WRITE/REVISE), addressing the issues
    listed in the Revision Roadmap. Use write-skill (revision mode)
    to revise the paper, then review-skill to re-evaluate."

4. End this session. The user (or automation) will start a new session
   with the prompt above.
```

## Context Health Monitoring

### Health Check (run at end of each Stage 4)

```python
def check_context_health():
    # Approximate token count (rough heuristic)
    estimated_tokens = estimate_current_context_tokens()
    context_limit = get_context_limit()  # model-specific
    
    usage_pct = estimated_tokens / context_limit
    
    if usage_pct > 0.85:
        return "CRITICAL"  # Must hard reset before next iteration
    elif usage_pct > 0.70:
        return "WARNING"   # Recommend hard reset
    elif usage_pct > 0.50:
        return "ELEVATED"  # Soft compression sufficient
    else:
        return "HEALTHY"   # Soft compression
    
def estimate_current_context_tokens():
    # Rough heuristic: count characters / 4
    # In practice, use the model's reported usage if available
    pass
```

### Degradation Signals

Watch for these signs that context is degrading:
- Model repeats content from earlier iterations verbatim
- Model forgets the research question or key findings
- Output sections become noticeably shorter/less detailed
- Model asks questions already answered earlier in the conversation
- Citation formatting errors increase (model "forgets" the venue style)

### Emergency Compression

If degradation is detected mid-iteration:
1. Immediately save all working files
2. Write a partial Resume Packet with current state
3. Ask user: "Context is degrading. Hard reset recommended. Continue in new session?"
4. If yes → Level 2 Hard Reset
5. If no → continue with warning, monitor closely

## Compression Frequency Rules

| Iteration | Default Action | Can Override? |
|-----------|---------------|---------------|
| 1 → 2 (first loop) | Level 1 (Soft) | Yes, user can request Level 2 |
| 2 → 3 | Level 1 (Soft) | Yes |
| 3 → 4 | Level 1 (Soft), health check | Yes |
| 4 → 5 | Level 1 (Soft), health check | Yes |
| 5 → 6 | Level 2 (Hard) recommended | Yes, user can stay at Level 1 |
| 6+ | Level 2 (Hard) mandatory | No — hard stop, must reset |
| Any with CRITICAL health | Level 2 (Hard) mandatory | No |
| Any with user request | As requested | — |

## What Survives Compression

### Level 1 (Soft) — Survives:
- All files on disk (papers, reviews, state)
- Resume packet (always kept up to date)
- Iteration brief for the just-completed iteration
- state.json

### Level 1 (Soft) — Lost:
- Full conversation history
- Intermediate reasoning
- Debugging context

### Level 2 (Hard) — Survives:
- All files on disk
- Resume packet (comprehensive)
- state.json

### Level 2 (Hard) — Lost:
- Everything in the conversation
- Claude Code session state
- Tool call history
