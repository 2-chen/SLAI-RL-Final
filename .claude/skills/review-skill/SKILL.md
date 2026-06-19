---
name: review-skill
description: "Paper review orchestrator — submits papers to paperreview.ai for external review and runs internal multi-perspective review (5 reviewers) in parallel. Organizes all review results into markdown by round and source (internal/external). 6 modes: full, external-only, internal-only, poll, synthesis, status. Triggers on: review paper, submit for review, get reviews, 审稿, 提交审稿, 论文审稿, check review status, collect reviews."
metadata:
  version: "1.0"
  last_updated: "2026-05-28"
---

# Review Skill — Dual-Source Paper Review Orchestrator

Submits papers to paperreview.ai for external AI review while simultaneously running internal multi-perspective review (5 personas). Organizes all review outputs into a round-based directory structure with clear internal/external separation.

## Quick Start

**Full dual review:**
```
Review this paper: workspace/my_project/paper/paper.pdf
```

**Result:**
```
workspace/my_project/review/
└── round_000/
    ├── README.md              # Round summary with scores + verdicts
    ├── external.md            # paperreview.ai review
    ├── internal/
    │   ├── methodology_expert.md
    │   ├── experiments_reviewer.md
    │   ├── clarity_writing_reviewer.md
    │   ├── related_work_reviewer.md
    │   ├── devils_advocate.md
    │   └── merged_internal_review.md
    └── synthesis.md           # Cross-source comparison + revision roadmap
```

## Trigger Conditions

### Trigger Keywords

**English**: review paper, submit for review, peer review, get reviews, check review status, collect reviews, dual review, external review, internal review, paper review, review my paper, submit to paperreview

**繁體中文**: 審稿, 提交審稿, 論文審稿, 同儕審查, 外部審稿, 內部審稿, 雙重審稿, 檢查審稿狀態, 收集審稿結果

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Writing a paper (not reviewing) | `write-skill` |
| Literature search / finding references | `search-skill` |
| Full research pipeline | `pipeline-skill` |
| Revising after review | `write-skill` |

---

## Modes

| Mode | Trigger | What It Does |
|------|---------|-------------|
| `full` | "review this paper", "submit for review" | Submit external + run internal in parallel → collect both → synthesis |
| `external-only` | "submit to paperreview.ai", "external review only" | Submit to paperreview.ai → poll → save external.md |
| `internal-only` | "internal review only", "run internal reviewers" | Run 5 internal reviewers via claude -p → save to internal/ |
| `poll` | "check review status", "get review for token" | Poll paperreview.ai for an existing submission token |
| `synthesis` | "synthesize reviews", "compare reviews" | Read existing internal + external reviews, produce synthesis.md |
| `status` | "review status", "where is my review" | Report current state: token, poll progress, internal progress |

Default mode: `full` (dual review).

---

## Workflow Detail

### Mode: full — Dual Review

**Step 1: Prepare output directory**
1. Determine the paper's workspace directory from the PDF path
2. If `review/` dir exists, find the next round number (`round_000`, `round_001`, ...)
3. Create `review/round_<NNN>/` with `internal/` subdirectory

**Step 2: Launch reviews in parallel**

*Track A — External (paperreview.ai):*
1. Call `paperreview_api.submit_paper(pdf_path, email, venue)` → get token
2. Save token to `round_<NNN>/token.txt`
3. Wait initial 300s, then poll every 60s via `paperreview_api.poll_review(token)`
4. On ready: convert to markdown via `paperreview_api.review_to_markdown(review)`
5. Save to `round_<NNN>/external.md`
6. Extract verdict via `paperreview_api.extract_verdict(review)`

*Track B — Internal (5 reviewers running in parallel via claude -p):*
1. Extract paper text (pdftotext for PDF, or read .tex directly)
2. Launch 5 reviewer personas concurrently (as defined in internal_review.py REVIEWER_POOL):

   | Reviewer | Focus |
   |----------|-------|
   | Methodology Expert | Algorithm design, theory, notation, reproducibility |
   | Experiments Reviewer | Datasets, baselines, metrics, statistics, ablations |
   | Clarity & Writing Reviewer | Structure, clarity, flow, figures, AI-writing flags |
   | Related Work Reviewer | Literature coverage, missing citations, positioning |
   | Devil's Advocate | Overclaims, hidden assumptions, alternative explanations |

3. Each reviewer runs via: `claude -p --model <model> "<reviewer_prompt + paper_text>"`
4. Save individual reviews to `round_<NNN>/internal/<reviewer_slug>.md`
5. Merge into `round_<NNN>/internal/merged_internal_review.md`
6. Extract scores, compute average, determine internal consensus verdict

**Step 3: Wait for both tracks**

Track A (external) typically takes 5-15 minutes. Track B (internal) typically takes 3-8 minutes (parallel execution). Report progress as each track completes.

**Step 4: Synthesis**

Once both tracks complete, produce `round_<NNN>/synthesis.md`:
1. **Verdict comparison**: external verdict vs internal consensus
2. **Agreement analysis**: where do all reviewers agree?
3. **Conflict analysis**: where do they disagree? Weight by reviewer expertise.
4. **Common issues**: issues flagged by both external and ≥2 internal reviewers
5. **External-only issues**: issues only paperreview.ai caught
6. **Internal-only issues**: issues only internal reviewers caught
7. **Revision roadmap**: prioritized list of changes with impact estimates
8. **Score summary table**:

   | Source | Reviewer | Score | Verdict |
   |--------|----------|-------|---------|
   | External | paperreview.ai | — | accept / weak accept / reject |
   | Internal | Methodology Expert | X/10 | — |
   | Internal | Experiments Reviewer | X/10 | — |
   | Internal | Clarity & Writing Reviewer | X/10 | — |
   | Internal | Related Work Reviewer | X/10 | — |
   | Internal | Devil's Advocate | X/10 | — |
   | **Internal** | **Consensus** | **avg/10** | **verdict** |

**Step 5: Round README**

Produce `round_<NNN>/README.md` summarizing:
- Round number, timestamp, paper path
- External review token and status
- Key findings (top 5 issues from both sources)
- Scores and verdicts table
- Path to synthesis for full details
- Path to external.md and internal/ for raw reviews

### Mode: external-only

Execute only Track A from full mode:
1. Submit to paperreview.ai → get token
2. Poll for results
3. Save `external.md` + `token.txt`

### Mode: internal-only

Execute only Track B from full mode:
1. Extract paper text
2. Run 5 reviewers in parallel
3. Save individual + merged reviews to `internal/`

### Mode: poll

For an existing submission (user provides token or token.txt):
1. Read token
2. Poll `paperreview_api.poll_review(token)`
3. Save/update `external.md`
4. Report verdict

### Mode: synthesis

When reviews already exist but synthesis hasn't been generated:
1. Read `external.md` and `internal/merged_internal_review.md`
2. Produce `synthesis.md` with cross-source comparison

### Mode: status

Report current state of reviews:
1. Check for token.txt → external review submitted?
2. Poll external status (if token exists)
3. Check for internal/ files → internal review done?
4. Report: "External: still processing (poll X of Y)" or "External: ready (verdict: Z)", etc.

---

## Internal Reviewer Personas (Detailed)

The 5 internal reviewers are defined in `internal_review.py:REVIEWER_POOL`. Their prompts use the **PROBLEM → IMPACT → FIX** format for actionable feedback. Each outputs a structured markdown section with: Strengths, Weaknesses, Detailed Issues, Score (1-10), Recommendation.

To invoke internal reviewers, the skill uses `claude -p` (the same mechanism as `internal_review.py`). The full reviewer prompts are in `internal_review.py:33-181`.

### Score → Verdict Mapping

| Average Score | Consensus Verdict |
|---------------|-------------------|
| ≥ 7.0 | accept |
| 5.5 – 6.9 | weak accept |
| < 5.5 | revise |

---

## paperreview.ai API Flow

The external review uses the 3-step upload process implemented in `paperreview_api.py`:

```
POST /api/get-upload-url  → presigned S3 URL + s3_key
POST <presigned_url>       → upload PDF directly to S3
POST /api/confirm-upload   → finalize; returns review token
```

Then poll:
```
GET /api/review/{token}    → 202 = still processing, 200 = review ready
```

Default parameters:
- Venue: AAAI (configurable)
- Email: 250010008@slai.edu.cn
- Initial wait: 300s (5 min)
- Poll interval: 60s
- Max wait: 7200s (2 hours)

---

## Output Directory Convention

Every review round is self-contained:

```
<paper_workspace>/review/
├── round_000/                  # First submission
│   ├── README.md               # Round summary
│   ├── token.txt               # paperreview.ai review token
│   ├── external.md             # paperreview.ai review (markdown)
│   ├── internal/               # Internal multi-perspective reviews
│   │   ├── methodology_expert.md
│   │   ├── experiments_reviewer.md
│   │   ├── clarity_writing_reviewer.md
│   │   ├── related_work_reviewer.md
│   │   ├── devils_advocate.md
│   │   └── merged_internal_review.md
│   └── synthesis.md            # Cross-source comparison + revision roadmap
├── round_001/                  # After first revision
│   ├── README.md
│   ├── token.txt
│   ├── external.md
│   ├── internal/
│   │   └── ...
│   └── synthesis.md
└── ...
```

Round numbers are zero-padded (`round_000`, `round_001`, ...). Each revision-and-resubmit cycle creates a new round.

When the user provides a paper path like `workspace/<topic>/paper/paper.pdf`, the review output goes to `workspace/<topic>/review/`.

---

## Automated Pre-Review Checks

Before launching LLM reviewers, run automated rule-based checks from `shared/review_tools.py`. These checks run instantly (no LLM call) and detect issues that human reviewers often catch.

### AI Writing Artifact Detection

Scans the paper for:
- **20 AI-flagged words**: delve, leverage, utilize, harness, pivotal, unveil, elucidate, foster, intricate, nuanced, profound, testament, vibrant, ameliorate, underscore, transcend, envision, bolster, culminate, traverse
- **Em-dash overuse**: >3 occurrences of `---`
- **Furthermore/Moreover overuse**: >3 occurrences each
- **Hedging pileups**: "may potentially", "could possibly", "might perhaps"

### Citation Coverage

- Flags papers with <10 unique citations (high severity)
- Flags papers with <25 citations (medium severity)
- Checks Related Work section has ≥10 citations

### LaTeX Structure Validation

- Checks `\begin`/`\end` environment balance
- Detects mismatched environments (e.g., `\begin{equation}...\end{parameter}`)
- Verifies `\documentclass` and `\end{document}` presence

### Usage in Review Flow

```python
from shared.review_tools import detect_ai_artifacts, check_citation_coverage, format_issues_for_llm

# After reading paper text
auto_issues = detect_ai_artifacts(paper_text)
auto_issues.extend(check_citation_coverage(paper_text))

# Inject into reviewer prompts
auto_checks_text = format_issues_for_llm(auto_issues)

# Add to each reviewer's prompt before the paper content
reviewer_prompt = f"{base_prompt}\n\n{auto_checks_text}\n\nPAPER:\n{paper_text}"
```

Automated check results are included in `merged_internal_review.md` as a dedicated section.

---

## Safety Rules

1. **Never lose a token**: always save token to `token.txt` immediately after submission
2. **Parallel is default**: external and internal reviews run concurrently to minimize wall-clock time
3. **Don't overwrite existing reviews**: auto-increment round number; never overwrite a completed round
4. **Report honestly**: if a reviewer crashes, note the error in merged output — don't fabricate a review
5. **Timeout handling**: if paperreview.ai doesn't return within 2h, report the token so the user can check manually
6. **Model selection**: internal reviewers use the current CLAUDE_MODEL from config; paperreview.ai uses its own model
7. **Quota awareness**: paperreview.ai has limited quota — every submission must be a substantial improvement over the previous version; never submit trivial text-only revisions
8. **TODO-driven revision**: every review round MUST produce a structured TODO list; each item must be explicitly marked as completed before re-submission
9. **Run automated checks before LLM review**: AI artifact detection + citation coverage + LaTeX validation must run BEFORE launching reviewers — results are injected into reviewer prompts

---

## Revision Protocol (Post-Review)

After receiving reviews (external + internal), the following protocol is MANDATORY before the next paper submission. This ensures every review round is treated with the rigor it deserves, given paperreview.ai's limited quota.

### Step 1: Generate Unified TODO List

From `synthesis.md`, extract every actionable criticism into a structured TODO list saved at `review/round_<NNN>/TODO.md`:

```markdown
# Revision TODO — Round NNN

## Critical (blocks resubmission)
- [ ] [E-001] Missing comparison to <method X> — add baseline + re-run experiments
- [ ] [E-002] Ablation for <component Y> is incomplete — design and run additional ablation
- [ ] [I-001] Theorem 3.2 has an unstated assumption — add formal condition

## Major (significantly weakens paper)
- [ ] [E-003] Dataset split details unclear — document train/val/test protocol
- [ ] [I-002] Related work misses <paper Z> (2024) — add discussion + citation
- [ ] [I-003] Figure 2 labels too small — regenerate figure

## Minor (cosmetic / clarity)
- [ ] [E-004] Abstract grammar issue in line 3
- [ ] [I-004] Table 1 missing standard deviation for baseline B
```

**Label convention**: `[E-NNN]` = external reviewer issue, `[I-NNN]` = internal reviewer issue. This preserves traceability back to the original review.

### Step 2: Classify Required Changes

| Type | Action Required | Example |
|------|----------------|---------|
| **Supplementary experiment** | Design + run new experiment, collect results | Missing baseline, additional ablation |
| **Literature gap** | Search for missing papers, read, add to related work | Reviewer pointed out uncited prior work |
| **Method clarification** | Rewrite section, add formal definitions | Ambiguous notation, missing assumption |
| **Figure/table** | Regenerate with corrections | Wrong error bars, illegible labels |
| **Text polish** | Language-only change (lowest priority) | Grammar, phrasing, structure |

**Rule**: Do NOT submit to paperreview.ai again if the only changes are text polish. At minimum, every resubmission must include new experimental evidence or substantially revised methodology.

### Step 3: Execute Items One by One

For each TODO item:
1. Determine which skill to dispatch (search-skill for literature gaps, experiment-skill for supplementary experiments, write-skill for text/method changes)
2. Execute the change
3. Mark the item as `[x]` in `TODO.md` with a brief note on what was done
4. Update the paper version

**Progress tracking** in `review/round_<NNN>/TODO.md`:
```
- [x] [E-001] Missing comparison to <method X> → Added baseline, running experiment (SCO job: pt-xyz123)
- [ ] [E-002] Ablation for <component Y> → Designed, pending experiment submission
```

### Step 4: Pre-Submission Checklist

Before re-submitting to paperreview.ai, verify:

```
□ At least one supplementary experiment was added, OR
□ At least 3 literature gaps were filled with new citations AND discussion, OR
□ A major methodology section was substantially rewritten
□ All Critical items are resolved
□ At least 80% of Major items are resolved
□ TODO.md shows all items are either checked or explicitly deferred with reason
□ The new paper version compiles successfully
```

If this checklist cannot be satisfied, do NOT re-submit to paperreview.ai — the revision is not yet substantial enough to justify consuming quota.

### Step 5: Attach Revision Notes

When re-submitting, include a `revision_notes.md` that maps each review criticism to the change made:

```markdown
# Revision Notes — Round NNN → Round MMM

## Response to External Reviewer
| Issue | Action | Location |
|-------|--------|----------|
| Missing comparison to X | Added X as baseline, Table 2, row 5 | paper.tex §4.2, L345 |
| Ablation incomplete | Added per-component ablation | paper.tex §4.3, Fig 4 |
| ... | ... | ... |

## Response to Internal Reviewers
| Reviewer | Issue | Action | Location |
|----------|-------|--------|----------|
| Experiments | No std dev reported | Added ±std to all tables | Tables 1-3 |
| Related Work | Missing Z (2024) | Added discussion | paper.tex §2, L156 |
| ... | ... | ... | ... |
```

## Reference Loading

- Read [review_organization.md](references/review_organization.md) for detailed output directory specification and naming conventions
- Read [paperreview_api_reference.md](references/paperreview_api_reference.md) for full API details, error codes, and edge cases
