# Academic Search API Reference

Complete reference for the three academic search APIs used by search-skill.

## arXiv API

**Endpoint**: `https://export.arxiv.org/api/query`
**Auth**: None (free, no key required)
**Rate limit**: ~1 request per 3 seconds (be polite, use exponential backoff on 429)
**Best for**: Computer science, mathematics, physics, statistics preprints

### Query Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `search_query` | `all:<terms>` | Supports Boolean: AND, OR, ANDNOT |
| `start` | `0` | Result offset |
| `max_results` | `20` | Max per request |
| `sortBy` | `relevance` | or `lastUpdatedDate`, `submittedDate` |
| `sortOrder` | `descending` | or `ascending` |

### Query Construction

- `all:diffusion+models` — search all fields
- `ti:diffusion+models` — title only
- `au:hochreiter` — author search
- `cat:cs.AI` — category filter
- `all:diffusion+AND+all:molecule` — Boolean AND
- `all:diffusion+ANDNOT+all:image` — exclude image-related

### Returned Fields Per Paper

```python
{
    "source": "arxiv",
    "title": "...",
    "authors": ["Author Name", ...],
    "year": "2024",
    "abstract": "...",
    "url": "https://arxiv.org/abs/XXXX.XXXXX",
    "arxiv_id": "XXXX.XXXXX",
    "category": "cs.AI",  # primary category
}
```

### Rate Limit Handling

```python
for attempt in range(3):
    resp = requests.get(url, params=params, timeout=30)
    if resp.status_code == 429:
        wait = 5 * (attempt + 1)  # 5s, 10s, 15s
        time.sleep(wait)
        continue
    resp.raise_for_status()
    break
```

---

## Semantic Scholar API

**Endpoint**: `https://api.semanticscholar.org/graph/v1/paper/search`
**Auth**: API key recommended (`x-api-key` header, format: `s2k-...`)
**Rate limit**: 1 req/s without key, 100 req/5min with key
**Best for**: Citation counts, venue information, influential citations

### Query Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `query` | search terms | Plain text query |
| `limit` | `min(max_results, 100)` | Max 100 per request |
| `fields` | `title,authors,year,abstract,url,externalIds,citationCount,venue` | Comma-separated |

### Available Fields

- `title` — paper title
- `authors` — author list with names
- `year` — publication year
- `abstract` — abstract text (may be truncated)
- `url` — Semantic Scholar URL
- `externalIds` — DOI, ArXiv, MAG, PubMed, Corpus
- `citationCount` — total citation count
- `venue` — journal or conference name
- `publicationTypes` — JournalArticle, Conference, Review, etc.
- `influentialCitationCount` — citations from highly-cited papers

### Returned Fields Per Paper

```python
{
    "source": "semantic_scholar",
    "title": "...",
    "authors": ["Author Name", ...],
    "year": "2024",
    "abstract": "...",
    "url": "https://www.semanticscholar.org/paper/...",
    "arxiv_id": "XXXX.XXXXX",  # from externalIds.ArXiv
    "citations": 42,            # from citationCount
    "venue": "NeurIPS 2024",
}
```

### Error Handling

- 429 → rate limited, skip and return empty (don't retry — key likely invalid)
- Other errors → log warning, return empty
- Fallback: if key is invalid/missing, requests go through unauthenticated (lower limit)

---

## OpenAlex API

**Endpoint**: `https://api.openalex.org/works`
**Auth**: None (free, no key required); polite email in User-Agent recommended
**Rate limit**: 10 req/s (very generous)
**Best for**: Broad coverage, open access works, abstract reconstruction

### Query Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `search` | search terms | Full-text search |
| `per_page` | `min(max_results, 200)` | Max 200 per page |
| `sort` | `cited_by_count:desc` | Sort by citations (default for search-skill) |
| `filter` | `type:journal-article` | Optional: filter by type, year, venue, etc. |

### Abstract Reconstruction

OpenAlex stores abstracts as inverted indices for legal reasons. The search-skill reconstructs them:

```python
idx = p["abstract_inverted_index"]
# idx = {"word1": [pos1, pos3], "word2": [pos2], ...}
# Reconstruct by sorting all (position, word) pairs
words = sorted([(pos, word) for word, positions in idx.items() for pos in positions])
abstract = " ".join(w for _, w in words)
```

### Returned Fields Per Paper

```python
{
    "source": "openalex",
    "title": "...",
    "authors": ["Author Name", ...],
    "year": "2024",
    "abstract": "...",         # reconstructed from inverted index
    "url": "https://doi.org/...",  # DOI URL
    "arxiv_id": "...",         # extracted from primary_location URL
    "citations": 42,           # from cited_by_count
    "venue": "Nature Machine Intelligence",
}
```

### Additional Filters (Optional)

```
# Peer-reviewed journal articles only
filter=type:journal-article

# Recent papers
filter=from_publication_date:2023-01-01

# Specific venue
filter=primary_location.source.display_name:Nature

# Open access only
filter=open_access.is_oa:true
```

---

## Merge Strategy

After retrieving from all three sources, papers are merged and deduplicated:

```python
def _title_key(title: str) -> str:
    """Normalize title for dedup comparison."""
    return " ".join(title.lower().split())[:80]

def merge_results(all_papers: list[dict]) -> list[dict]:
    seen = {}
    # Process by abstract length ascending → longer abstracts win
    for p in sorted(all_papers, key=lambda x: len(x.get("abstract") or "")):
        key = _title_key(p["title"])
        seen[key] = p
    # Sort by citations descending
    return sorted(seen.values(), key=lambda x: x.get("citations") or 0, reverse=True)
```

### Merge Priorities
1. Keep entry with longest abstract (most informative)
2. Sort final list by citation count (most impactful first)
3. Preserve source tag on every entry

## Error Recovery Matrix

| Scenario | arXiv | Semantic Scholar | OpenAlex |
|----------|-------|-----------------|----------|
| Network timeout | Retry ×3 (3s wait) | Skip, return [] | Skip, return [] |
| Rate limit (429) | Retry ×3 with backoff | Skip, return [] | N/A (very high limit) |
| Auth failure (403) | N/A (no auth) | Fall back to no-key | N/A (no auth) |
| Parse error | Skip malformed entry | Skip malformed entry | Skip malformed entry |
| All sources fail | Raise error | — | — |

## Quick Test

```bash
cd /data/ResearchSkills/chen-search-skills
python shared/search_papers.py "transformer attention mechanism" -n 5 -o /tmp/test_search/
cat /tmp/test_search/literature_review.md | head -30
```
