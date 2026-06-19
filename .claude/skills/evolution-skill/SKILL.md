---
name: evolution-skill
description: "Meta-skill for self-evolving chen-research-skills. Analyzes feedback from review-skill (external + internal reviews), pipeline-skill execution traces, and user feedback to identify recurring weaknesses, then proposes concrete file-level improvements. 5 modes: analyze → propose → apply → retrospective → watch. Targets all production skills (search, experiment, write, review, pipeline). Requires git repo for reversibility. Triggers on: evolve skill, improve skill, fix skill pattern, 技能进化, 自我改进."
metadata:
  version: "1.0"
  last_updated: "2026-05-28"
  depends_on: "git (for reversibility)"
---

# Evolution Skill — Self-Improving Meta-Skill for Chen-Research

A meta-skill that analyzes feedback from the chen-research-skills pipeline, identifies recurring weaknesses in individual skills, and proposes concrete file-level modifications. Operates as a **closed-loop self-improvement system** — the pipeline reviews papers, then evolution-skill reviews the skills that produced them.

## Quick Start

```
# After a pipeline review cycle completes:
Analyze the latest review feedback for skill improvement patterns

# Targeted fix:
The write-skill keeps producing papers with missing ablation tables. Propose a fix.

# Periodic maintenance:
Run a retrospective on all skills for the past week
```

---

## Trigger Conditions

### Auto-Trigger Signals

- **pipeline-skill** completes Stage 4 (REVIEW) → offer to analyze feedback for skill patterns
- **review-skill** synthesis.md shows consistent issues across ≥2 rounds → likely skill pattern
- User says: "the skill keeps making the same mistake"
- User says: "why doesn't [skill] handle X?"
- After 3+ pipeline iterations on the same paper → patterns almost certainly exist
- An experiment, review, or compilation fails with the same error ≥3 times

### Manual Trigger Keywords

**English**: evolve skill, improve skill, self-evolve, skill feedback, meta-learning, skill improvement, fix skill, update skill triggers, optimize agent, why does this keep happening, fix this pattern, 技能进化, 自我改进, 技能优化, 修正技能

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Fixing a one-off error (not a pattern) | Directly edit the file |
| Adding a new feature (not fixing a weakness) | Directly edit the file |
| First-time skill creation | Create new skill directory |
| Debugging a SCO job failure | `experiment-skill` diagnose mode |
| Fixing paper content (not skill behavior) | `write-skill` or manual edit |

---

## Modes

| Mode | Purpose | Output |
|------|---------|--------|
| `analyze` | Ingest reviewer feedback + error logs, identify patterns and root causes | Pattern Report |
| `propose` | Generate specific file-level diffs for each identified pattern | Evolution Proposal |
| `apply` | Execute approved proposals with git versioning | Committed changes |
| `retrospective` | Mine past pipeline runs for recurring failure signals | Retrospective Report |
| `watch` | Monitor skill usage over time, periodic improvement suggestions | Watch Report |
| `distill` | Extract external review insights and distill them into internal reviewer prompts | Distillation Report + updated reviewer prompts |

Default: `analyze → propose → human approve → apply`

---

## Architecture

```
Feedback Sources                     Evolution Engine               Target Skills
─────────────────────────────────────────────────────────────────────────────────
review-skill external.md ──┐
review-skill synthesis.md ─┤
review-skill internal/*.md ─┤
pipeline verdict_history ──┼──→ evolution_architect ──→ diff_engine ──→ Modified files
SCO job failure logs ──────┤         │                       │              │
User complaints ───────────┤         ↓                       ↓              ↓
Compilation error logs ────┘   Pattern Report         Evolution Proposal  git commit
         │                             │                       │
         │                             ↓                       │
         └─────────────────── distill mode ────────────────────┘
                              (external → internal
                               review improvement loop)
```

The **distill** mode creates a closed loop: external review catches gaps → distillation updates internal reviewer prompts → internal reviews become more comprehensive → fewer gaps in the next round. Over time, internal reviewers approach external review quality.

## Evolution Target Levels

Adapted for chen-research-skills' unique skill structure:

| Level | Target Files | chen-research Example |
|-------|-------------|----------------------|
| **L1: Trigger** | `SKILL.md` frontmatter | Add "跑实验" to experiment-skill triggers |
| **L2: Agent Instruction** | `agents/*.md` | write-agent missing instruction to always include ablation tables |
| **L3: Reference** | `references/*.md` | experiment_pattern.md missing OOM recovery pattern |
| **L4: Template** | `templates/*` | build.sh.j2 not handling missing bibtex case |
| **L5: Example** | `examples/*.md` | Add successful mid-entry pipeline example |
| **L6: Routing/Config** | `SKILL.md` routing rules, `shared/config.py` | Add new SCO worker spec default |
| **L7: Shared Library** | `shared/*.py` | search_papers.py missing rate-limit handling for new API |

---

## Chen-Research-Specific Feedback Sources

### Source 1: Review Feedback (Highest Signal)

The richest source. Extract from every completed review round:

```
workspace/<topic>/review/round_NNN/
├── external.md              → paperreview.ai criticisms
├── internal/
│   ├── methodology_expert.md → method/experiment gaps
│   ├── experiments_reviewer.md → missing baselines, weak ablations
│   ├── clarity_writing_reviewer.md → writing quality issues
│   ├── related_work_reviewer.md → literature coverage gaps
│   └── devils_advocate.md     → fundamental flaws, overclaims
└── synthesis.md             → consolidated issues with priorities
```

**How to read**: Each reviewer criticism can be traced to a skill weakness:
- "Missing comparison to method X" → search-skill didn't find this paper, OR write-skill didn't include the baseline
- "Ablation study incomplete" → write-skill agent didn't enforce ablation coverage
- "References contain broken DOIs" → search-skill source verification gap
- "Figure text too small" → write-skill figure rcParams misconfigured

### Source 2: Pipeline Execution Traces

From `pipeline_state/`:
```
pipeline_state/
├── state.json              → stage transitions, error counts, skipped stages
├── verdict_history.md      → verdict trend across iterations
└── iteration_*_brief.md    → per-iteration issue summaries
```

**How to read**: 
- Verdict stuck at "reject" for 5+ iterations → fundamental skill gap, not paper-specific
- Stage 2 (experiment) skipped 3 times due to failures → experiment-skill reliability issue
- Context compression triggered at iteration 3 instead of 5 → write-skill producing too much output

### Source 3: Compilation & Build Errors

From `write-skill` compilation:
```
paper.log → Overfull hbox warnings, undefined citations, missing packages
build.sh output → pdflatex errors, bibtex failures
```

**How to read**:
- Repeated "Overfull hbox" on equations → write-skill not wrapping equations properly
- "Citation undefined" for papers in references.bib → write-skill citation format mismatch
- Compilation fails on specific venue → ccf_a_templates.md has incorrect package list

### Source 4: SCO Job Failures

From `experiment-skill` execution:
```
sco_logs.txt → OOM errors, missing dependencies, path errors
sco_runner.py output → submission failures, timeout errors
```

**How to read**:
- Repeated OOM on same worker spec → experiment_pattern.md needs smaller default batch size guidance
- "sco CLI not found" → experiment-skill should check PATH in pre-submit validation
- AFS path errors → sco_config.md has wrong mount point

### Source 5: User Direct Feedback

User statements captured during pipeline execution:
- "The paper is too long, always 2 pages over limit" → write-skill word budget issue
- "It never finds papers from [specific venue]" → search-skill API coverage gap
- "The reviews take too long" → review-skill polling interval or parallelism issue

---

## Workflow Detail

### Mode: analyze

1. **Collect feedback**: Read the latest iteration's review files + pipeline state
2. **Extract criticisms**: Every reviewer issue, error log entry, compilation warning
3. **Classify by severity**:
   - **Critical**: Blocks correct output (paper won't compile, experiment won't submit)
   - **Major**: Degrades quality consistently (missing ablation, poor figure quality)
   - **Minor**: Cosmetic or rare (occasional formatting drift)
4. **Group into patterns**: A pattern exists when same issue appears from ≥2 independent sources OR ≥3 times across sessions
5. **Root-cause classification**: Map each pattern to a target level (L1-L7) and specific skill
6. **Output Pattern Report**:

```markdown
# Pattern Report — 2026-05-28
## Sources Analyzed
- review/round_002/ (external + internal, 5 reviewers)
- review/round_001/ (external + internal)
- pipeline_state/verdict_history.md

## Patterns Found: 3

### EVO-20260528-001: Write-skill consistently missing ablation tables
- **Level**: L2 (Agent Instruction)
- **Target**: write-skill/agents/write-agent.md
- **Evidence**:
  - Round 1, Experiments Reviewer: "No ablation study provided" (score 4/10)
  - Round 2, Experiments Reviewer: "Ablation still missing" (score 5/10)
  - External review round 2: "Need component-wise analysis"
- **Frequency**: 3/3 reviews flag this
- **Root Cause**: write-agent.md section on experiments mentions ablation but doesn't require it
- **Proposed Fix**: Add "REQUIRED: ablation table showing per-component contribution" to the experiments section in write-agent.md
- **Expected Impact**: Eliminates most common reviewer criticism
- **Risk**: LOW — additive change only

### EVO-20260528-002: Research-skill missing papers from venue X
...

### EVO-20260528-003: Review-skill internal reviewer timeout on long papers
...
```

### Mode: propose

For each pattern in the Pattern Report, generate a concrete file-level diff:

```markdown
# Evolution Proposal

## Proposal 1: EVO-20260528-001
**Target**: write-skill/agents/write-agent.md
**Change**: Add ablation requirement to experiments section

### Diff Preview
--- a/write-skill/agents/write-agent.md
+++ b/write-skill/agents/write-agent.md
@@ -XX,Y +XX,Z @@
 ### Experiments Section
--Include main results table + qualitative examples
+-Include main results table + ablation study table + qualitative examples
+-Ablation table is REQUIRED: show per-component contribution to primary metric

### Validation Checklist
- [ ] write-agent.md still compiles as valid markdown
- [ ] No contradiction with existing instructions
- [ ] Change is additive (doesn't remove existing guidance)
```

### Mode: apply

1. Verify target skill is in the git repo
2. Show `git diff` preview
3. Wait for explicit user approval
4. Apply the change
5. Create a git commit with descriptive message:
   ```
   evolution: require ablation tables in write-skill experiments section
   
   Evidence: flagged by internal experiments reviewer in 3/3 review rounds.
   Root cause: write-agent.md mentioned ablation but didn't require it.
   
   Co-Authored-By: Evolution Skill <evolution@chen-research-skills>
   ```
6. Report: "Change applied. Commit: abc1234. To revert: git revert abc1234."

### Mode: retrospective

1. Scan `pipeline_state/` across all projects in `workspace/`
2. Read verdict_history.md from each project
3. Identify recurring issues that persist across different papers
4. Cross-reference: same reviewer complaint appearing in different projects → skill issue, not paper issue
5. Output Retrospective Report:

```markdown
# Retrospective Report — Week of 2026-05-22 to 2026-05-28

## Projects Analyzed: 3
- fewshot_prompt (4 iterations, final: borderline)
- tta_medical (2 iterations, final: weak accept)
- molecular_diffusion (6 iterations, final: weak reject)

## Cross-Project Patterns

### Pattern 1: Ablation completeness
- fewshot_prompt: flagged in 3/4 rounds
- tta_medical: flagged in 1/2 rounds
- molecular_diffusion: flagged in 5/6 rounds
→ CONFIDENCE: HIGH. This is a write-skill issue, not paper-specific.

### Pattern 2: Internal reviewer timeout
- fewshot_prompt: Clarity reviewer timed out (round 3)
- molecular_diffusion: Related Work reviewer timed out (round 4, 5)
→ CONFIDENCE: MEDIUM. May be paper-length dependent.

## Recommendations
1. [HIGH] Fix write-skill ablation requirement (affects 3/3 projects)
2. [MEDIUM] Investigate internal reviewer timeout on long papers
3. [LOW] Add more CCF-A venue templates (user requested KDD twice)
```

### Mode: watch

Continuous monitoring mode for long-running pipeline sessions:

1. After each pipeline iteration completes, append to `evolution_state/watch_log.md`
2. Track per-iteration: external verdict, internal scores, top issues, skill errors
3. Every 3 iterations, produce a Watch Report summarizing trends
4. Alert if: same issue appears 3+ times, scores plateau, or new failure pattern emerges

### Mode: distill — External Review Distillation

The most powerful self-improvement mechanism in evolution-skill. External reviewers (paperreview.ai) are trained on real conference review data and often catch issues that internal reviewers miss completely. This mode extracts those insights and uses them to permanently improve the internal reviewer personas.

#### Why This Matters

Internal reviewers (5 personas defined in `internal_review.py`) have fixed prompts. They can only evaluate papers through the lenses they were programmed with. External reviewers, by contrast, bring novel review angles learned from real peer review data. Over multiple review rounds, patterns emerge: external review consistently flags issues in areas where internal reviewers are silent.

The distillation process closes this gap — it learns from external review feedback and bakes those insights into the internal reviewer prompts, progressively improving internal review quality.

#### Distillation Protocol

**Phase 1: Gap Analysis**

For each review round, compare external and internal reviews side by side:

```markdown
## Gap Analysis — Round NNN

### Issue: External reviewer flagged "missing theoretical convergence proof"
- **External**: "The paper lacks formal convergence guarantees for the proposed algorithm" (Score impact: -2)
- **Internal**: No reviewer mentioned this
- **Mapping**: Which internal reviewer SHOULD have caught this? → Methodology Expert
- **Gap type**: Missing review dimension — the internal Methodology Expert prompt has no instruction about checking convergence proofs

### Issue: External reviewer flagged "unfair baseline comparison"
- **External**: "Baseline X was tuned on validation set while proposed method was tuned on test set"
- **Internal**: No reviewer mentioned this
- **Mapping**: Experiments Reviewer SHOULD have caught this
- **Gap type**: Missing review dimension — the internal Experiments Reviewer prompt has no fairness-of-comparison check
```

**Phase 2: Pattern Accumulation**

Track gaps across rounds. A gap that appears ≥2 times across different papers is a **persistent gap** — the internal reviewer prompt is structurally deficient:

```
Distillation State (persisted to evolution_state/distillation_registry.md):

Methodology Expert gaps:
- [2×] Convergence proof / theoretical guarantees check
- [1×] Notation consistency with prior work

Experiments Reviewer gaps:
- [3×] Fairness of baseline comparison (tuning protocol, data splits)
- [2×] Statistical significance testing beyond just reporting mean±std
- [1×] Compute cost normalization (FLOPs, GPU-hours)

Clarity & Writing Reviewer gaps:
- [1×] Citation format consistency check

Related Work Reviewer gaps:
- [2×] Distinction from concurrent work (not just published work)

Devil's Advocate gaps:
- [2×] "What if the improvement comes from a confound, not the proposed method?" reasoning
```

**Phase 3: Prompt Distillation**

For each persistent gap (≥2 occurrences), update the corresponding internal reviewer's prompt in `internal_review.py:REVIEWER_POOL`:

| Gap | Internal Reviewer | Prompt Addition |
|-----|------------------|-----------------|
| Convergence proof check | Methodology Expert | "Check whether the paper provides formal theoretical guarantees (convergence, optimality, generalization bound). If the method lacks such guarantees and claims theoretical novelty, flag this as a major weakness." |
| Fair baseline comparison | Experiments Reviewer | "Verify that all methods in the comparison were tuned under the same protocol. Check whether the proposed method had access to test-set information during tuning while baselines did not. Flag any asymmetry." |
| Statistical significance | Experiments Reviewer | "Check whether results include statistical significance tests (t-test, bootstrap, Wilcoxon). Reporting only mean±std without significance is insufficient for claiming improvement." |

**Phase 4: Apply & Validate**

1. Generate an Evolution Proposal with the exact diff for `shared/internal_review.py`
2. Show the proposed prompt changes + evidence (review quotes showing the gap)
3. Require human approval before modifying reviewer prompts
4. After applying, the improved internal reviewer prompts activate on the next review round
5. Track: does the next internal review catch issues that were previously external-only?

#### Distillation Output

```
evolution_state/
├── distillation_registry.md    # Running log of gaps per reviewer persona
├── distill_round_NNN.md        # Per-round gap analysis
└── prompt_diffs/               # Approved prompt modifications
    ├── EVO-20260528-D01.md     # Methodology Expert: convergence proof check
    └── EVO-20260528-D02.md     # Experiments Reviewer: fairness check
```

#### Safety Constraints

1. **Evidence bar**: Only distill a gap if it appears in ≥2 independent external reviews across different papers
2. **Human-in-the-loop**: Prompt modifications MUST be approved before applying — reviewer prompts directly affect paper quality assessment
3. **Additive only**: New review dimensions can only be ADDED to prompts, never removed (removing dimensions could degrade review quality)
4. **Preserve persona**: New dimensions must align with the reviewer's persona — don't add experiment checks to the Clarity reviewer
5. **One dimension per change**: Each prompt modification adds exactly one new review dimension, for clean reversibility
6. **Track provenance**: Every prompt modification records which external reviews motivated it, so accuracy can be audited

---

## Skills-Specific Pattern Catalog

### search-skill Patterns

| Symptom | Root Cause | Fix Level |
|---------|-----------|-----------|
| Key papers from venue X consistently missed | API coverage gap | L3: add API config |
| Search returns <5 papers on reasonable query | Query formulation too strict | L2: agent needs query expansion |
| Duplicates not properly merged | Title normalization too aggressive | L7: fix shared/search_papers.py |
| Papers from 2026 not appearing | Year filter too restrictive | L3: update search_strategies.md |
| Chinese queries return no results | No Chinese API support documented | L3: add API language guidance |
| PDF download consistently fails for venue X | Paywall or anti-bot protection | L3: update pdf_download.md |
| GitHub search returns 0 results for most papers | Query construction too narrow | L2: broaden GitHub search logic |
| Dataset download links 404 | Platform moved or deprecated | L3: update data_resources.md |

### experiment-skill Patterns

| Symptom | Root Cause | Fix Level |
|-----------|---------|-----------|
| SCO submit fails: "worker spec not found" | Outdated spec in sco_config.md | L3: update spec list |
| Job OOM on first run every time | Default batch size too large | L3: add OOM guidance to experiment_pattern.md |
| AFS path not writable | Mount configuration wrong | L3/L6: fix sco_config.md or config.py |
| "sco CLI not found" on fresh session | PATH check missing | L2: agent needs pre-flight check |
| Results not collected after job succeeds | No auto-collect in submit flow | L2: add post-success log grab |

### write-skill Patterns

| Symptom | Root Cause | Fix Level |
|-----------|---------|-----------|
| Paper always 1-2 pages over limit | Word budget per section not enforced | L2: agent needs budget tracking |
| Ablation table missing | Agent doesn't require it | L2: add REQUIRED annotation |
| Figure text too small (7pt → 5pt) | rcParams drift | L2/L4: hardcode font size in agent + template |
| AI-writing markers in every draft | Polish step too lenient | L2: strengthen polish instructions |
| Compilation fails on specific venue | Template package list wrong | L3: fix ccf_a_templates.md |
| References section: "[?]" markers | Citation not in .bib, or format mismatch | L2: add citation pre-check step |
| method_overview.pdf too complex | Agent not following figure contract | L2: enforce contract-before-code |

### review-skill Patterns

| Symptom | Root Cause | Fix Level |
|-----------|---------|-----------|
| paperreview.ai timeout (50%+ of submissions) | Poll start too early or interval too long | L6: adjust poll params |
| Internal reviewer consistently fails on long papers | Paper text truncation at 20000 chars | L7: fix internal_review.py |
| Synthesis.md missing external-internal comparison | Agent skipping comparison step | L2: add REQUIRED comparison |
| Round numbering collision | concurrent runs | L2: add lock or timestamp |
| Token lost (not saved to token.txt) | Agent error path doesn't save | L2: add save-before-submit rule |

### pipeline-skill Patterns

| Symptom | Root Cause | Fix Level |
|-----------|---------|-----------|
| Context overflow on iteration 4 (not 6 as designed) | write-skill producing verbose output | L2: add verbosity check before iteration start |
| state.json corrupted on interruption | No atomic write | L7: use temp file + rename |
| Verdict gate lets "borderline" through without user confirm | Decision matrix not applied | L2: fix verdict gate logic in agent |
| Resume fails because file paths changed | Absolute paths in state.json | L2: use workspace-relative paths |
| Compression brief too large (>5KB) | Too much detail preserved | L2: enforce brief size limit |

---

## Integration with Pipeline

```
pipeline-skill
  │
  ├── Stage 4: REVIEW complete
  │     │
  │     └──→ [AUTO-OFFER] "Review complete. Analyze feedback for skill patterns?"
  │           │
  │           ├── User: yes → evolution-skill (analyze mode)
  │           │     │
  │           │     ├── Pattern Report generated
  │           │     ├── User: "propose fixes" → Evolution Proposals with diffs
  │           │     └── User: "apply" → git commit → skills improved
  │           │
  │           └── User: no → continue pipeline
  │
  └── Pipeline ends (accept or max iterations)
        │
        └──→ [AUTO-OFFER] "Run retrospective on this pipeline run?"
              │
              └── evolution-skill (retrospective mode)
                    → Cross-reference with other projects
                    → Recommendations for skill improvement
```

---

## Safety Protocol

1. **Git required** — all target skills must be in the git repo (`/data/ResearchSkills/chen-research-skills/.git`). Refuse to apply changes otherwise.
2. **Diff preview mandatory** — `git diff` shown before any write in apply mode.
3. **Human approval required** — `apply` mode never auto-executes.
4. **One commit per change** — each fix is an independent, revertible commit.
5. **Evidence citation** — every change must cite specific reviewer feedback, error logs, or user complaints.
6. **validation_agent pre-screens** — auto-rejects:
   - Changes removing safety constraints
   - Changes contradicting existing agent instructions without explanation
   - Empty or malformed diffs
   - Changes touching >3 agent files in a single proposal
   - Changes to `shared/` Python code without test validation
7. **Dry-run default** — `propose` mode shows what *would* change without applying.

---

## Output Directory

```
evolution_state/
├── pattern_reports/          # analyze mode output
│   └── PR_2026-05-28_001.md
├── proposals/                # propose mode output
│   └── EVO-20260528-001.md
├── retrospectives/           # retrospective mode output
│   └── RETRO_2026-05-28.md
├── watch_log.md              # watch mode continuous log
├── applied_history.md        # Record of all applied changes
├── distillation_registry.md  # Running log of gaps per reviewer persona
├── distill_round_NNN/        # Per-round gap analysis
│   └── gap_analysis.md
└── prompt_diffs/             # Approved internal reviewer prompt modifications
    └── EVO-20260528-D01.md
```

## Reference Loading

- Read [evolution_patterns.md](references/evolution_patterns.md) for the complete chen-research-specific pattern catalog with detailed symptoms and canonical fixes
