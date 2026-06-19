# GitHub Repository Search Reference

Strategies for finding open-source implementations of research papers.

## API Endpoints

### Search Repositories
```
GET https://api.github.com/search/repositories
  ?q={title_keywords}+{author_name}+in:readme
  &sort=stars
  &per_page=5
```

### Rate Limits
- Unauthenticated: 60 requests/hour
- With `GITHUB_TOKEN`: 5000 requests/hour
- Search endpoint is rate-limited separately: 10 req/min (unauth), 30 req/min (auth)

Set via environment: `export GITHUB_TOKEN=ghp_xxxxxxxxxxxx`

## Query Construction

### By Paper
```python
# Extract key elements
title_keywords = " ".join(paper["title"].split()[:6])  # first 6 words
first_author_lastname = paper["authors"][0].split()[-1]

# Build query
query = f"{title_keywords} {first_author_lastname} in:readme"
```

### By Topic
```python
# Find implementations for a method, not a specific paper
query = f"{method_name} implementation pytorch"
```

### Advanced Filters
```
# Official implementations only (less likely to be forks)
{query} NOT fork:only

# Recently active
{query} pushed:>2024-01-01

# Specific language
{query} language:python

# With specific file (e.g., requirements.txt present)
{query} filename:requirements.txt
```

## Confidence Scoring

| Signal | Score | Weight |
|--------|-------|--------|
| Repository owner matches paper author name | +40 | HIGH |
| Paper title appears verbatim in README | +30 | HIGH |
| "Official implementation" in README | +30 | HIGH |
| Repository name matches paper acronym | +25 | MEDIUM |
| arXiv ID or DOI in README | +20 | MEDIUM |
| Stars > 100 + relevant keywords | +15 | MEDIUM |
| Stars < 10, keyword match only | +5 | LOW |
| Fork of another result | -20 | LOW |
| No README or empty README | -10 | LOW |

**Confidence levels**: HIGH (≥60), MEDIUM (30-59), LOW (<30)

## Repo Quality Assessment

For each found repo, evaluate:

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| Stars | >100 | 10-100 | <10 |
| Last commit | <6 months | 6-12 months | >1 year |
| Requirements file | requirements.txt / environment.yaml | setup.py only | none |
| README | Detailed, with results | Brief | Empty |
| License | MIT / Apache 2.0 / BSD | GPL / custom | None |
| Issues | Active discussion | Some unanswered | Many stale |

## Output Enrichment

For each repo, collect additional context:
- **Installation complexity**: check requirements.txt for unusual deps
- **Hardware requirements**: look for `--batch_size`, `--gpus` in README
- **Pretrained models**: check for `.pth`, `.ckpt` download links
- **Reproducibility**: check for `--seed`, config files, Dockerfile

## Cloning Policy

- **Auto-clone**: repos with HIGH confidence + MIT/Apache license + <100MB
- **Ask first**: repos with MEDIUM confidence or >100MB
- **Skip**: repos with LOW confidence, no license, or >1GB

Clone command: `git clone --depth 1 https://github.com/{owner}/{repo}.git repos/{repo_name}/`

## Failure Recovery

| Issue | Action |
|-------|--------|
| No repos found for paper | Try broader query (remove author, search by method name) |
| All results are forks | Filter `NOT fork:only`, search again |
| Rate limited | Wait for reset time from `X-RateLimit-Reset` header |
| Repo archived/read-only | Note as "unmaintained" but still collect for reference |
| Private repo | Note, skip, suggest contacting author |
