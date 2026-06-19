# Data Resource Search Reference

Platforms and strategies for discovering and downloading research datasets.

## Data Search Platforms

### PapersWithCode
```
GET https://paperswithcode.com/api/v1/datasets/?q={task_name}
GET https://paperswithcode.com/api/v1/evaluation-tables/?task={task_id}
```
- Best for: ML benchmark datasets, SOTA results, task→dataset mapping
- Rate limit: Polite use, no hard limit

### HuggingFace Datasets
```
GET https://huggingface.co/api/datasets?search={query}&sort=downloads&limit=20
```
- Best for: NLP, vision, audio ML datasets
- Provides: download count, license, size, format, loading code
- Download: `datasets.load_dataset("{dataset_name}")`

### Kaggle Datasets
```
GET https://www.kaggle.com/api/v1/datasets?search={query}&sortBy=votes
```
- Best for: Competition datasets, diverse domains
- Download: requires Kaggle API key (`~/.kaggle/kaggle.json`)
- `kaggle datasets download {owner/dataset_name}`

### Zenodo
```
GET https://zenodo.org/api/records?q={query}&access_right=open&size=20
```
- Best for: Academic research data, DOI-citable datasets
- All Zenodo datasets have DOIs — easy to cite
- Download: direct URL from record metadata

### Google Dataset Search (WebSearch fallback)
- Use WebSearch with `site:datasetsearch.research.google.com {query}`
- Best for: Discoverability across all platforms
- Not for direct download — find the hosting platform, then use its API

## Relevance Ranking

For each dataset found:

| Level | Criteria | Example |
|-------|----------|---------|
| **BENCHMARK** | Used as primary benchmark by ≥3 papers in lit review | ImageNet for image classification |
| **IN_USE** | Used by 1-2 papers in lit review | A custom dataset from a specific paper |
| **RELATED** | Same task/domain, not in lit review but standard | COCO for object detection (when lit review is about medical imaging) |
| **GENERIC** | Large-scale dataset usable but not domain-specific | CommonCrawl for any NLP task |

## Download Strategy

| Size | Action |
|------|--------|
| <100 MB | Auto-download directly |
| 100 MB – 1 GB | Auto-download with progress indicator |
| 1 GB – 10 GB | Ask user confirmation, then download |
| >10 GB | Provide download instructions + script. Do NOT auto-download. |
| API-gated | Provide registration link + API key setup instructions |

## License Awareness

Critical: datasets have licenses that affect paper usage.

| License | Can Use for Research | Can Redistribute | Must Cite |
|---------|---------------------|------------------|-----------|
| CC-BY 4.0 | ✓ | ✓ | ✓ |
| CC-BY-SA 4.0 | ✓ | ✓ (same license) | ✓ |
| CC-BY-NC 4.0 | ✓ (non-commercial) | ✓ | ✓ |
| CC0 (public domain) | ✓ | ✓ | Optional |
| MIT | ✓ | ✓ | Optional |
| Custom research-only | ✓ | ✗ (check terms) | ✓ |
| No license specified | Ask permission | ✗ | ✓ |
| GDPR-covered (personal data) | Requires ethics approval | ✗ | ✓ |

**Always flag**: datasets with no license, personal data, or commercial restrictions.

## Data Citation Format

For each dataset, produce a citable reference:
```bibtex
@misc{dataset_name,
  title = {Dataset Full Name},
  author = {Creators},
  year = {YYYY},
  publisher = {Platform/Institution},
  doi = {DOI if available},
  url = {Download URL},
  note = {License: CC-BY 4.0}
}
```

## Cross-Reference with Literature

For each dataset, check which papers in the user's literature review use it. This establishes:
- **Benchmark status**: if multiple SOTA papers evaluate on it
- **Expected baseline performance**: what numbers should the user target
- **Fair comparison**: ensures the user's experiments are comparable

```markdown
### Dataset: GEOM-QM9
**Used by**:
- Song et al. (2021) — baseline NLL: 1.23
- Xu et al. (2022) — baseline NLL: 0.98
- Ho et al. (2020) — baseline NLL: 1.45
→ Target for new method: NLL < 0.98
```

## Common Pitfalls

1. **Expired download links**: Verify each URL resolves before writing it to the index
2. **Version mismatch**: Some datasets have multiple versions — note which version papers use
3. **Requires preprocessing**: Raw datasets may need significant preprocessing. Note this.
4. **Regional restrictions**: Some datasets (medical especially) are region-locked
5. **Size underestimation**: Platform-reported sizes may be compressed; actual size can be 3-5× larger
