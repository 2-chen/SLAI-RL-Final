# Chen-Research Evolution Patterns — Complete Catalog

A comprehensive catalog of common skill failure patterns across all chen-research-skills, with symptoms, root causes, detection rules, and canonical fixes. Used by the evolution_architect to speed up pattern recognition.

---

## Pattern Detection Rules

A pattern exists when **any** of these conditions are met:
- Same issue appears from ≥2 independent sources (e.g., external review + internal reviewer)
- Same issue appears ≥3 times across sessions/iterations
- Single critical issue that would affect most future pipeline runs (e.g., compilation always fails)

---

## L1: Trigger Gaps

### P1.1: Missing Domain Terminology
**Skill affected**: Any
**Symptoms**: User asks using field jargon, skill doesn't activate.
**Example**: "Run a training job on SenseCore" doesn't trigger experiment-skill (but "submit experiment" does).
**Detection**: Compare user vocabulary against trigger keywords in SKILL.md frontmatter.
**Fix**: Add domain synonyms to `description` triggers field.

### P1.2: Language Coverage Gap
**Skill affected**: Any
**Symptoms**: Triggers on English but not equivalent Chinese.
**Example**: "幫我跑實驗" doesn't trigger experiment-skill.
**Fix**: Add Chinese translations of trigger keywords. Follow existing bilingual pattern.

### P1.3: Implicit Intent Not Matched
**Skill affected**: Any
**Symptoms**: User intent clearly matches, but wording doesn't match any trigger.
**Example**: "I need GPU for training" → should trigger experiment-skill but doesn't.
**Fix**: Add intent-based phrases to triggers, not just technical terms.

### P1.4: Overly Broad Trigger (False Positive)
**Skill affected**: Any
**Symptoms**: Skill activates on unrelated requests.
**Example**: "Write a SQL query" triggers write-skill.
**Fix**: Add exclusion keywords or narrow trigger patterns.

---

## L2: Agent Instruction Gaps

### search-skill

#### P2.1: Query Too Narrow
**Symptoms**: Search returns <5 papers on reasonable topics. Gap analysis notes "insufficient literature."
**Fix**: Add query expansion instruction to search-agent.md: "If first search returns <5 results, automatically generate 2-3 alternative queries with broader terms."

#### P2.2: Missing Source Verification
**Symptoms**: Internal reviewers or paperreview.ai flag broken DOIs, predatory journals, or retracted papers in references.
**Fix**: Add pre-output verification step: "For all tier_1 papers, verify DOI resolves before including in literature_review.md."

#### P2.3: No Currency Warning
**Symptoms**: Literature review includes papers from 2018 without noting they may be outdated (CS/AI moves fast).
**Fix**: Add currency check: "Flag papers older than 3 years (CS/AI) or 5 years (other fields) with a 'may be outdated' note."

#### P2.3b: PDF Download Paywall Silence
**Symptoms**: pdf-download mode reports "failed" without distinguishing paywall from network error.
**Fix**: Add detailed failure reason to download_log.md: paywall / timeout / not-found / rate-limited.

#### P2.3c: GitHub Query Too Strict
**Symptoms**: github-search returns 0 results for well-known papers with public implementations.
**Fix**: Broaden query: remove author constraint first, then reduce title keywords to top 4 words.

### experiment-skill

#### P2.4: Missing Pre-Flight Checks
**Symptoms**: SCO submit fails with "sco CLI not found" or "workspace not accessible."
**Fix**: Add pre-flight sequence to experiment-agent.md: which sco → sco config list → verify AFS mount accessible.

#### P2.5: No Auto-Result Collection
**Symptoms**: Job succeeds but user asks "where are my results?"
**Fix**: Add post-success step: stream-logs → save to experiment/sco_logs.txt → report results path.

#### P2.6: Default Spec Too Large
**Symptoms**: Jobs consistently OOM on first run.
**Fix**: Add guidance: "If job OOMs, suggest halving batch size and resubmitting before asking user."

### write-skill

#### P2.7: Missing Ablation Requirement
**Symptoms**: Internal Experiments Reviewer flags "no ablation study" in ≥2 rounds.
**Frequency**: HIGH — most common write-skill gap.
**Fix**: In write-agent.md experiments section, change "Consider including ablation" to "REQUIRED: ablation table showing per-component contribution."

#### P2.8: Word Budget Not Enforced
**Symptoms**: Paper consistently 1-2 pages over venue limit. Pipeline iteration wastes time cutting.
**Fix**: Add budget check after each section: "After drafting, report word count vs budget. If over by >10%, suggest cuts before proceeding."

#### P2.9: Figure Font Size Drift
**Symptoms**: Reviewer: "Figure text illegible" — font size dropped from 8pt to 6pt.
**Fix**: In write-agent.md, hardcode: "ALL figure text must be ≥7pt. Check before export. Reject figures with smaller text."

#### P2.10: AI-Writing Markers Not Caught
**Symptoms**: Internal Clarity reviewer repeatedly flags "LLM-generated feel."
**Fix**: Add post-polish scan in write-agent.md: "After polish, scan for: hedging pileups, 'delve into', 'leverage' used >3 times, 'furthermore'/'moreover' per paragraph >1. Flag and rewrite any found."

#### P2.11: Citation Format Mismatch
**Symptoms**: Compilation warnings: "Citation X undefined" even though it's in references.bib.
**Fix**: Add pre-compile check: "Verify all \cite{} keys exist in references.bib. Run grep 'citation{' paper.tex | sort -u against bib keys."

### review-skill

#### P2.12: Token Not Saved on Error
**Symptoms**: paperreview.ai submission succeeds but error in later step loses the token.
**Fix**: In review-agent.md: "Save token to token.txt IMMEDIATELY after submission, before any other operation."

#### P2.13: Internal Reviewer Timeout Not Handled
**Symptoms**: One reviewer crashes (timeout after 600s), merged review has "error" for that reviewer.
**Fix**: Add graceful degradation: "If a reviewer times out, note it in merged output with 'Reviewer unavailable for this round' — don't block the whole review."

#### P2.14: Synthesis Skips Comparison
**Symptoms**: synthesis.md has external and internal sections but no actual cross-comparison.
**Fix**: Add structure requirement: "synthesis.md MUST contain a Verdict Comparison table and an Agreement Analysis section."

### pipeline-skill

#### P2.15: Compression Brief Too Verbose
**Symptoms**: Iteration brief is 8KB instead of ~1KB. Defeats the purpose.
**Fix**: Add size limit: "Iteration brief MUST be under 2KB. If over, trim to: verdict, top 3 issues, key changes only."

#### P2.16: Verdict Gate Logic Too Permissive
**Symptoms**: Pipeline continues after borderline verdict without asking user.
**Fix**: Add explicit check: "If external verdict is 'borderline' AND internal ≥6.0, MUST offer user choice: continue or stop."

#### P2.17: Stage 2 Skip Not Tracked
**Symptoms**: Experiment skipped in iteration 2 but state.json doesn't record why.
**Fix**: When skipping Stage 2, write reason to state.json stages.experiment.notes.

---

## L3: Reference Gaps

### P3.1: Outdated SCO Worker Spec
**Skill**: experiment-skill
**Symptoms**: "Worker spec n6ls.iu.i40.4.32c512g not found" — cluster updated, spec deprecated.
**Fix**: Run `sco aec2 clusters list-workerspec` and update sco_config.md.

### P3.2: Missing CCF-A Venue Template
**Skill**: write-skill
**Symptoms**: User requests venue X (e.g., KDD, SIGIR, MM), write-skill defaults to AAAI.
**Fix**: Add venue entry to ccf_a_templates.md with page limit, template requirements, package bans.

### P3.3: API Rate Limit Changed
**Skill**: search-skill
**Symptoms**: Semantic Scholar starts returning 429 errors more frequently.
**Fix**: Update academic_apis.md with new rate limit and backoff strategy.

### P3.4: Missing Experiment Pattern
**Skill**: experiment-skill
**Symptoms**: User repeatedly hits the same failure mode that isn't documented.
**Fix**: Add new failure pattern to experiment_pattern.md (e.g., "CUDA version mismatch between image and code").

### P3.5: Outdated Venue Style Files
**Skill**: write-skill
**Symptoms**: AAAI 2026 style file conflicts with updated document class.
**Fix**: Download latest .sty/.bst from conference website, update templates/.

---

## L4: Template Gaps

### P4.1: Build Script Fails Without BibTeX
**Symptoms**: Papers without citations fail compilation because build.sh tries to run bibtex.
**Fix**: Add conditional in build.sh.j2: "if grep -q 'citation' paper.aux; then bibtex; else echo 'no citations'; fi"

### P4.2: State Template Missing Fields
**Symptoms**: pipeline state can't record new types of events.
**Fix**: Add fields to state.json template, maintain backward compatibility.

### P4.3: Run Experiment Template Assumes GPU
**Symptoms**: Experiment fails on CPU-only node.
**Fix**: Add GPU check at start of run_experiment.sh.j2: "nvidia-smi || echo 'WARNING: No GPU detected'"

---

## L5: Example Gaps

### P5.1: Edge Case Not Covered
**Symptoms**: Skill handles typical cases but fails on legitimate variant.
**Example**: write-skill handles AAAI/NeurIPS format well but fails on CVPR (different \documentclass).
**Fix**: Add edge case example to examples/usage.md.

### P5.2: Successful Run Not Promoted
**Symptoms**: A pipeline iteration produced excellent results due to a specific approach, but that approach isn't documented.
**Fix**: Extract the successful pattern, add as new example in the relevant skill.

---

## L6: Routing & Config Gaps

### P6.1: Skill Dispatched for Wrong Task
**Symptoms**: pipeline-skill dispatches experiment-skill for a theoretical paper.
**Fix**: Add paper-type check in pipeline-agent.md: "If paper_type is 'theoretical' or 'survey', offer to skip Stage 2."

### P6.2: Config Default Wrong for New Use Case
**Symptoms**: New SCO quota type available but not in config.py.
**Fix**: Add new default to shared/config.py with environment variable override.

### P6.3: Cross-Skill Handoff Missing Data
**Symptoms**: write-skill starts without experiment metrics because pipeline didn't pass them.
**Fix**: Add required fields to the stage transition handoff specification.

---

## L7: Shared Library Gaps

### P7.1: search_papers.py Missing Error Recovery
**Symptoms**: One API failure causes entire search to return empty.
**Fix**: Each API call wrapped in try/except; partial results returned if ≥1 source succeeds.

### P7.2: internal_review.py Prompt Too Long
**Symptoms**: Reviewer prompt + paper exceeds model context, causing truncated output.
**Fix**: Add smart truncation: prioritize abstract, intro, method, results; trim related work and conclusion if needed.

### P7.3: sco_runner.py Hardcoded AFS Path
**Symptoms**: AFS base path changed, all jobs fail.
**Fix**: Move AFS_BASE to config.py with environment variable override.

### P7.4: paperreview_api.py No Retry on Network Error
**Symptoms**: Transient network error causes submission failure with no retry.
**Fix**: Add exponential backoff retry for network errors in submit_paper() and poll_review().

---

## Cross-Cutting Patterns

### CC1: Overconfidence Pattern
**Across**: write-skill, search-skill
**Symptoms**: Claims presented with "demonstrate"/"establish" when evidence only supports "suggest".
**Fix**: Add claim calibration table (Evidence Strength → Appropriate Verbs) to all agent instructions.

### CC2: Missing Negative Space
**Across**: write-skill, review-skill
**Symptoms**: Only positive results reported. Failures, limitations, and null results omitted.
**Fix**: Add explicit "report negative results" instruction to all relevant agents.

### CC3: Context Creep
**Across**: pipeline-skill, write-skill
**Symptoms**: Each iteration produces more verbose output, accelerating context overflow.
**Fix**: Add verbosity budget to write-agent: "Each iteration's revision notes ≤500 words."
