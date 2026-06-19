"""
Paper resource acquisition — PDF download, GitHub repo search, dataset discovery.
Used by search-skill for the pdf-download, github-search, and data-search modes.
"""

import os
import re
import time
import json
import logging
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "search-skill/2.0 (mailto:250010008@slai.edu.cn)"}
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# ---------------------------------------------------------------------------
# PDF Download
# ---------------------------------------------------------------------------

def download_paper_pdf(paper: dict, output_dir: Path | str) -> dict:
    """Download a single paper PDF. Returns {paper_title, path, status, reason}."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = _make_pdf_filename(paper)
    filepath = output_dir / filename

    if filepath.exists():
        return {"title": paper.get("title", ""), "path": str(filepath), "status": "cached"}

    # Priority 1: arXiv
    arxiv_id = paper.get("arxiv_id", "")
    if arxiv_id:
        result = _download(f"https://arxiv.org/pdf/{arxiv_id}.pdf", filepath)
        if result["status"] == "ok":
            return {"title": paper.get("title", ""), "path": str(filepath), "status": "ok", "source": "arxiv"}

    # Priority 2: DOI
    url = paper.get("url", "")
    if url and "doi.org" in url:
        doi_suffix = url.split("doi.org/")[-1]
        result = _download(f"https://doi.org/pdf/{doi_suffix}", filepath)
        if result["status"] == "ok":
            return {"title": paper.get("title", ""), "path": str(filepath), "status": "ok", "source": "doi"}

    # Priority 3: Semantic Scholar URL → extract PDF
    if paper.get("source") == "semantic_scholar" and url:
        result = _download(url, filepath)
        if result["status"] == "ok":
            return {"title": paper.get("title", ""), "path": str(filepath), "status": "ok", "source": "s2"}

    return {"title": paper.get("title", ""), "path": None, "status": "failed", "reason": result.get("reason", "all sources exhausted")}


def download_papers_batch(papers: list[dict], output_dir: str, max_workers: int = 3) -> list[dict]:
    """Download PDFs for multiple papers concurrently."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_paper_pdf, p, output_dir): p for p in papers}
        for future in as_completed(futures):
            try:
                results.append(future.result(timeout=120))
            except Exception as e:
                paper = futures[future]
                results.append({"title": paper.get("title", ""), "status": "error", "reason": str(e)})
            time.sleep(3)  # rate limit between submissions
    return results


# ---------------------------------------------------------------------------
# GitHub Search
# ---------------------------------------------------------------------------

GITHUB_API = "https://api.github.com"

def search_github_repo(paper: dict) -> list[dict]:
    """Search GitHub for repositories implementing a paper."""
    title_words = " ".join(paper.get("title", "").split()[:8])
    authors = paper.get("authors", [])
    first_author = authors[0].split()[-1] if authors else ""

    query = f"{title_words} {first_author} in:readme"

    try:
        resp = requests.get(
            f"{GITHUB_API}/search/repositories",
            params={"q": query, "sort": "stars", "per_page": 5},
            headers=HEADERS,
            timeout=30,
        )
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            logger.warning("GitHub rate limit reached")
            return []
        resp.raise_for_status()
        repos = resp.json().get("items", [])
    except requests.RequestException as e:
        logger.warning("GitHub search failed for '%s': %s", paper.get("title", "")[:60], e)
        return []

    scored = []
    for repo in repos:
        score = _score_repo(repo, paper)
        scored.append({
            "full_name": repo["full_name"],
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "language": repo.get("language", ""),
            "last_push": repo.get("pushed_at", ""),
            "description": repo.get("description", ""),
            "confidence": "HIGH" if score >= 60 else ("MEDIUM" if score >= 30 else "LOW"),
            "confidence_score": score,
            "fork": repo.get("fork", False),
            "license": (repo.get("license") or {}).get("spdx_id", "None"),
        })

    return sorted(scored, key=lambda r: r["confidence_score"], reverse=True)


def search_github_batch(papers: list[dict], output_dir: str) -> dict:
    """Search GitHub for repos for all papers. Returns paper→repos mapping."""
    results = {}
    for i, paper in enumerate(papers):
        repos = search_github_repo(paper)
        if repos:
            results[paper.get("title", f"paper_{i}")] = repos
        time.sleep(2)  # rate limit for search endpoint
    return results


# ---------------------------------------------------------------------------
# Dataset Search
# ---------------------------------------------------------------------------

def search_pwc_datasets(task: str) -> list[dict]:
    """Search PapersWithCode for datasets related to a task."""
    try:
        resp = requests.get(
            "https://paperswithcode.com/api/v1/datasets/",
            params={"q": task},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        logger.warning("PWC search failed: %s", e)
        return []


def search_hf_datasets(query: str) -> list[dict]:
    """Search HuggingFace datasets."""
    try:
        resp = requests.get(
            "https://huggingface.co/api/datasets",
            params={"search": query, "sort": "downloads", "limit": 20},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning("HF search failed: %s", e)
        return []


def search_kaggle_datasets(query: str) -> list[dict]:
    """Search Kaggle datasets."""
    try:
        resp = requests.get(
            "https://www.kaggle.com/api/v1/datasets",
            params={"search": query, "sortBy": "votes"},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning("Kaggle search failed: %s", e)
        return []


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_pdf_filename(paper: dict) -> str:
    first_author = paper.get("authors", ["unknown"])[0]
    lastname = first_author.split()[-1].lower() if first_author else "unknown"
    year = paper.get("year", "????")
    title_words = "_".join(paper.get("title", "untitled").lower().split()[:4])
    safe = re.sub(r"[^a-z0-9_]", "", title_words)
    return f"{lastname}_{year}_{safe}.pdf"


def _download(url: str, filepath: Path, timeout: int = 30) -> dict:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "")
            if "application/pdf" in content_type or url.endswith(".pdf"):
                with open(filepath, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                if _is_valid_pdf(filepath):
                    return {"status": "ok"}
                else:
                    filepath.unlink(missing_ok=True)
                    return {"status": "failed", "reason": "not a valid PDF"}
        if resp.status_code == 429:
            return {"status": "failed", "reason": "rate limited"}
        if resp.status_code in (401, 403):
            return {"status": "failed", "reason": "paywalled or access denied"}
        return {"status": "failed", "reason": f"HTTP {resp.status_code}"}
    except requests.Timeout:
        return {"status": "failed", "reason": "timeout"}
    except Exception as e:
        return {"status": "failed", "reason": str(e)[:100]}


def _is_valid_pdf(filepath: Path) -> bool:
    try:
        with open(filepath, "rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False


def _score_repo(repo: dict, paper: dict) -> int:
    score = 0
    desc = (repo.get("description") or "").lower()
    readme_owner = repo.get("full_name", "").lower()
    paper_title = paper.get("title", "").lower()
    first_author = (paper.get("authors", [""])[0] or "").lower()

    if first_author and first_author in readme_owner:
        score += 40
    if any(w in desc for w in paper_title.split()[:6] if len(w) > 3):
        score += 30
    if "official" in desc:
        score += 30
    if paper.get("arxiv_id", "") and paper["arxiv_id"] in desc:
        score += 20
    if repo.get("stargazers_count", 0) > 100:
        score += 15
    if repo.get("fork", False):
        score -= 20

    return score
