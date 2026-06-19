---
name: hypothesis-skill
description: "ReAct-based research hypothesis generation — multi-round literature search, PDF deep-reading, gap analysis, hypothesis scoring, and selection. Automates the ideation stage of the research pipeline. 4 modes: full, generate, evaluate, refine. Triggers on: generate hypothesis, research gap, find research idea, 研究假设, 生成假设, 找研究空白, research ideation."
metadata:
  version: "1.0"
  last_updated: "2026-06-01"
  depends_on: "search-skill"
---

# Hypothesis Skill — ReAct-Based Research Hypothese Generation

Uses a ReAct (Reasoning + Acting) loop to iteratively search literature, read paper PDFs deeply, identify research gaps, and generate scored, ranked, and verified research hypotheses. Each hypothesis is grounded in specific literature findings and assessed for novelty, feasibility, and impact.

## Quick Start

**Generate hypotheses from a topic:**
```
Generate research hypotheses for "Improving Few-Shot Learning through Adaptive Prompt Optimization"
```

**From an existing literature review:**
```
Analyze gaps in workspace/my_topic/literature/ and propose 5 research hypotheses
```

**Execution flow:**
1. Initial literature search → identify broad research area
2. Multi-round ReAct loop: search → read PDFs → identify gaps → refine hypotheses
3. Hypothesis scoring and ranking
4. Literature grounding verification
5. Output structured hypothesis report

---

## Trigger Conditions

### Trigger Keywords

**English**: generate hypothesis, research hypothesis, research gap, find research idea, propose research direction, research ideation, hypothesis generation, 研究假设, 生成假设, 找研究空白, 研究思路, 研究方向

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Literature search only (no hypothesis) | `search-skill` |
| Running experiments | `experiment-skill` |
| Full pipeline | `pipeline-skill` |

---

## Modes

| Mode | Trigger | What It Does |
|------|---------|-------------|
| `full` | "generate hypotheses", "research ideation" | Complete ReAct loop: search → read → gap-find → score → rank |
| `generate` | "propose hypotheses", "brainstorm ideas" | Generate hypotheses from existing literature (skip search phase) |
| `evaluate` | "evaluate this hypothesis", "score hypotheses" | Evaluate existing hypotheses against literature for novelty and feasibility |
| `refine` | "refine hypothesis", "improve research direction" | Take an existing hypothesis and refine it with additional literature evidence |

Default mode: `full`.

---

## ReAct Hypothesis Engine

The skill uses a ReAct (Reasoning + Acting) loop modeled after ChenResearch's `hypothesis_engine.py`:

```
┌─────────────────────────────────────────────────────────────┐
│                    ReAct Hypothesis Loop                     │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │  SEARCH  │───→│   READ   │───→│   GAP    │               │
│  │  papers  │    │  PDFs    │    │ ANALYSIS │               │
│  └──────────┘    └──────────┘    └────┬─────┘               │
│       ↑                                │                     │
│       │                                ↓                     │
│       │                          ┌──────────┐                │
│       │                          │ HYPOTHESIS│               │
│       │                          │GENERATION │               │
│       │                          └────┬─────┘               │
│       │                                │                     │
│       │                                ↓                     │
│       │                          ┌──────────┐                │
│       │                          │ SCORING  │                │
│       │                          │ & RANK   │                │
│       │                          └────┬─────┘               │
│       │                                │                     │
│       │                    ┌───────────┴──────────┐          │
│       │                    │   GAPS REMAIN?        │          │
│       │                    └──────┬─────────┬──────┘          │
│       │                           │ YES     │ NO              │
│       │                           ↓         ↓                 │
│       └─────────────────────── REFINE    OUTPUT               │
│         (new search queries                              │
│          targeting gaps)                                 │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1: Initial Literature Survey

1. Dispatch `search-skill` (lit-search mode) to gather 20-50 papers on the topic
2. Categorize papers by approach/method type
3. Build a research landscape map

### Phase 2: Deep Reading (ReAct Loop)

For each React round (max 3 rounds by default):

**Reasoning (R):**
1. Analyze current literature coverage
2. Identify specific research gaps with evidence from papers:
   - "Paper X claims Y but doesn't address Z"
   - "All existing methods assume A, but real-world scenarios have B"
   - "The SOTA on dataset D has plateaued at metric M for 2 years"
3. Formulate targeted search queries for gap verification

**Acting (A):**
1. Search for papers specifically addressing the identified gap
2. Download and read PDFs of the most relevant papers (top 5 per round)
3. Extract: methods used, limitations stated, future work suggested
4. Verify: is the gap truly unfilled? (Checking is critical — many "gaps" have been filled)

### Phase 3: Hypothesis Generation

For each verified gap, generate a structured hypothesis:

```json
{
  "id": "H-001",
  "hypothesis": "Adaptive prompt selection based on input complexity can improve few-shot performance by 15-20% without increasing model size",
  "gap": "Current prompt optimization methods use static prompts regardless of input difficulty",
  "evidence": [
    {"paper": "Liu et al. 2024", "finding": "Prompt quality varies 30% across different input types"},
    {"paper": "Zhang et al. 2023", "finding": "Simple inputs need less prompting than complex ones"}
  ],
  "proposed_method": "Complexity-gated prompt selector that routes inputs to different prompt templates",
  "expected_impact": "high",
  "feasibility": "medium",
  "novelty_score": 8.5,
  "feasibility_score": 7.0,
  "impact_score": 8.0,
  "composite_score": 7.8,
  "required_resources": ["Standard NLP benchmarks (GLUE, SuperGLUE)", "4× GPU for prompt tuning"],
  "potential_venues": ["ACL", "EMNLP", "NeurIPS"],
  "risks": [
    "Complexity metric may be task-dependent",
    "May not generalize beyond classification tasks"
  ]
}
```

### Phase 4: Scoring & Ranking

Each hypothesis is scored on three dimensions (1-10):

| Dimension | Criteria | Weight |
|-----------|----------|--------|
| **Novelty** | Is this truly new? Not just incremental? Verified gap? | 40% |
| **Feasibility** | Can this be tested with available resources? Data available? | 35% |
| **Impact** | If successful, how significant? Venue potential? Citation potential? | 25% |

Composite score = 0.4 × novelty + 0.35 × feasibility + 0.25 × impact

### Phase 5: Literature Grounding Verification

For each hypothesis above a score threshold (default 6.0):

1. Verify ≥3 specific papers support the gap claim
2. Check that no paper already proposes the same solution
3. Flag hypotheses with insufficient evidence
4. Cross-reference against the "Future Work" sections of key papers

---

## Workflow Detail

### Mode: full

1. **Confirm topic** — if topic is vague, use Socratic questioning to refine:
   - What specific sub-area?
   - What's the current SOTA bottleneck?
   - What resources (data, compute) are available?

2. **Initial search** → dispatch `search-skill` (lit-search mode, 30-50 papers)

3. **ReAct loop** (max 3 rounds):
   - R: Analyze coverage → identify gaps → formulate verification queries
   - A: Search for gap-filling papers → download PDFs → deep-read → verify
   - If gap is real: add to verified gaps list
   - If gap was filled: update literature map, continue searching

4. **Generate hypotheses** from verified gaps (target: 5-10 hypotheses)

5. **Score and rank** all hypotheses

6. **Output**: structured `hypothesis_report.md` + `hypotheses.json`

### Mode: generate

Skip the search phase. Takes existing literature (from `literature_review.md`) and directly generates hypotheses. Useful when literature search is already done.

### Mode: evaluate

Takes one or more existing hypotheses and evaluates them against the literature:
- Novelty check: has this been done?
- Feasibility check: resources required?
- Impact check: venue fit, significance estimate

### Mode: refine

Takes an existing hypothesis and improves it:
- Searches for additional supporting evidence
- Identifies potential weaknesses and countermeasures
- Suggests alternative approaches to test the same hypothesis

---

## Output Structure

```
<workspace>/hypothesis/
├── hypothesis_report.md      # Full report with all hypotheses
├── hypotheses.json           # Machine-readable hypothesis data
├── gap_analysis.md           # Verified research gaps
├── literature_map.md          # Research landscape categorization
├── search_trajectory.md       # ReAct loop trace (searches performed, papers read)
└── pdf_notes/                 # Notes from deep PDF reading
    └── <paper_key>.md
```

---

## Socratic Mode for Research Question Refinement

When a topic is vague or too broad, use Socratic questioning to narrow it down:

### Process

1. **Scope**: "This topic spans X sub-areas. Which are you most interested in?"
2. **Bottleneck**: "The current SOTA bottleneck in this area is [X]. Is that what you want to address?"
3. **Resources**: "This direction requires [dataset X, compute Y]. Do you have access?"
4. **Ambition**: "Are you aiming for incremental improvement (+2-3%) or a fundamentally new approach?"

### Output: Refined Research Question

```
Original: "Improving few-shot learning"
Refined:  "Adaptive prompt optimization for few-shot text classification
           that adjusts prompt complexity based on input difficulty,
           targeting 15-20% improvement on GLUE benchmark without
           increasing model parameters"
```

---

## Safety Rules

1. **Gap verification is mandatory** — never claim a gap without verifying it against recent literature
2. **No fabricated papers** — every citation must come from actual search results
3. **Feasibility honesty** — flag hypotheses that require unavailable resources
4. **Overclaim prevention** — "revolutionary" claims require proportionally strong evidence
5. **ReAct traceability** — log every search query and paper read for reproducibility
6. **Score transparency** — show the breakdown of how each hypothesis score was computed

## Configuration

```bash
# Hypothesis generation tuning
export HYPOTHESIS_MAX_REACT_ROUNDS=3    # Max ReAct iterations
export HYPOTHESIS_TOP_K_PDFS=5          # PDFs to deep-read per round
export HYPOTHESIS_MAX_PAPERS=50         # Max papers in initial survey
export HYPOTHESIS_MIN_SCORE=6.0         # Min composite score to include
export HYPOTHESIS_TARGET_COUNT=5        # Target number of hypotheses
```

## Reference Loading

- Read [react_protocol.md](references/react_protocol.md) for the detailed ReAct loop algorithm
- Read [scoring_rubric.md](references/scoring_rubric.md) for the hypothesis evaluation rubric
