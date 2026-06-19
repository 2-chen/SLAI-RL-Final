# Evolution Skill — Usage Examples

## Example 1: Analyze After Pipeline Review

**Context**: pipeline-skill just completed iteration 3. Review round 003 shows the same issues as rounds 001 and 002.

**User:**
```
Analyze the latest review feedback for skill improvement patterns
```

**Skill executes (analyze mode):**
```
Reading feedback sources:
  ✓ review/round_003/external.md (verdict: weak reject)
  ✓ review/round_003/internal/ (5 reviewers)
  ✓ review/round_002/synthesis.md
  ✓ review/round_001/synthesis.md
  ✓ pipeline_state/verdict_history.md

Extracting criticisms... 23 total across 3 rounds
Grouping into patterns... 3 patterns found

━━━ Pattern Report ━━━

EVO-20260528-001: Write-skill missing ablation tables
  Skill: write-skill | Level: L2 | Confidence: HIGH
  Evidence:
  - Round 1, Experiments Reviewer: "No ablation study" (score 4/10)
  - Round 2, Experiments Reviewer: "Ablation still missing" (score 5/10)
  - Round 3, External: "Need component-wise analysis of contributions"
  - Round 3, Experiments Reviewer: "Ablation missing for 3rd consecutive round" (score 4/10)
  Target: write-skill/agents/write-agent.md
  Proposed: Add "REQUIRED" annotation to ablation section in experiments instructions

EVO-20260528-002: Figure text consistently too small
  Skill: write-skill | Level: L2 | Confidence: HIGH
  Evidence:
  - Round 1, Clarity Reviewer: "Figure 2 labels barely legible"
  - Round 2, Clarity Reviewer: "Figure text still too small (appears ~5pt)"
  - Round 3, Clarity Reviewer: "Font size inconsistent across figures"
  Target: write-skill/agents/write-agent.md
  Proposed: Hardcode minimum 7pt font size in figure rcParams + add pre-export check

EVO-20260528-003: Internal reviewer timeout on round 3
  Skill: review-skill | Level: L7 | Confidence: MEDIUM
  Evidence:
  - Round 3 only: Clarity & Writing Reviewer timed out after 600s
  - Paper length: 9 pages with 4 figures (longer than rounds 1-2)
  Target: shared/internal_review.py
  Proposed: Increase paper_text truncation from 20000 to 30000 chars

Proceed to propose mode? [Y/n]
```

## Example 2: Generate Evolution Proposals

**User:**
```
Propose fixes for EVO-20260528-001 and EVO-20260528-002
```

**Skill executes (propose mode):**
```
━━━ Evolution Proposals ━━━

Proposal 1/2: EVO-20260528-001
  Target: write-skill/agents/write-agent.md
  Validation: ⚠ APPROVED (additive change, low risk)

  --- a/write-skill/agents/write-agent.md
  +++ b/write-skill/agents/write-agent.md
  @@ experiments section:
  -Include main results table + qualitative examples
  +Include main results table + ablation study table + qualitative examples
  +
  +Ablation table is REQUIRED for all method papers:
  +- Show per-component contribution to primary metric
  +- Format: booktabs style, bold best, sorted by contribution impact
  +- If ablation is genuinely impossible (no components to ablate),
  +  explain why in a footnote

  Validation checklist:
  ✓ Additive change only
  ✓ No contradiction with existing instructions
  ✓ Evidence: 3/3 review rounds flagged this

Proposal 2/2: EVO-20260528-002
  Target: write-skill/agents/write-agent.md
  Validation: ⚠ APPROVED (additive, hardcoded minimum)

  --- a/write-skill/agents/write-agent.md
  +++ b/write-skill/agents/write-agent.md
  @@ figure section, after rcParams block:
  +HARD MINIMUM: All figure text (labels, ticks, legends, annotations)
  +must be ≥7pt in the exported PDF. Before finalizing any figure:
  +  1. Check all font sizes in the matplotlib code
  +  2. Render and visually verify text is readable at print size
  +  3. Reject figures with text <7pt — regenerate at larger size

Apply these proposals? [Y/n]
```

## Example 3: Apply with Git Tracking

**User:**
```
Apply both proposals
```

**Skill executes (apply mode):**
```
Checking git status...
  ✓ /data/ResearchSkills/chen-research-skills is a git repo
  ✓ Working tree clean (no uncommitted changes)

Applying EVO-20260528-001...
  ✓ write-skill/agents/write-agent.md updated
  ✓ git add write-skill/agents/write-agent.md

Applying EVO-20260528-002...
  ✓ write-skill/agents/write-agent.md updated
  ✓ git add write-skill/agents/write-agent.md

Creating commit...
  [main abc1234] evolution: require ablation tables + enforce figure font minimums

  Evidence: Ablation missing flagged by experiments reviewer in 3/3 rounds.
           Figure text too small flagged by clarity reviewer in 3/3 rounds.
  Files: write-skill/agents/write-agent.md (+8 lines)

  2 files changed, 8 insertions(+)

To revert: git revert abc1234
```

## Example 4: Retrospective Across Projects

**User:**
```
Run a retrospective on all skills for the past week
```

**Skill executes (retrospective mode):**
```
Scanning workspace/ for pipeline projects...
  ✓ fewshot_prompt (4 iterations, final: borderline)
  ✓ tta_medical (2 iterations, final: weak accept)
  ✓ molecular_diffusion (6 iterations, final: weak reject)

Scanning pipeline_state/ for patterns...
Cross-referencing review complaints across projects...

━━━ Retrospective Report — Week of 2026-05-22 to 2026-05-28 ━━━

Projects analyzed: 3 | Total iterations: 12 | Total review rounds: 12

Cross-Project Patterns:

1. [HIGH] Ablation tables missing
   - fewshot_prompt: flagged 3/4 rounds
   - tta_medical: flagged 1/2 rounds
   - molecular_diffusion: flagged 5/6 rounds
   → Affects 3/3 projects. Write-skill instruction gap.

2. [HIGH] Paper over page limit on first draft
   - fewshot_prompt: 10 pages (AAAI limit: 9)
   - tta_medical: 9.5 pages (AAAI limit: 9)
   - molecular_diffusion: 11 pages (AAAI limit: 9)
   → Write-skill word budget not enforced. Affects 3/3 projects.

3. [MEDIUM] Internal reviewer timeout
   - fewshot_prompt: Clarity reviewer timed out (round 3)
   - molecular_diffusion: Related Work reviewer timed out (rounds 4,5)
   → Affects 2/3 projects. May be paper-length dependent.

4. [LOW] Experiment stage skipped due to SCO failures
   - molecular_diffusion: SCO failed 3 times (iteration 4)
   → Affects 1/3 projects. May be cluster-specific.

Recommendations:
  [HIGH] Apply EVO-20260528-001 (ablation requirement) — affects all projects
  [HIGH] Add word budget enforcement to write-skill (new pattern)
  [MEDIUM] Investigate internal_review.py timeout on papers >8 pages
  [LOW] Monitor SCO job reliability; may be transient cluster issue
```

## Example 5: Continuous Watch Mode

**User:**
```
Watch skills during this pipeline run and report every 3 iterations
```

**Skill executes (watch mode):**
```
Watch mode active. Monitoring pipeline iterations...

Iteration 1 complete — baseline established.
Iteration 2 complete — no new patterns.
Iteration 3 complete — generating Watch Report...

━━━ Watch Report — Iterations 1-3 ━━━

Trend: Scores improving (4.2 → 5.8 → 6.1)
New patterns: None
Persistent issues:
  - Ablation table missing (all 3 rounds) → existing pattern, fix pending
  - Figure text size (rounds 1-2, fixed in round 3)

Alert: Internal Clarity reviewer has flagged "AI-writing markers" in 
all 3 rounds. This may indicate a new pattern. Monitor for 2 more rounds.

Continuing watch...
```

## Example 6: Validation Agent Rejects a Proposal

**Context**: Someone proposes removing the "never fabricate results" rule to "speed up drafting."

**Skill executes (propose mode → validation):**
```
Proposal: EVO-20260528-099
  Target: write-skill/agents/write-agent.md
  Change: Remove "Never fabricate results" constraint
  
Validation: ⚠ REJECTED
  Rule violated: Safety Violation
  Detail: Proposal removes a core safety constraint.
  The rule "Never fabricate results, methods, references, or novelty"
  is a non-negotiable quality guarantee.

Proposal blocked. Not forwarded for human review.
```
