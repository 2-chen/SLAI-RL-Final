# Review Organization & Naming Convention

How review-skill organizes paper reviews by round and source.

## Directory Convention

```
<workspace>/review/
├── round_000/
│   ├── README.md
│   ├── token.txt
│   ├── external.md
│   ├── internal/
│   │   ├── methodology_expert.md
│   │   ├── experiments_reviewer.md
│   │   ├── clarity_writing_reviewer.md
│   │   ├── related_work_reviewer.md
│   │   ├── devils_advocate.md
│   │   └── merged_internal_review.md
│   └── synthesis.md
├── round_001/
│   └── ...
└── latest -> round_001/   # symlink to latest round (optional)
```

## Round Numbering

- Rounds are zero-padded to 3 digits: `round_000`, `round_001`, ..., `round_999`
- `round_000` is always the first submission
- Each revision-and-resubmit creates the next round
- To determine the next round number:
  ```python
  import os
  existing = sorted([d for d in os.listdir("review/") if d.startswith("round_")])
  next_num = len(existing)  # 0, 1, 2, ...
  next_dir = f"round_{next_num:03d}"
  ```

## File Specifications

### token.txt

Single line containing the paperreview.ai review token.

```
pt_abc123def456ghi789
```

### external.md

Markdown conversion of paperreview.ai JSON response. Structured as:

```markdown
# Stanford Agentic Reviewer — Review Report

**Paper**: <title>
**Venue**: <venue>
**Submitted**: <date>

---

## Summary
...

## Strengths
...

## Weaknesses
...

## Detailed Comments
...

## Questions
...

## Overall Assessment
...

**Parsed Verdict**: `accept`
```

### internal/<reviewer_slug>.md

Individual reviewer output. Each file follows this structure:

```markdown
# Internal Review: <Reviewer Name>

## <Section> Review

### Strengths (3-5)
...

### Weaknesses (3-5)
...

### Detailed Issues
- [PROBLEM] ... → [IMPACT] ... → [FIX] ...

### Score (1-10)
X

### Recommendation
Accept / Weak Accept / Borderline / Reject
```

Reviewer slugs:
| Reviewer Name | Slug |
|---------------|------|
| Methodology Expert | `methodology_expert` |
| Experiments Reviewer | `experiments_reviewer` |
| Clarity & Writing Reviewer | `clarity_writing_reviewer` |
| Related Work Reviewer | `related_work_reviewer` |
| Devil's Advocate | `devils_advocate` |

### internal/merged_internal_review.md

Aggregated internal review with header:

```markdown
# Internal Multi-Perspective Review

**Date**: YYYY-MM-DD HH:MM
**Reviewers**: 5 (Methodology Expert, Experiments Reviewer, ...)
**Average Score**: 6.4 / 10
**Consensus**: WEAK ACCEPT

---

## Methodology Expert
...

## Experiments Reviewer
...

## Clarity & Writing Reviewer
...

## Related Work Reviewer
...

## Devil's Advocate
...
```

### synthesis.md

Cross-source comparison document:

```markdown
# Review Synthesis — Round <NNN>

## Verdict Comparison

| Source | Verdict |
|--------|---------|
| paperreview.ai (external) | weak accept |
| Internal Consensus | accept (avg 7.2/10) |

## Score Summary

| Source | Reviewer | Score | Verdict |
|--------|----------|-------|---------|
| External | paperreview.ai | — | weak accept |
| Internal | Methodology Expert | 8/10 | accept |
| Internal | Experiments Reviewer | 7/10 | accept |
| Internal | Clarity & Writing Reviewer | 6/10 | weak accept |
| Internal | Related Work Reviewer | 8/10 | accept |
| Internal | Devil's Advocate | 7/10 | accept |
| **Internal** | **Consensus** | **7.2/10** | **accept** |

## Agreement Analysis

### Issues all reviewers agree on
1. ...

### Conflicts between reviewers
1. ...

## Common Issues (flagged by external + ≥2 internal)
...

## External-Only Issues (only paperreview.ai)
...

## Internal-Only Issues (only internal reviewers)
...

## Revision Roadmap

### Critical (must fix before resubmission)
1. [ ] ...

### Important (should fix)
1. [ ] ...

### Nice-to-have
1. [ ] ...
```

### README.md (Round Summary)

```markdown
# Review Round <NNN>

**Submitted**: YYYY-MM-DD HH:MM
**Paper**: <path>
**External Token**: <token>
**Status**: Complete

## Quick Summary

- External (paperreview.ai): **weak accept**
- Internal Consensus: **accept** (avg 7.2/10)
- Agreement: 4/5 internal reviewers agree with external verdict

## Top Issues

1. [Methodology] ...
2. [Experiments] ...
3. [Writing] ...
4. [Related Work] ...

## Files

- [External Review](external.md)
- [Internal Reviews](internal/)
- [Full Synthesis](synthesis.md)
```

## Workspace Discovery

When the user says "review this paper: path/to/paper.pdf", determine the review output directory:

1. If path is `workspace/<topic>/paper/paper.pdf` → reviews go to `workspace/<topic>/review/`
2. If path is just `paper.pdf` in current dir → reviews go to `./review/`
3. If path is arbitrary → reviews go to `<paper_dir>/review/`

Always create symlink `review/latest -> review/round_<NNN>/` after completing a round, pointing to the most recent round.
