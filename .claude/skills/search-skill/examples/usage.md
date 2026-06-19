# Search Skill — Usage Examples

## Example 1: Quick Literature Search

**User:**
```
Search papers on "diffusion models for molecular graph generation"
```

**Skill executes:**
1. Formulate query: `diffusion model AND molecular graph generation`
2. Run `search_papers.py` across all 3 APIs
3. Generate `literature_review.md` + `references.bib`

**Output:**
```
Search complete. Found 34 unique papers across 3 sources.

Sources: arXiv (15), Semantic Scholar (12), OpenAlex (18)
Date range: 2019 – 2026
Top venues: NeurIPS, ICLR, ICML, Nature Machine Intelligence

Most cited:
  1. "Score-Based Generative Modeling through Stochastic Differential Equations" (Song et al., 2021) — cited 2500+×
  2. "GeoDiff: A Geometric Diffusion Model for Molecular Conformation Generation" (Xu et al., 2022) — cited 180+×
  ...

Full review: workspace/molecule_gen/literature/literature_review.md
BibTeX: workspace/molecule_gen/literature/references.bib
```

## Example 2: Full Research Analysis

**User:**
```
Research "federated learning with differential privacy for healthcare" — full analysis
```

**Skill executes:**
1. lit-search on the topic → 42 papers found
2. Thematic analysis → 4 themes identified
3. Trend analysis → growing field (paper count doubling yearly)
4. Gap analysis → 6 specific research gaps documented
5. Key paper deep-dive → top 10 papers summarized

**Output structure:**
```
workspace/fedlearn_healthcare/literature/
├── literature_review.md       # 42 papers, formatted
├── references.bib             # BibTeX entries
├── gap_analysis.md            # 6 research gaps + future directions
├── key_papers.md              # Top 10 deep-dive
└── search_queries.txt         # Queries used
```

## Example 3: Quick Brief

**User:**
```
Quick search: are there papers on "LLM-based automated peer review"?
```

**Skill executes:**
1. arXiv-only search, 10 papers
2. Concise brief

**Output (`literature_brief.md`):**
```markdown
# Quick Literature Brief: LLM-based Automated Peer Review
**Searched**: 2026-05-28 | **Source**: arXiv | **Papers**: 10

## Top Papers
1. "Can LLMs Perform Peer Review?" (2024) — First systematic evaluation; LLMs match human reviewers on clarity feedback but miss methodological flaws.
2. "Automated Scientific Review with Large Language Models" (2025) — Proposes iterative review-refine pipeline using GPT-4.
3. ...

## Research Directions
- **LLM-as-Reviewer**: Directly using LLMs to generate reviews (dominant approach, 6/10 papers)
- **Human-AI Collaboration**: LLMs assist human reviewers rather than replace them (3/10 papers)
- **Review Quality Assessment**: Benchmarks for evaluating AI-generated reviews (1/10 papers)

## Key Authors
Liang (Stanford), Zhang (CMU), Wang (Meta AI)

## Verdict
Active and growing area. Worth pursuing but expect fast-moving competition.
```

## Example 4: Socratic Guidance

**User:**
```
I want to research something about AI in education but I'm not sure what specifically.
```

**Skill enters socratic mode:**
```
Let me help you refine this. 

Q: When you think about "AI in education," what specific aspect interests you most?
   - Personalized tutoring systems?
   - Automated assessment or grading?
   - AI for educational content creation?
   - Student engagement or dropout prediction?
   - Something else?

User: Automated assessment, especially for coding assignments.

Q: Good. So automated assessment of student code. Now — what's the gap you see?
   - Are existing tools not accurate enough?
   - Do they not give good feedback (just a score, not suggestions)?
   - Do they not handle certain types of assignments well?
   - Is the issue about fairness or bias in grading?

User: They give scores but not good feedback. Students don't learn from just a number.

Q: That's a clear problem. Let me propose a focused research question:
   "Generating educational code review feedback using LLMs for automated programming assessment"

   This narrows to: (1) code-specific, (2) feedback generation (not just scoring), 
   (3) educational purpose, (4) LLM-based approach.

   Does this capture your interest? Should I search with this focus?

User: Yes, search that.
```

→ Transitions to lit-search with the refined query.

## Example 5: Deep Research

**User:**
```
Deep research on "test-time adaptation for domain generalization in medical image segmentation"
```

**Skill executes:**
1. Expanded multi-query search (3 alternative queries, 60+ papers)
2. Source verification: DOI check, venue tier grading
3. Evidence synthesis: convergence mapping, contradiction identification
4. Gap analysis: 8 specific research gaps

**Output:**
```
Deep research complete. 63 unique papers analyzed.

Quality distribution:
  tier_1 (top venues): 18 papers (29%) — MICCAI, TMI, MedIA, NeurIPS
  tier_2 (peer-reviewed): 28 papers (44%) — Other journals/conferences
  tier_3 (preprints):    15 papers (24%) — arXiv
  tier_4 (grey lit):      2 papers (3%) — Tech reports
  Flagged (predatory):    0 papers

Evidence convergence (findings confirmed by ≥3 independent sources):
  ✓ TTA outperforms source-only models by 10-30% on distribution shifts
  ✓ Entropy minimization is the most common adaptation objective
  ✓ Batch normalization adaptation is more effective than layer norm for medical images

Contradictions (disagreements in literature):
  ⚠ TTA batch size: some papers show batch=1 works (instance-level), others require batch≥16

Output: workspace/tta_medical/literature/
```

## Example 6: Source Verification

**User:**
```
Verify the sources in workspace/my_paper/literature/literature_review.md
```

**Skill executes:**
1. Reads the paper list
2. Validates each DOI
3. Grades venue tier and evidence level
4. Produces quality report

**Output (`verification_report.md`):**
```markdown
# Source Verification Report
**Verified**: 2026-05-28 | **Papers**: 25

## Quality Distribution
| Tier | Count | % |
|------|-------|---|
| tier_1 (top venues) | 8 | 32% |
| tier_2 (peer-reviewed) | 12 | 48% |
| tier_3 (preprints) | 4 | 16% |
| tier_4 (grey literature) | 1 | 4% |
| DOI verified | 22/25 | 88% |

## Flagged Papers
- Paper #14: DOI does not resolve → verify manually
- Paper #21: Published in journal on Beall's watchlist → consider replacing
- Paper #23: Preprint, never published in peer-reviewed venue → flag as tier_3

## Recommendation
Source quality is adequate for a survey paper. Replace or supplement papers #21 and #23.
```

## Example 7: Download Paper PDFs

**User:**
```
Download PDFs for the top 10 papers in workspace/diffusion_mol/literature/literature_review.md
```

**Skill executes (pdf-download mode):**
1. Reads literature_review.md, extracts top 10 papers by citation count
2. For each: tries arXiv PDF → DOI → Semantic Scholar page
3. Downloads with 3s rate limiting, 3 concurrent threads
4. Logs all results

**Output:**
```
PDF Download Report
====================
Downloaded: 8/10
  ✓ song_2021_score_based_generative.pdf (2.1 MB, arXiv)
  ✓ xu_2022_geodiff_geometric_diffusion.pdf (3.4 MB, arXiv)
  ✓ ho_2020_denoising_diffusion_probabilistic.pdf (1.8 MB, arXiv)
  ✓ shi_2021_score_based_generative.pdf (4.2 MB, DOI)
  ✗ wang_2023_diffusion_molecular.pdf — paywalled (Springer)
  ✓ ...
  ✗ li_2024_equivariant_diffusion.pdf — 404 (try author's homepage)

Saved to: workspace/diffusion_mol/literature/papers/
Log: workspace/diffusion_mol/literature/papers/download_log.md
```

## Example 8: Find Open-Source Code

**User:**
```
Find GitHub repos for the papers in workspace/diffusion_mol/literature/
```

**Skill executes (github-search mode):**
1. Reads paper list
2. For each paper: `GET /search/repositories?q={title}+{author}+in:readme`
3. Scores repos: author match (+40), title match (+30), "official" (+30), arXiv ID (+20)
4. Writes repos_index.md + repos.json

**Output (`repos/repos_index.md`):**
```markdown
# Code Repositories — Diffusion Models for Molecular Generation

## HIGH Confidence (Official)
| Paper | Repo | Stars | Language | Freshness |
|-------|------|-------|----------|-----------|
| Song 2021 | yang-song/score_sde | 3.2k | Python | Active |
| Xu 2022 | MinkaiXu/GeoDiff | 280 | Python | 2024-03 |
| Ho 2020 | hojonathanho/diffusion | 1.2k | Python | Archived |

## MEDIUM Confidence (Unofficial but popular)
| Paper | Repo | Stars | Note |
|-------|------|-------|------|
| Ho 2020 | lucidrains/denoising-diffusion-pytorch | 7.8k | Active fork, more popular than official |

## LOW Confidence (keyword match only)
- None
```

## Example 9: Find Datasets

**User:**
```
Find benchmark datasets for "molecular conformation generation"
```

**Skill executes (data-search mode):**
1. Searches PapersWithCode + HuggingFace + Kaggle + Zenodo in parallel
2. Cross-references with papers in lit review
3. Ranks by benchmark usage frequency
4. Downloads small datasets, provides instructions for large ones

**Output (`datasets/data_index.md`):**
```markdown
# Dataset Index — Molecular Conformation Generation

## BENCHMARK: GEOM-QM9
- **Size**: 2.3 GB | **License**: CC-BY 4.0
- **Used by**: Song 2021, Xu 2022, Shi 2021, Ho 2020
- **Download**: https://doi.org/10.6084/m9.figshare.12345678
- **Status**: ✓ Downloaded to datasets/GEOM-QM9/

## BENCHMARK: GEOM-Drugs
- **Size**: 18 GB | **License**: CC-BY 4.0
- **Used by**: Xu 2022, Shi 2021
- **Download**: https://doi.org/10.6084/m9.figshare.87654321
- **Status**: ⚠ Too large for auto-download. Run:
  `wget https://doi.org/10.6084/m9.figshare.87654321 -O datasets/GEOM-Drugs/`

## RELATED: ChEMBL
- **Size**: 5 GB (subset) | **License**: CC-BY-SA 3.0
- **Download**: https://www.ebi.ac.uk/chembl/
- **Status**: ✗ API-gated. Register at chembl.github.io for access key.
```
