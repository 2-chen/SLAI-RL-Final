# Pipeline Skill — Usage Examples

## Example 1: Full Pipeline from Scratch

**User:**
```
Start the full pipeline on "Test-Time Adaptation for Medical Image Segmentation"
```

**Pipeline executes (Iteration 1):**

```
=== Pipeline Started ===
Topic: Test-Time Adaptation for Medical Image Segmentation
Entry: Stage 1 (RESEARCH) — no existing materials
Max iterations: 10
Target verdict: weak accept

━━━ Stage 1: RESEARCH ━━━
Dispatching search-skill (full mode)...

[search-skill] Searching arXiv + Semantic Scholar + OpenAlex...
[search-skill] 38 papers found. Generating analysis...

✓ Stage 1 complete
  - 38 papers in literature review
  - 5 research themes identified
  - 7 specific research gaps documented
  - Output: workspace/tta_medical/literature/

Proceed to Stage 2 (EXPERIMENT)? [Y/n]

━━━ Stage 2: EXPERIMENT ━━━
Dispatching experiment-skill (submit mode)...

[experiment-skill] GPU Detection: checking local GPUs...
[experiment-skill] No local GPUs → delegating to sco-skill for remote execution.
[experiment-skill] Job pt-abc123 submitted.
[experiment-skill] Monitoring... RUNNING → SUCCEEDED (12min)
[experiment-skill] Results: Dice 78.3% (baseline: 72.1%)

✓ Stage 2 complete
  - Experiment run: pt-abc123 (SUCCEEDED)
  - Key result: +6.2% Dice over baseline
  - Output: workspace/tta_medical/experiment/

Proceed to Stage 3 (WRITE)? [Y/n]

━━━ Stage 3: WRITE ━━━
Dispatching write-skill (full mode, AAAI 2026)...

[write-skill] Architecture → Draft → Figures → Polish → Compile
[write-skill] 8 pages (limit: 9). 3 figures. 2 tables. 0 citation errors.

✓ Stage 3 complete
  - paper.pdf compiled (8 pages)
  - Output: workspace/tta_medical/paper/

Proceed to Stage 4 (REVIEW)? [Y/n]

━━━ Stage 4: REVIEW ━━━
Dispatching review-skill (full mode)...

[review-skill] External: submitted to paperreview.ai (token: pt_xyz)
[review-skill] Internal: 5 reviewers running...
[review-skill] Internal complete: avg 4.2/10
[review-skill] External ready: verdict = reject

━━━ VERDICT GATE ━━━
External: reject
Internal: 4.2/10 (revise)
→ CONTINUE to iteration 2

Top issues:
  1. [Critical] No comparison to recent method X (2025)
  2. [Critical] Ablation study missing for key component
  3. [High] Writing clarity needs improvement in method section
  4. [Medium] Missing statistical significance tests
  5. [Medium] Only tested on one modality (MRI)

Proceed with context compression? [Y/n] (mandatory)
```

→ Level 1 compression → iteration brief saved → new session starts

```
=== Pipeline Iteration 2 ===
Context: Soft-compressed. Reading iteration_1_brief.md + review/round_000/

━━━ Stage 3: REVISE ━━━
Dispatching write-skill (revision mode)...
Addressing 5 issues from review...

[write-skill] Revised paper: added baseline X, expanded ablation, 
             improved method clarity, added significance tests.
[write-skill] 8.5 pages. Compiled.

━━━ Stage 4: REVIEW ━━━
Dispatching review-skill (full mode)...

[review-skill] External: verdict = weak accept ✓
[review-skill] Internal: avg 7.8/10

━━━ VERDICT GATE ━━━
External: weak accept ✓
Internal: 7.8/10 (accept)
→ STOP — PAPER READY

Pipeline complete after 2 iterations.
Final paper: workspace/tta_medical/paper/paper.pdf

Verdict history:
  Round 1: reject → Round 2: weak accept ✓
```

## Example 2: Mid-Entry from Existing Research

**User:**
```
Run the pipeline starting from write stage — I have research and experiment results 
in workspace/molecular_diffusion/
```

**Pipeline executes:**
```
=== Pipeline Started ===
Topic: Diffusion Models for Molecular Graph Generation
Entry: Stage 3 (WRITE) — literature + experiments found

Materials detected:
  ✓ Literature: workspace/molecular_diffusion/literature/ (42 papers)
  ✓ Experiments: workspace/molecular_diffusion/experiment/ (run pt-def456, SUCCEEDED)
  ✗ Paper: not found

Starting from Stage 3 (WRITE). Iterations: 3 → 4 → verdict gate → ...

━━━ Stage 3: WRITE ━━━
...
```

## Example 3: Resume Interrupted Pipeline

**User:**
```
Resume pipeline for tta_medical
```

**Pipeline executes:**
```
=== Resuming Pipeline ===
State loaded: pipeline_state/state.json
Topic: Test-Time Adaptation for Medical Image Segmentation
Current stage: REVIEW (iteration 1)
Last action: review-skill dispatched, external review pending

Checking external review status...
Token: pt_xyz → Polling... → Review ready! Verdict: reject

Resuming from Verdict Gate...
[continues normally]
```

## Example 4: Context Compression in Action

**User (iteration 5 just completed, verdict: weak reject):**
```
Continue to next iteration
```

**Pipeline responds:**
```
━━━ CONTEXT COMPRESSION (Level 1) ━━━

Context health: WARNING (estimated 72% used)

Compressing iteration 5:
  ✓ Writing iteration brief → pipeline_state/iteration_5_brief.md
  ✓ Updating resume packet → pipeline_state/resume_packet.md
  ✓ Saving pipeline state → pipeline_state/state.json

Compression complete.

To continue with iteration 6, I recommend a HARD RESET (Level 2) 
since this is iteration 6+. This means:
  1. I will write a comprehensive resume packet
  2. You will start a fresh Claude Code session
  3. The fresh session reads the resume packet and continues

Proceed with hard reset? [Y/n]
```

**User confirms:**
```
Yes — hard reset
```

**Pipeline:**
```
━━━ HARD RESET ━━━

Writing comprehensive resume packet...
  ✓ Research identity
  ✓ Paper state (8.5 pages, 3 claims)
  ✓ Literature foundation (top 5 papers)
  ✓ Experiment results (pt-abc123, +6.2% Dice)
  ✓ Review history (5 rounds)
  ✓ Revision roadmap for iteration 6
  ✓ Complete file map

Resume packet saved: pipeline_state/resume_packet.md

All files verified on disk. Ready for new session.

─── New Session Prompt ───
"You are continuing the chen-research-skills pipeline.
 Read pipeline_state/resume_packet.md for full context.
 Continue from Stage 3 (WRITE/REVISE), iteration 6.
 Address the issues in the Revision Roadmap."

Please start a new Claude Code session with this prompt.
This session will now exit.
```

## Example 5: Forced Stop at Max Iterations

**User (after 10 iterations):**
```
Check pipeline status
```

**Pipeline:**
```
╔══════════════════════════════════════════════════════╗
║            Pipeline Status — Iteration 10/10         ║
╠══════════════════════════════════════════════════════╣
║ Verdict History:                                      ║
║   R1: reject    R2: weak reject  R3: borderline      ║
║   R4: reject    R5: borderline   R6: weak reject     ║
║   R7: reject    R8: borderline   R9: borderline      ║
║   R10: borderline (ext) / 6.2/10 (int)               ║
╠══════════════════════════════════════════════════════╣
║ MAX ITERATIONS REACHED                                ║
║                                                        ║
║ Best result: Round 3/5/8/9/10 — borderline            ║
║ Remaining issues after 10 iterations:                  ║
║   1. [persistent] Method novelty questioned            ║
║   2. [persistent] Dataset scale concern                ║
║                                                        ║
║ Recommendation:                                        ║
║   - Accept current paper as "borderline" quality       ║
║   - Or: add more experiments (different dataset)       ║
║   - Or: reframe contribution more modestly             ║
║                                                        ║
║ Pipeline stopping. Final paper preserved at:           ║
║   workspace/my_topic/paper/paper.pdf                   ║
╚══════════════════════════════════════════════════════╝
```
