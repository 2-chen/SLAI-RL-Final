# Chen-Research Skills

A suite of Claude Code skills for automated AI research: literature search, GPU experiment execution, CCF-A paper writing, dual-source peer review, closed-loop pipeline orchestration, and VPN/proxy network access.

## Skills Overview

| Skill | Purpose | Key Modes |
|-------|---------|-----------|
| `search-skill` v2.0 | Academic search + resource acquisition (PDF, code, data) | lit-search, full, quick, socratic, deep, verify, pdf-download, github-search, data-search |
| `experiment-skill` v1.1 | GPU experiment execution with auto-detection (local-first, remote fallback) | submit, monitor, logs, list, stop, diagnose, full |
| `sco-skill` v1.0 | Remote GPU execution on SenseCore SCO ACP cluster | submit, monitor, logs, list, stop, diagnose, full |
| `write-skill` v1.0 | CCF-A LaTeX paper writing with figures & tables | full, draft-only, section, figures, polish, compile, plan |
| `review-skill` v1.0 | Dual-source peer review (external + internal) | full, external-only, internal-only, poll, synthesis, status |
| `hypothesis-skill` v1.0 | ReAct-based research hypothesis generation with gap verification | full, generate, evaluate, refine |
| `pipeline-skill` v1.0 | Closed-loop orchestrator (iterate until weak accept) | (coordinates all above + context compression + VPN) |
| `evolution-skill` v1.0 | Meta-skill for self-improving skill files | analyze, propose, apply, retrospective, watch, distill |
| `vpn-skill` v1.0 | Network proxy management via clash-for-linux | on, off, status, setup, diagnose, full |

## Routing Rules

1. **pipeline-skill vs individual skills**: pipeline-skill = full orchestrator (search → experiment → write → review → iterate). If the user only needs a single function (just literature search, just experiments, just writing, just review), trigger the corresponding skill directly without the pipeline.

2. **search-skill vs write-skill**: search-skill = upstream resource gathering (papers, PDFs, code, data). write-skill = downstream paper production. Recommended flow: search-skill → write-skill.

3. **write-skill vs review-skill**: write-skill produces papers, review-skill evaluates them. After review, use write-skill (revision mode) to address feedback.

4. **experiment-skill vs search-skill**: experiment-skill runs GPU jobs (local or remote). search-skill finds papers and code. They are independent — run in parallel when possible.

5. **experiment-skill vs sco-skill**: experiment-skill = auto-detect GPUs and run locally or remotely. sco-skill = direct SCO/ACP remote GPU job management, no GPU detection. "run experiment" / "submit experiment" (without qualifier) → experiment-skill (auto-detect). "sco submit" / "acp job" / "remote GPU" / "SenseCore" → sco-skill. experiment-skill delegates to sco-skill when no local GPUs are available.

6. **evolution-skill vs everything else**: evolution-skill is NOT a user-facing production skill. It is a maintenance tool triggered after review cycles or on explicit request ("evolve skill", "improve skill").

7. **vpn-skill vs everything else**: vpn-skill is a **supporting skill** that ensures network connectivity for all other skills. It is auto-invoked by other skills when they hit network errors, or directly by the user ("turn on VPN", "can't download"). The pipeline-skill auto-checks network before each stage and invokes vpn-skill if needed.

8. **hypothesis-skill vs search-skill**: hypothesis-skill = generates research hypotheses from literature (ReAct loop → gap finding → scoring). search-skill = finds papers and resources. Use hypothesis-skill when the user wants to find research directions, not just papers. Recommended flow: hypothesis-skill → experiment-skill → write-skill.

## Quick Mode Selection

| Your Situation | Use |
|---------------|-----|
| "I have a research idea, need to find related work" | `search-skill` (lit-search or full) |
| "I need to find a research direction / research gap" | `hypothesis-skill` (full) |
| "I need to run an experiment (auto-detect GPU)" | `experiment-skill` (submit) |
| "I need to run GPU experiments on SenseCore / SCO" | `sco-skill` (submit) |
| "Submit SCO job / manage ACP jobs" | `sco-skill` |
| "I have results, need to write a CCF-A paper" | `write-skill` (full) |
| "I have a paper draft, need to review it" | `review-skill` (full) |
| "Do everything from research to publication" | `pipeline-skill` |
| "The skills keep making the same mistakes" | `evolution-skill` (analyze) |
| "I can't download from HuggingFace/GitHub" | `vpn-skill` (diagnose or on) |
| "Turn on VPN / enable proxy" | `vpn-skill` (on) |
| "Network timeout / connection refused" | `vpn-skill` (diagnose) |

## Shared Python Library

All skills share a Python library in `shared/`:
- `shared/config.py` — Unified configuration (API keys, SCO defaults)
- `shared/search_papers.py` — Multi-source academic search (arXiv + Semantic Scholar + OpenAlex)
- `shared/paperreview_api.py` — paperreview.ai submission & polling client
- `shared/internal_review.py` — 5-persona internal review system
- `shared/sco_runner.py` — SCO CLI wrapper for ACP job submission
- `shared/paper_download.py` — PDF download, GitHub search, dataset discovery
- `shared/review_tools.py` — Automated review checks: AI artifact detection, claim-result consistency, citation coverage, LaTeX structure validation

Import from project root:
```python
import sys; sys.path.insert(0, '/data/homework/RL/final2')
from shared.search_papers import search_arxiv, merge_results
from shared.paperreview_api import submit_paper, poll_review
```

## Configuration

All defaults in `shared/config.py`, overridable via environment variables:

```bash
# Academic APIs
export SEMANTIC_SCHOLAR_API_KEY=s2k-...

# SCO / SenseCore (used by sco-skill and experiment-skill's remote fallback)
export SCO_WORKSPACE=share-space
export SCO_AEC2=share-cluster
export SCO_IMAGE=registry.cn-sh-01.sensecore.cn/ccr-zhicheng-02/chen-mirror2:2chen-mini-20260410132739
export SCO_WORKER_SPEC=n6ls.iu.i40.4.32c512g
export SCO_STORAGE_MOUNT=01995892-d478-76d8-aec7-13fd8284477e:/data:/250010008

# paperreview.ai
export PAPERREVIEW_EMAIL=250010008@slai.edu.cn

# Pipeline
export PIPELINE_MAX_ITERATIONS=10
export PIPELINE_VENUE=AAAI

# VPN (vpn-skill)
export VPN_AUTO_ENABLE=true
export VPN_PROXY_HOST=127.0.0.1
export VPN_PROXY_PORT=7890

# GitHub (optional, for github-search mode)
export GITHUB_TOKEN=ghp_...
```

## Version Info
- **Version**: 1.2
- **Last Updated**: 2026-06-01
- **Total Skills**: 9 (5 production + 1 sco/remote + 1 orchestrator + 1 meta + 1 supporting [VPN])
- **Shared Modules**: 8 Python files
