# Review Skill — Usage Examples

## Example 1: Full Dual Review (Default)

**User:**
```
Review this paper: workspace/federated_learning/paper/paper.pdf
```

**Skill executes:**
1. Determine review dir: `workspace/federated_learning/review/`
2. First submission → create `round_000/`
3. Launch external (paperreview.ai) + internal (5 reviewers) in parallel
4. Save token to `round_000/token.txt`
5. Save external review → `round_000/external.md`
6. Save internal reviews → `round_000/internal/*.md`
7. Produce synthesis → `round_000/synthesis.md`
8. Produce README → `round_000/README.md`

**Progress output:**
```
Review Round 000 started for federated_learning/paper/paper.pdf

[internal] Methodology Expert ... ✓ (8/10)
[internal] Experiments Reviewer ... ✓ (7/10)
[internal] Clarity & Writing Reviewer ... running
[internal] Related Work Reviewer ... running
[internal] Devil's Advocate ... running
[external] Submitted to paperreview.ai (token: pt_abc123)
[external] Waiting 5 minutes before first poll...

[internal] All 5 reviewers complete (avg 7.2/10 → ACCEPT)
[external] Polling (attempt 6, elapsed 10min)...
[external] Review ready! Verdict: weak accept

Synthesis complete → round_000/synthesis.md
Round README → round_000/README.md

Done. 2 sources agree: paper is acceptable with minor revisions.
```

## Example 2: External Review Only

**User:**
```
Submit this paper to paperreview.ai: paper.pdf (venue: NeurIPS)
```

**Skill executes:**
1. Create review directory
2. Submit to paperreview.ai with venue=NeurIPS
3. Poll for results
4. Save `external.md` + `token.txt`
5. Report verdict

## Example 3: Internal Review Only

**User:**
```
Run internal review on workspace/my_paper/paper/paper.pdf
```

**Skill executes:**
1. Create review directory
2. Extract paper text (pdftotext)
3. Run 5 reviewers in parallel via claude -p
4. Save individual + merged reviews to `internal/`
5. Report average score and consensus verdict

## Example 4: Check External Review Status

**User:**
```
Check the status of my review: token pt_abc123
```

**Skill executes:**
1. Poll `GET /api/review/pt_abc123`
2. If 202: "Still processing. Polled X times over Y minutes."
3. If 200: "Review ready! Saving to external.md. Verdict: weak accept."

## Example 5: Synthesize Existing Reviews

**User:**
```
Synthesize reviews in workspace/my_paper/review/round_000/
```

**Skill executes:**
1. Read `external.md`
2. Read `internal/merged_internal_review.md`
3. Produce `synthesis.md` with cross-source comparison and revision roadmap

## Example 6: Re-review After Revision

**User:**
```
I revised my paper — review it again: workspace/my_paper/paper/paper.pdf
```

**Skill executes:**
1. Detect existing `round_000/` → create `round_001/`
2. Submit new external review (new token)
3. Run new internal review on revised paper
4. In synthesis, compare to previous round's findings
5. Note which issues were fixed vs persistent

## Example 7: Quick Status Check

**User:**
```
Review status for workspace/my_paper/
```

**Skill executes:**
1. Check `review/` directory
2. List all rounds with status
3. Report:
   ```
   workspace/my_paper/review/
   ├── round_000/  COMPLETE  (ext: weak accept, int: 7.2/10 accept)
   └── round_001/  IN PROGRESS (ext: polling, int: 3/5 done)
   ```
