---
name: pipeline-skill
description: "Full research pipeline orchestrator — coordinates search-skill, experiment-skill, write-skill, and review-skill into an automated iterate-until-accept workflow. Loops through research → experiment → write → review until paperreview.ai returns weak accept or better. Features mandatory context compression at the start of each iteration to keep Claude Code running indefinitely across many rounds. Tracks pipeline state for pause/resume. Triggers on: full pipeline, auto research, paper pipeline, 全自动科研, 完整流水线, end-to-end research, research-to-paper loop."
metadata:
  version: "1.0"
  last_updated: "2026-05-28"
  depends_on: "search-skill, experiment-skill, write-skill, review-skill"
---

# Pipeline Skill — Automated Iterate-Until-Accept Orchestrator

Orchestrates the four production skills into a closed-loop research pipeline. The pipeline iterates: **search → experiment → write → review**, checking after each review whether paperreview.ai returns `weak accept` or `accept`. If not, it feeds review feedback back to the write stage and iterates again — with context compression at the start of each iteration to prevent Claude Code context overflow.

## Quick Start

**Full pipeline from scratch:**
```
Start the full pipeline on "Improving Few-Shot Learning through Adaptive Prompt Optimization"
```

**Resume interrupted pipeline:**
```
Resume pipeline for fewshot_prompt_optimization
```

**Pipeline from existing research:**
```
Run the pipeline starting from write stage — I have research and experiment results in workspace/my_topic/
```

**Execution loop:**
```
Iteration 1: RESEARCH → EXPERIMENT → WRITE → REVIEW → verdict: reject
  ↓ (context compressed)
Iteration 2: RESEARCH(supplement) → EXPERIMENT(supplement) → WRITE(revise) → REVIEW → verdict: weak accept ✓ STOP
```
Note: On review failure, the pipeline does NOT simply revise text. It re-enters the full cycle: search for missing literature → design & run supplementary experiments → rewrite with new evidence → re-review.

---

## Trigger Conditions

### Trigger Keywords

**English**: full pipeline, auto research, paper pipeline, automated research, end-to-end paper, research-to-paper loop, iterate until accept, run the full pipeline, start pipeline, resume pipeline, pipeline status, 全自动科研, 完整流水线

**繁體中文**: 全自動科研, 完整流水線, 自動迭代, 自動寫論文, 跑完整流程, 啟動流水線

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Just need literature search | `search-skill` |
| Just need to run experiments | `experiment-skill` |
| Just need to write a paper | `write-skill` |
| Just need to review a paper | `review-skill` |
| Single-stage task of any kind | The specific skill for that task |

---

## Pipeline Stages (4 Core + Verdict Gate)

```
┌──────────────────────────────────────────────────────────────┐
│                      PIPELINE LOOP                            │
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                │
│  │ 1.RESEARCH│───→│2.EXPERIMENT│───→│ 3.WRITE  │               │
│  │ lit-search│    │  submit   │    │  full    │               │
│  └─────┬─────┘    └──────────┘    └─────┬────┘               │
│        ↑                                │                     │
│        │                                ↓                     │
│        │                          ┌──────────┐                │
│        │                          │ 4.REVIEW │                │
│        │                          │   full   │                │
│        │                          └─────┬────┘               │
│        │                                │                     │
│        │                    ┌───────────┴──────────┐          │
│        │                    │   VERDICT GATE        │          │
│        │                    │   weak accept / accept? │        │
│        │                    └──────┬─────────┬──────┘          │
│        │                           │ YES     │ NO              │
│        │                           ↓         ↓                 │
│        │                         DONE     ┌─────────┐          │
│        │                                  │ COMPRESS │          │
│        │                                  │ CONTEXT  │          │
│        │                                  └────┬────┘          │
│        │                                       │               │
│        └───────────────────────────────────────┘               │
│     (back to RESEARCH with review feedback — FULL re-iteration)│
└──────────────────────────────────────────────────────────────┘
```

**On review failure, the loop returns to Stage 1 (RESEARCH), not Stage 3 (WRITE).** The pipeline searches for literature missed by the reviewers' critiques, designs and runs supplementary experiments, rewrites with new evidence, and then re-reviews. Text-only revision is NOT sufficient to justify consuming paperreview.ai quota.

| Stage | Name | Skill Dispatched | Mode | Deliverables |
|-------|------|-----------------|------|-------------|
| 1 | RESEARCH | `search-skill` | lit-search or full | literature_review.md, references.bib, gap_analysis.md |
| 2 | EXPERIMENT | `experiment-skill` | submit (or manual skip) | Experiment code, execution run ID, results |
| 3 | WRITE | `write-skill` | full | paper.tex, figures/, paper.pdf |
| 4 | REVIEW | `review-skill` | full (dual: external + internal) | round_NNN/external.md, internal/*.md, synthesis.md, TODO.md |
| — | VERDICT GATE | orchestrator | — | Decision: STOP or re-enter at Stage 1 |

**Stage 2 (EXPERIMENT) can be skipped** if:
- User already has experiment results
- The paper is theoretical (no experiments needed)
- User explicitly requests "skip experiment stage"

**On re-iteration (review failure)**:
- Stage 1 (RESEARCH): targeted supplementary search — find papers the reviewers flagged as missing, expand literature coverage
- Stage 2 (EXPERIMENT): supplementary experiments — run additional baselines, ablations, or analyses requested by reviewers
- The `review/round_NNN/TODO.md` from review-skill drives what to search for and what experiments to run

---

## Iteration & Context Management

### The Problem

Claude Code has a finite context window. After 2-3 full pipeline iterations (each involving research, writing, review), the accumulated conversation history can overflow the context window, causing degraded performance or failures. Without active context management, the pipeline cannot sustain the 5-10+ iterations sometimes needed to reach `weak accept`.

### The Solution: Mandatory Context Compression

**At the start of each iteration (after Stage 4 REVIEW returns a non-accept verdict), the orchestrator MUST compress context before proceeding.**

#### Compression Protocol

Two levels, chosen based on how much context remains:

**Level 1 — Soft Compression (default for iteration 2-5):**
1. Summarize the previous iteration into a compact Iteration Brief:
   ```
   === Iteration N Summary ===
   Verdict: [reject / weak reject / borderline]
   Top 3 external reviewer issues:
     1. [issue] — [status: addressed / partially / not yet]
     2. [issue] — [status]
     3. [issue] — [status]
   Top 3 internal reviewer issues:
     1. [issue]
     2. [issue]
     3. [issue]
   Key changes made: [bullet list]
   Results this iteration: [experiment run status, key metrics]
   Files: [paths to all deliverables from this iteration]
   ```
2. Write this brief to `pipeline_state/iteration_N_brief.md`
3. Instruct Claude Code to start the next iteration by reading only the brief + the latest review files — NOT the full conversation history

**Level 2 — Hard Reset (for iteration 6+, or when context is visibly degraded):**
1. Write a comprehensive Pipeline Resume Packet to `pipeline_state/resume_packet.md`:
   ```markdown
   # Pipeline Resume Packet — Iteration N
   
   ## Research Summary
   - Topic: [topic]
   - Key papers: [top 5 citations]
   - Research gaps: [key gaps identified]
   
   ## Experiment Status
   - Latest experiment run: [run_id] ([status])
   - Key results: [metrics summary]
   - Results location: [results path]
   
   ## Paper Status
   - Current draft: [path to latest paper.tex]
   - Page count: [N]
   - Key claims: [list]
   
   ## Review History
   | Iteration | External Verdict | Internal Avg Score | Top Issue |
   |-----------|-----------------|-------------------|-----------|
   | 1 | reject | 4.2 | [issue] |
   | 2 | weak reject | 5.8 | [issue] |
   | ... | ... | ... | ... |
   
   ## Next Iteration Priorities
   1. [Priority 1 — from review synthesis]
   2. [Priority 2]
   3. [Priority 3]
   
   ## File Map
   - Literature: workspace/<topic>/literature/
   - Experiments: workspace/<topic>/experiment/
   - Paper: workspace/<topic>/paper/
   - Reviews: workspace/<topic>/review/
   - Pipeline state: pipeline_state/
   ```
2. Save all working files (ensure nothing is lost)
3. Start a fresh Claude Code session with the resume packet as the initial prompt
4. The fresh session reads the resume packet, loads files from disk, and continues from Stage 3 (WRITE)

#### When to Use Each Level

| Condition | Compression Level |
|-----------|------------------|
| Iteration 2-3 | Level 1 (Soft) |
| Iteration 4-5 | Level 1 (Soft), monitor for degradation |
| Iteration 6+ | Level 2 (Hard Reset) |
| Context visibly degraded (truncation, forgetting) | Level 2 immediately |
| User explicitly requests fresh start | Level 2 |
| After major direction change | Level 2 |

#### Context Health Monitoring

At the end of each iteration, the orchestrator should check:
- Approximate token usage relative to context window
- Whether the model is showing signs of context fatigue (repeating earlier content, forgetting recent instructions)
- If tokens used > 70% of context window → recommend Level 2 on next iteration

### Iteration Loop Rules

1. **First iteration (Iteration 1)** always runs Stages 1→2→3→4 fresh
2. **Subsequent iterations (on review failure)** re-enter at Stage 1 (RESEARCH) — search for literature missed in prior rounds, then Stage 2 (EXPERIMENT) for supplementary experiments, then Stage 3 (WRITE) to integrate new evidence and address all review criticisms, then Stage 4 (REVIEW)
3. **Why full re-iteration**: paperreview.ai has limited quota. Each resubmission must be a substantially improved paper with new experimental evidence and/or expanded literature coverage — not just reworded text
4. **Context compression is MANDATORY** before starting a new iteration — never skip
5. **Max iterations**: default 10 (configurable via `PIPELINE_MAX_ITERATIONS`). At iteration 10, accept best result and stop.
6. **Verdict tracking**: record every verdict + key metrics to `pipeline_state/verdict_history.md`

---

## Pipeline State Machine

```
START
  │
  ├─ has research? ──No──→ Stage 1: RESEARCH ──→ user confirm
  │                                                   │
  ├─ has experiments? ──No──→ Stage 2: EXPERIMENT ──→ user confirm
  │                                                   │
  ├────────────────────────→ Stage 3: WRITE ──→ user confirm
  │                                                   │
  └────────────────────────→ Stage 4: REVIEW (dual)
                                                      │
                                              ┌───────┴────────┐
                                              │  VERDICT GATE   │
                                              └───────┬────────┘
                                          accept / weak accept  │ reject / weak reject
                                                      │        │
                                                     DONE      │
                                                               │
                                              ┌────────────────┴────────────┐
                                              │  COMPRESS CONTEXT            │
                                              │  (mandatory before loop)     │
                                              └────────────────┬────────────┘
                                                               │
                                              ┌────────────────┴────────────┐
                                              │  Back to Stage 1 (RESEARCH)  │
                                              │  Full re-iteration: search   │
                                              │  missing lit → supplement    │
                                              │  experiments → rewrite →     │
                                              │  re-review                   │
                                              └─────────────────────────────┘
```

### Mid-Entry Detection

The orchestrator auto-detects where to start based on available materials:

| User Has | Start At |
|----------|----------|
| Nothing — just a topic idea | Stage 1 (RESEARCH) |
| Literature review already done | Stage 2 (EXPERIMENT) |
| Experiment results already available | Stage 3 (WRITE) |
| Paper draft already written | Stage 4 (REVIEW) |
| Review feedback already received | Stage 3 (REVISE) with feedback |
| Pipeline state file exists | Resume from saved state |

---

## Orchestrator Workflow

### Step 1: Intake & Detection

1. Determine the research topic
2. Scan for existing materials:
   - `workspace/<topic>/literature/` → research done?
   - `workspace/<topic>/experiment/` → experiments done?
   - `workspace/<topic>/paper/paper.tex` → paper drafted?
   - `workspace/<topic>/review/round_*/` → reviews done?
   - `pipeline_state/` → previous pipeline run?
3. Determine entry point
4. Present plan to user: "Starting from Stage X. Iterations will continue until weak accept (max N). Confirm?"

### Step 2: Stage Dispatch

The orchestrator does NOT do substantive work — it only dispatches skills:

```
Stage 1 → dispatch search-skill (lit-search or full mode)
Stage 2 → dispatch experiment-skill (submit mode) or skip
Stage 3 → dispatch write-skill (full mode, with research + experiment materials)
Stage 4 → dispatch review-skill (full mode, dual review)
```

Each dispatch:
1. Load the target skill's SKILL.md for reference
2. Pass relevant materials from previous stages
3. Inform user: "Starting Stage N: [name] using [skill] ([mode] mode)"
4. Monitor completion
5. Compile deliverables list
6. Present checkpoint → wait for user confirmation

### Step 3: Verdict Gate

After Stage 4 completes:
1. Read `review/round_<NNN>/external.md` → extract paperreview.ai verdict
2. Read `review/round_<NNN>/internal/merged_internal_review.md` → extract internal consensus score
3. Decision matrix:

| External Verdict | Internal Score | Pipeline Action |
|-----------------|----------------|-----------------|
| `accept` | any | **STOP — paper ready** |
| `weak accept` | any | **STOP — paper ready (minor polish optional)** |
| `borderline` | ≥ 6.0 | Offer choice: stop or one more iteration |
| `borderline` | < 6.0 | Continue to next iteration |
| `reject` / `weak reject` | any | Continue to next iteration |

4. If STOP: congratulate user, produce final summary, archive deliverables
5. If CONTINUE: generate TODO.md from review feedback → compress context → back to Stage 1 (RESEARCH) for supplementary literature search

### Step 4: Context Compression (MANDATORY before re-entering Stage 1)

Execute the compression protocol (see above). This is NOT optional — the orchestrator must refuse to continue without compression.

---

## State Tracking

Pipeline state is persisted to `pipeline_state/state.json`:

```json
{
  "topic": "Improving Few-Shot Learning through Adaptive Prompt Optimization",
  "topic_slug": "fewshot_prompt_optimization",
  "workspace": "workspace/fewshot_prompt_optimization",
  "current_stage": "review",
  "iteration": 2,
  "max_iterations": 10,
  "stages_completed": {
    "research": true,
    "experiment": true,
    "write": true,
    "review": false
  },
  "verdict_history": [
    {"iteration": 1, "external": "reject", "internal_avg": 4.2, "round": "round_000"},
    {"iteration": 2, "external": null, "internal_avg": null, "round": "round_001"}
  ],
  "experiment_runs": [
    {"iteration": 1, "run_id": "pt-abc123", "status": "SUCCEEDED"}
  ],
  "context_compressions": [
    {"iteration": 2, "level": "soft", "brief_path": "pipeline_state/iteration_1_brief.md"}
  ]
}
```

### Progress Dashboard

Users can say "pipeline status" at any time:

```
╔══════════════════════════════════════════════════════╗
║            Pipeline Status — Iteration 2/10          ║
╠══════════════════════════════════════════════════════╣
║ Topic: Few-Shot Prompt Optimization for NLP          ║
╠══════════════════════════════════════════════════════╣
║                                                       ║
║  Stage 1  RESEARCH        [✓] Done (34 papers)        ║
║  Stage 2  EXPERIMENT      [✓] Done (pt-abc123, OK)    ║
║  Stage 3  WRITE           [✓] Done (8 pages)          ║
║  Stage 4  REVIEW          [✓] Done (reject)           ║
║                                                       ║
║  ─── Iteration 2 ─────────────────────────────────   ║
║  Stage 3  REVISE          [..] In Progress            ║
║  Stage 4  REVIEW          [  ] Pending                ║
║                                                       ║
╠══════════════════════════════════════════════════════╣
║ Verdict History:                                      ║
║   Round 1: reject (ext) / 4.2/10 (int)                ║
║   Round 2: pending...                                 ║
╠══════════════════════════════════════════════════════╣
║ Context: Level 1 compressed after iteration 1         ║
║ Resume packet: pipeline_state/resume_packet.md        ║
╚══════════════════════════════════════════════════════╝
```

---

## Checkpoint System

After each stage, the orchestrator presents a checkpoint. Adapted from academic-pipeline's 3-tier system:

| Type | When | Behavior |
|------|------|----------|
| FULL | Stage 1 completion, Stage 3 completion, first iteration | Full deliverables + metrics + decision dashboard |
| SLIM | Stage 2 completion, Stage 4 → 3 transition (after 2+ iterations) | One-line status + auto-continue in 5s |
| MANDATORY | Verdict gate (after Stage 4), context compression | Cannot skip; requires explicit user input |

---

## Failure Recovery

| Scenario | Recovery |
|----------|----------|
| Experiment execution fails | `experiment-skill` diagnose mode → fix → rerun. Max 3 retries per iteration. |
| Write produces poor draft | Reviewer feedback will catch issues — feed back to Stage 3. |
| Review timeout (paperreview.ai > 2h) | Save token. User can check manually or skip external, use internal-only. |
| Context overflow mid-iteration | Emergency compression: save state, summarize, restart from current stage. |
| User interrupts | Save pipeline state to `pipeline_state/state.json`. Can resume later. |
| Max iterations reached without accept | Stop. Present best verdict, synthesis of remaining issues, recommendation. |
| All experiment retries exhausted | Skip experiment stage for this iteration. Write with available data. Flag missing experiments. |

---

## Output Directory Convention

```
<workspace>/                        # e.g., workspace/fewshot_prompt/
├── literature/                     # Stage 1 output
│   ├── literature_review.md
│   ├── references.bib
│   └── gap_analysis.md
├── experiment/                     # Stage 2 output
│   ├── run_experiment.sh
│   ├── experiment.log
│   └── results/
├── paper/                          # Stage 3 output
│   ├── paper.tex
│   ├── references.bib
│   ├── figures/
│   └── paper.pdf
├── review/                         # Stage 4 output
│   ├── round_000/
│   ├── round_001/
│   └── ...
└── pipeline_state/                 # Orchestrator state
    ├── state.json
    ├── verdict_history.md
    ├── resume_packet.md
    └── iteration_*_brief.md
```

---

## Configuration

```bash
# Pipeline tuning
export PIPELINE_MAX_ITERATIONS=10       # max review-revise loops
export PIPELINE_SKIP_EXPERIMENT=false   # skip Stage 2
export PIPELINE_VENUE=AAAI              # target venue for paper
export PIPELINE_CONTEXT_LEVEL=auto      # auto / soft / hard

# Skill-specific (inherited from shared/config.py)
export PAPERREVIEW_EMAIL=250010008@slai.edu.cn
export SEMANTIC_SCHOLAR_API_KEY=s2k-...
```

---

## Safety Rules

1. **Context compression is MANDATORY** — never skip it between iterations. The orchestrator must refuse to start a new iteration without compression.
2. **Never auto-accept** — the verdict gate requires actual paperreview.ai + internal review data. Don't skip review.
3. **State persistence** — save state after every stage completion. Pipeline must be resumable.
4. **User-in-the-loop** — MANDATORY checkpoints at verdict gate and context compression. User confirms before each new iteration.
5. **Experiment safety** — never execute experiments without user confirmation of the experiment script.
6. **Max iteration cap** — hard stop at PIPELINE_MAX_ITERATIONS. Don't loop indefinitely.
7. **Honest verdict reporting** — report the actual paperreview.ai verdict. Don't soften or reinterpret.

## Reference Loading

- Read [pipeline_state_machine.md](references/pipeline_state_machine.md) for complete state transition rules and edge cases
- Read [context_management.md](references/context_management.md) for detailed compression protocols and context health monitoring
