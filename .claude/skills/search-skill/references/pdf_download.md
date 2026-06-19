# PDF Download Reference

Strategies for acquiring paper PDFs from various sources.

## Download Priority

1. **arXiv PDF** — `https://arxiv.org/pdf/{arxiv_id}.pdf`
   - Always works for arXiv papers
   - No rate limiting if polite (3s between requests)
   - Example: `https://arxiv.org/pdf/2006.11239.pdf`

2. **DOI → Publisher PDF**
   - `https://doi.org/{doi}` resolves to publisher page
   - Some publishers allow direct PDF: replace `/10.xxx/` with `/pdf/10.xxx/`
   - Open Access papers: direct download; subscription: redirect to paywall

3. **Semantic Scholar URL**
   - S2 page often links to arXiv or publisher PDF
   - Parse the page for `arxiv.org/pdf/` or `.pdf` links

4. **OpenAlex DOI**
   - Same as DOI approach — resolve and follow

5. **Author homepage / institution page**
   - Many authors host PDFs on personal sites
   - Search: `{author_name} {paper_title} filetype:pdf`

## Paywall Handling

| Publisher | OA Policy | Workaround |
|-----------|-----------|------------|
| IEEE | Most paywalled | Check author's institution page |
| ACM | Author can post author-version | Search for author's copy |
| Springer | Hybrid OA | Check for "Open Access" badge |
| Elsevier | Hybrid OA | Green OA: author can post preprint |
| NeurIPS/ICML/ICLR | Always free | Direct download from proceedings |
| AAAI | Always free | Direct from aaai.org |

**Policy**: Never attempt to bypass paywalls. Log paper as "paywalled" and suggest:
- Check the author's institutional page
- Look for a preprint on arXiv
- Use institutional library access

## Rate Limiting

- **Between requests**: 3 seconds minimum
- **Concurrent downloads**: Max 3 threads
- **Retry on failure**: 3 retries with exponential backoff (3s, 9s, 27s)
- **User-Agent**: Identify as `search-skill/2.0 (mailto:250010008@slai.edu.cn)`

## File Naming Convention

```
{first_author_lastname}_{year}_{first_three_words_of_title}.pdf
```

Examples:
- `song_2021_score_based_generative.pdf`
- `xu_2022_geodiff_geometric_diffusion.pdf`
- `ho_2020_denoising_diffusion_probabilistic.pdf`

Clean filenames: lowercase, replace spaces with underscores, remove special chars.

## Download Verification

After download, verify the file is a valid PDF:
```python
def is_valid_pdf(filepath: str) -> bool:
    with open(filepath, "rb") as f:
        header = f.read(5)
    return header == b"%PDF-"
```

## Edge Cases

- **Paper withdrawn from arXiv**: PDF still available, add `[WITHDRAWN]` note
- **arXiv PDF redirects to HTML abstract**: Some older arXiv papers. Try `arxiv.org/pdf/` first, fall back to `arxiv.org/abs/`
- **Very large PDF (>100MB)**: Ask user before downloading
- **Scanned PDF (not text-searchable)**: Download anyway, add note
