---
name: search-skill
description: "Academic search and resource acquisition skill — searches academic APIs (arXiv, Semantic Scholar, OpenAlex) for high-quality papers, downloads paper PDFs, extracts and searches GitHub repositories linked from papers, and discovers downloadable datasets and benchmarks. 9 modes: lit-search, full, quick, socratic, deep, verify, pdf-download, github-search, data-search. Triggers on: search papers, literature search, find papers, download paper, download PDF, find code, search github repo, find dataset, 文献检索, 找论文, 下载论文, 找代码, 找数据."
metadata:
  version: "2.0"
  last_updated: "2026-05-28"
---

# Search Skill — Academic Literature Search & Resource Acquisition

Searches academic databases for papers, downloads PDFs, finds open-source repositories, and discovers datasets — everything needed to go from a research topic to a complete set of reference materials with code and data.

## Quick Start

**Paper search:**
```
Search papers on "diffusion models for molecular generation"
```

**Download PDFs for found papers:**
```
Download PDFs for the papers in workspace/my_topic/literature/literature_review.md
```

**Find open-source code:**
```
Search GitHub for official implementations of papers in workspace/my_topic/literature/
```

**Find datasets:**
```
Find benchmark datasets for "medical image segmentation"
```

**Execution flow:**
1. Query formulation → multi-source retrieval (arXiv + Semantic Scholar + OpenAlex)
2. Merge & deduplicate → sort by relevance/citations → output literature_review.md + references.bib
3. (Optional) Download PDFs for top papers
4. (Optional) Extract GitHub links from papers and search for implementations
5. (Optional) Search for datasets and benchmarks with download links

---

## Trigger Conditions

### Trigger Keywords

**Paper search**:
search papers, literature search, find papers, research topic, literature review, survey papers on, recent work on, key papers, search arxiv, search literature, 查论文, 搜论文, 文献检索, 文献综述

**PDF download**:
download paper, download PDF, get PDF, fetch paper, download the paper, 下载论文, 下载PDF, 获取论文

**Code search**:
find code, search github, find implementation, open source code, official implementation, github repo, 找代码, 搜索代码, 开源实现, GitHub仓库

**Data search**:
find dataset, search dataset, download dataset, benchmark data, training data, data source, 找数据, 数据集, 下载数据, 数据资源

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Writing a paper | `write-skill` |
| Peer review | `review-skill` |
| Running GPU experiments | `experiment-skill` |
| Full pipeline | `pipeline-skill` |

---

## Modes

| Mode | Trigger | What It Does | Output |
|------|---------|-------------|--------|
| `lit-search` | "search papers", "find literature" | Multi-API search → merge → format markdown + bibtex | literature_review.md, references.bib |
| `full` | "research topic", "full analysis" | lit-search + theme analysis + gap identification + key paper deep-dive | above + gap_analysis.md + key_papers.md |
| `quick` | "quick search", "brief overview" | arXiv-only search (~10 papers) → concise summary | literature_brief.md |
| `socratic` | "guide my research", "help me refine" | Interactive refinement of research question before searching | refined RQ + search strategy |
| `deep` | "deep research on", "comprehensive" | full mode + source verification + evidence grading + synthesis | full outputs + verification_report.md + synthesis.md |
| `verify` | "verify these sources", "check citations" | DOI validation, predatory journal check, evidence tier grading | verification_report.md |
| **`pdf-download`** | **"download paper", "get PDF"** | **Download PDFs for papers in a literature review using arXiv ID / DOI / URL** | **papers/ directory with PDFs** |
| **`github-search`** | **"find code", "search github"** | **Extract repo links from papers, search GitHub for implementations, clone/download** | **repos/ directory + repos_index.md** |
| **`data-search`** | **"find dataset", "search data"** | **Search PapersWithCode / HuggingFace / Kaggle / Zenodo for datasets, check availability** | **datasets/ directory + data_index.md** |

Default mode: `full` (lit-search + analysis).

---

## Mode: pdf-download — Paper PDF Acquisition

### Workflow

1. Read a `literature_review.md` or a list of paper titles/URLs/arXiv IDs
2. For each paper, determine the best download source:
   - **arXiv ID available** → `https://arxiv.org/pdf/{arxiv_id}.pdf` (most reliable)
   - **DOI available** → try `https://doi.org/{doi}` → resolve to publisher page → find PDF link
   - **Semantic Scholar URL** → follow to paper page → extract PDF link
   - **OpenAlex DOI** → same DOI resolution path
3. Download PDFs with polite rate limiting (1 request per 3 seconds)
4. Save to `<output_dir>/papers/` with filename: `{first_author}_{year}_{short_title}.pdf`
5. Track success/failure in `papers/download_log.md`

### Download Strategy

```python
import requests
import time
from pathlib import Path

def download_paper_pdf(paper: dict, output_dir: Path) -> str | None:
    """Try multiple sources to download a paper PDF. Returns path or None."""
    
    # Priority 1: arXiv PDF (most reliable, always works for arXiv papers)
    arxiv_id = paper.get("arxiv_id", "")
    if arxiv_id:
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        return _try_download(url, output_dir, paper, source="arxiv")
    
    # Priority 2: DOI → publisher PDF (may have paywall)
    doi = paper.get("url", "")  # OpenAlex stores DOI in url field
    if doi and "doi.org" in doi:
        # Try direct DOI resolution
        url = doi.replace("https://doi.org/", "https://doi.org/") 
        # Some publishers allow direct PDF via doi.org/pdf/
        pdf_url = f"https://doi.org/pdf/{doi.split('doi.org/')[-1]}"
        result = _try_download(pdf_url, output_dir, paper, source="doi")
        if result:
            return result
    
    # Priority 3: Semantic Scholar paper URL (may have PDF link on page)
    s2_url = paper.get("url", "") if paper.get("source") == "semantic_scholar" else ""
    if s2_url:
        # Semantic Scholar often links to arxiv or publisher PDF
        result = _try_extract_and_download(s2_url, output_dir, paper)
        if result:
            return result
    
    return None  # Could not download

def _try_download(url: str, output_dir: Path, paper: dict, source: str) -> str | None:
    """Attempt to download PDF from URL. Return path or None."""
    try:
        resp = requests.get(url, timeout=30, stream=True)
        if resp.status_code == 200 and "application/pdf" in resp.headers.get("content-type", ""):
            filename = _make_filename(paper)
            filepath = output_dir / filename
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return str(filepath)
    except Exception:
        pass
    return None
```

### Rate Limiting & Politeness

- 3 seconds between requests (be a good API citizen)
- Max 5 retries on network errors with exponential backoff
- Concurrent downloads: max 3 at a time
- User-agent header: `search-skill/2.0 (mailto:250010008@slai.edu.cn)`

### Output

```
<workspace>/literature/papers/
├── song_2021_score_based_sde.pdf
├── xu_2022_geodiff.pdf
├── ho_2020_denoising_diffusion.pdf
├── ...
└── download_log.md        # Success/failure per paper
```

### Failure Handling

| Failure | Action |
|---------|--------|
| Paywall (publisher requires subscription) | Log: "Paywalled — try institutional access or Sci-Hub" |
| 404 / paper not found | Log, try next source |
| Network timeout | Retry ×3 with backoff |
| Rate limited (429) | Wait 30s, retry |
| All sources exhausted | Log: "Could not download — manual retrieval needed" |

---

## Mode: github-search — Repository Discovery

### Workflow

1. Read a `literature_review.md` or paper list
2. For each paper, extract repository clues:
   - **Explicit GitHub links** in paper abstract/URL (scan for `github.com/*`)
   - **arXiv abstract** — some authors list code URL at the end
   - **Paper title + "official implementation"** → search GitHub API
3. Search GitHub API for each paper:
   ```
   GET https://api.github.com/search/repositories?q={paper_title_keywords}+{first_author}
   ```
4. Score repositories by relevance:
   - Exact paper title match in README → HIGH confidence
   - Author name match → HIGH confidence
   - Keyword match only → MEDIUM confidence
   - Fork of another result → LOW confidence (likely not official)
5. For each found repo, collect:
   - Stars, forks, last commit date (freshness)
   - Language (Python/PyTorch preferred)
   - README content (confirm it's the right paper)
   - Requirements file (for experiment reproducibility)

### GitHub API Integration

```python
import requests

GITHUB_API = "https://api.github.com"
# Optional: GITHUB_TOKEN from environment for higher rate limit
HEADERS = {"Accept": "application/vnd.github.v3+json"}
if token := os.environ.get("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"token {token}"

def search_github_for_paper(paper: dict) -> list[dict]:
    """Search GitHub for repositories implementing a paper."""
    # Build query: paper title keywords + first author
    title_words = " ".join(paper["title"].split()[:8])  # first 8 words
    first_author = paper.get("authors", [""])[0].split()[-1] if paper.get("authors") else ""
    
    query = f"{title_words} {first_author} in:readme"
    
    resp = requests.get(
        f"{GITHUB_API}/search/repositories",
        params={"q": query, "sort": "stars", "per_page": 5},
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("items", [])
```

### Output

```
<workspace>/literature/repos/
├── repos_index.md          # Structured index of all found repos
├── repos.json              # Machine-readable repo data
└── <repo_name>/            # Cloned repos (if requested)
    └── ...
```

**repos_index.md** format:
```markdown
# Code Repositories — <topic>

## Paper: Score-Based Generative Modeling through SDEs (Song et al., 2021)
- **Repo**: [yang-song/score_sde](https://github.com/yang-song/score_sde)
- **Stars**: 3.2k | **Language**: Python | **Last commit**: 2024-08
- **Confidence**: HIGH (author match + title match)
- **Status**: Official implementation ✓

## Paper: GeoDiff (Xu et al., 2022)
- **Repo**: [MinkaiXu/GeoDiff](https://github.com/MinkaiXu/GeoDiff)
- **Stars**: 280 | **Language**: Python | **Last commit**: 2024-03
- **Confidence**: HIGH (author match)
- **Status**: Official implementation ✓
- **Note**: Requires PyTorch Geometric ≥ 2.0

## Paper: Denoising Diffusion Probabilistic Models (Ho et al., 2020)
- **Repo**: [hojonathanho/diffusion](https://github.com/hojonathanho/diffusion)
- **Stars**: 1.2k | **Language**: Python | **Last commit**: 2022-11
- **Confidence**: HIGH
- **Status**: Official ✓ but unmaintained. Active fork: [lucidrains/denoising-diffusion-pytorch](https://github.com/lucidrains/denoising-diffusion-pytorch) (7.8k stars)
```

### Rate Limiting

- GitHub API: 60 req/hour without token, 5000 req/hour with token
- Search queries are expensive — batch paper titles into groups of 5 per query
- Cache results to `repos/repos.json` to avoid re-searching

---

## Mode: data-search — Dataset & Benchmark Discovery

### Workflow

1. Accept a research topic or a `literature_review.md`
2. Search multiple data sources:
   - **PapersWithCode**: `/api/v1/evaluation-tables/` → find benchmarks + datasets
   - **HuggingFace Datasets**: `https://huggingface.co/api/datasets?search={query}`
   - **Kaggle**: `https://www.kaggle.com/api/v1/datasets?search={query}`
   - **Zenodo**: `https://zenodo.org/api/records?q={query}`
   - **Google Dataset Search**: WebSearch fallback
3. For each dataset found, report:
   - Name, description, size, format
   - License (CC-BY, MIT, custom — critical for paper use)
   - Download URL and access method (direct, API, request-only)
   - Citation requirement
   - Used by which papers in the literature review (cross-reference)
4. Rank by relevance:
   - Used by ≥2 papers in the lit review → HIGH
   - Standard benchmark in the field → HIGH
   - Related but not used by found papers → MEDIUM
   - Generic dataset (e.g., ImageNet for non-vision tasks) → LOW

### API Integration

```python
# PapersWithCode — benchmarks for a task
def search_pwc_datasets(task: str) -> list[dict]:
    resp = requests.get(
        "https://paperswithcode.com/api/v1/datasets/",
        params={"q": task},
        timeout=30,
    )
    return resp.json().get("results", [])

# HuggingFace Datasets
def search_hf_datasets(query: str) -> list[dict]:
    resp = requests.get(
        "https://huggingface.co/api/datasets",
        params={"search": query, "sort": "downloads", "limit": 20},
        timeout=30,
    )
    return resp.json()

# Kaggle Datasets
def search_kaggle_datasets(query: str) -> list[dict]:
    resp = requests.get(
        "https://www.kaggle.com/api/v1/datasets",
        params={"search": query, "sortBy": "votes"},
        timeout=30,
    )
    return resp.json()
```

### Output

```
<workspace>/literature/datasets/
├── data_index.md            # Structured index of all datasets
└── data_sources.json        # Machine-readable dataset data
```

**data_index.md** format:
```markdown
# Dataset Index — <topic>

## HIGH Relevance (Standard Benchmarks)

### 1. GEOM-QM9
- **Description**: Geometric embeddings of QM9 molecules (130K molecules)
- **Size**: 2.3 GB | **Format**: .npz, .sdf
- **License**: CC-BY 4.0
- **Download**: https://doi.org/10.6084/m9.figshare.12345678
- **Papers using it**: Song 2021, Xu 2022, Ho 2020
- **Citation**: Ramakrishnan et al., Scientific Data 2014

### 2. GEOM-Drugs
- **Description**: Conformers for 300K+ drug-like molecules
- **Size**: 18 GB | **Format**: .sdf, .npz
- **License**: CC-BY 4.0
- **Download**: https://doi.org/10.6084/m9.figshare.87654321
- **Papers using it**: Xu 2022, Shi 2021

## MEDIUM Relevance (Related)

### 3. ChEMBL
- **Description**: Bioactivity data for 2M+ compounds
- **Size**: 5 GB (subset) | **Format**: CSV, SDF
- **License**: CC-BY-SA 3.0
- **Download**: https://www.ebi.ac.uk/chembl/
- **Note**: Not specific to molecular generation but commonly used

## Data Download Status
| Dataset | Status | Path | Size |
|---------|--------|------|------|
| GEOM-QM9 | ✓ Downloaded | datasets/GEOM-QM9/ | 2.3 GB |
| GEOM-Drugs | ⏳ Downloading... | — | 18 GB |
| ChEMBL | ✗ Too large for auto-download | — | 5 GB |

## Data Citation Checklist
For your paper, cite:
- [ ] Ramakrishnan et al. (2014) for QM9
- [ ] Axelrod & Gomez-Bombarelli (2022) for GEOM
```

### Download Handling

- **Small datasets (<1 GB)**: Auto-download to `datasets/`
- **Medium datasets (1-10 GB)**: Ask user before downloading
- **Large datasets (>10 GB)**: Provide download instructions only, do not auto-download
- **API-gated datasets**: Provide access instructions (registration URL, API key setup)
- Always record the download source URL and MD5/SHA checksum if available

---

## Multi-Source Search Architecture

### API Sources

| Source | API | Key Required | Rate Limit | Strengths |
|--------|-----|-------------|------------|-----------|
| **arXiv** | `export.arxiv.org/api/query` | No | 1 req / 3s | CS, math, physics preprints |
| **Semantic Scholar** | `api.semanticscholar.org/graph/v1/paper/search` | Yes (s2k-...) | 100 req / 5min | Citation counts, venue info |
| **OpenAlex** | `api.openalex.org/works` | No | 10 req / s | Broad coverage, open access |
| **GitHub** | `api.github.com/search/repositories` | Optional | 60→5000 req/h with token | Code repositories |
| **PapersWithCode** | `paperswithcode.com/api/v1/` | No | Polite | Benchmarks, datasets, code |
| **HuggingFace** | `huggingface.co/api/datasets` | No | Polite | ML datasets |
| **Kaggle** | `kaggle.com/api/v1/datasets` | Optional | Polite | Competition + research datasets |

---

## Output Directory Convention (Updated)

```
<workspace>/literature/
├── literature_review.md       # Main output: formatted paper list + summaries
├── references.bib             # BibTeX entries
├── gap_analysis.md            # (full/deep mode) Research gaps
├── key_papers.md              # (full mode) Deep-dive on top papers
├── verification_report.md     # (deep/verify mode) Source quality
├── synthesis.md               # (deep mode) Cross-source synthesis
├── search_queries.txt         # Queries used (for reproducibility)
├── papers/                    # (pdf-download mode) Downloaded PDFs
│   ├── download_log.md
│   └── *.pdf
├── repos/                     # (github-search mode) Found repositories
│   ├── repos_index.md
│   ├── repos.json
│   └── <cloned_repos>/
└── datasets/                  # (data-search mode) Dataset index + downloads
    ├── data_index.md
    ├── data_sources.json
    └── <downloaded_datasets>/
```

---

## Safety & Quality Rules

1. **Reproducibility**: always save search queries to `search_queries.txt`
2. **Source transparency**: every paper must show its source
3. **No fabrication**: never invent paper titles, authors, or abstracts
4. **Rate limit respect**: 3s between PDF downloads, cache GitHub results, respect API limits
5. **License awareness**: flag dataset licenses; warn if commercial use is restricted
6. **Paywall honesty**: don't claim a PDF is downloaded if it's behind a paywall
7. **Gap honesty**: if no papers/datasets/repos found, report it
8. **Storage awareness**: report total download size before bulk downloading

## Reference Loading

- Read [academic_apis.md](references/academic_apis.md) for paper search API specifications
- Read [search_strategies.md](references/search_strategies.md) for query formulation techniques
- Read [pdf_download.md](references/pdf_download.md) for PDF acquisition strategies and paywall handling
- Read [github_repos.md](references/github_repos.md) for GitHub search patterns and repo evaluation
- Read [data_resources.md](references/data_resources.md) for dataset discovery platforms and download strategies
