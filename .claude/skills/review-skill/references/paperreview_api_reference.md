# paperreview.ai API Reference

Complete reference for the paperreview.ai external review service used by review-skill.

## Overview

paperreview.ai provides automated AI peer review via a simple REST API. No browser needed. The service uses the Stanford Agentic Reviewer model.

**Base URL**: `https://paperreview.ai`

## 3-Step Upload Flow

### Step 1: Get Presigned Upload URL

```
POST /api/get-upload-url
Content-Type: application/json

{
    "filename": "paper.pdf",
    "venue": "AAAI"
}
```

**Success Response (200)**:
```json
{
    "success": true,
    "presigned_url": "https://s3.amazonaws.com/...",
    "presigned_fields": {
        "key": "uploads/xxx/paper.pdf",
        "AWSAccessKeyId": "...",
        "policy": "...",
        "signature": "..."
    },
    "s3_key": "uploads/xxx/paper.pdf"
}
```

### Step 2: Upload to S3

```
POST <presigned_url>
Content-Type: multipart/form-data

fields: <presigned_fields>
file: <PDF binary>
```

**Success**: HTTP 200 or 204

### Step 3: Confirm Upload

```
POST /api/confirm-upload
Content-Type: application/x-www-form-urlencoded

s3_key=uploads/xxx/paper.pdf&venue=AAAI&email=250010008@slai.edu.cn
```

**Success Response (200)**:
```json
{
    "success": true,
    "token": "pt_abc123def456"
}
```

The `token` is the review token. Save it — there's no way to recover it.

## Polling for Results

```
GET /api/review/{token}
```

**Still Processing (202)**:
```json
{
    "status": "processing"
}
```
→ Wait and retry.

**Review Ready (200)**:
```json
{
    "title": "Paper Title",
    "venue": "AAAI",
    "submission_date": "2026-05-28",
    "sections": {
        "summary": "...",
        "strengths": "...",
        "weaknesses": "...",
        "detailed_comments": "...",
        "questions": "...",
        "overall_assessment": "..."
    }
}
```

**Error (4xx/5xx)**: Check status code and retry with backoff.

## Verdict Extraction

The `extract_verdict()` function looks for the recommendation in this order:

1. Direct fields: `review["recommendation"]`, `review["verdict"]`, `review["decision"]`
2. Overal_assessment text: scans for patterns like `Recommendation: accept`
3. Returns `"unknown"` if nothing matches

Possible verdict values:
- `accept` — paper is ready
- `weak accept` / `borderline` — minor revisions needed
- `reject` — major issues

## Markdown Conversion

`review_to_markdown()` converts the review JSON to a structured markdown document with sections:
- Summary
- Strengths
- Weaknesses
- Detailed Comments
- Questions
- Overall Assessment
- Parsed Verdict

## Polling Strategy

Default parameters (from ChenResearch config):
- **Initial wait**: 300s (5 minutes) — paperreview.ai needs time to process
- **Poll interval**: 60s — check every minute
- **Max wait**: 7200s (2 hours) — timeout if review isn't ready

The poll loop:
```python
time.sleep(initial_wait)  # 300s
deadline = time.time() + max_wait  # +7200s
while time.time() < deadline:
    data = get_review(token)
    if data is not None:
        return data  # Ready!
    time.sleep(interval)  # 60s
raise TimeoutError("Review not ready")
```

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| `FileNotFoundError` | PDF doesn't exist | Verify path, ask user |
| `requests.ConnectionError` | Network down | Retry with backoff |
| `RuntimeError: get-upload-url failed` | Server rejected request | Check venue name, retry |
| `RuntimeError: S3 upload failed` | S3 presigned URL expired | Restart from Step 1 |
| `RuntimeError: confirm-upload failed` | Server rejected confirmation | Check email, retry |
| `TimeoutError` (poll) | Review took > 2h | Report token, user checks manually |

## Venue Options

Commonly used venues:
- `AAAI` — AAAI Conference on Artificial Intelligence
- `NeurIPS` — Neural Information Processing Systems
- `ICML` — International Conference on Machine Learning
- `ICLR` — International Conference on Learning Representations
- `CVPR` — Computer Vision and Pattern Recognition
- `ACL` — Association for Computational Linguistics

Default: `AAAI`

## Usage with Python

```python
import sys
sys.path.insert(0, '/data/ResearchSkills/chen-research-skills')
from shared.paperreview_api import submit_paper, poll_review, review_to_markdown, extract_verdict

# Submit
token = submit_paper("paper.pdf", email="250010008@slai.edu.cn", venue="AAAI")
print(f"Token: {token}")

# Poll
review = poll_review(token, initial_wait=300, interval=60, max_wait=7200)

# Convert to markdown and save
md = review_to_markdown(review)
with open("external.md", "w") as f:
    f.write(md)

# Get verdict
verdict = extract_verdict(review)
print(f"Verdict: {verdict}")
```

## Usage from Shell

```bash
cd /data/ResearchSkills/chen-research-skills

# Submit and get token
python -c "
from shared.paperreview_api import submit_paper
token = submit_paper('paper.pdf', venue='AAAI')
print(token)
"

# Poll with token from above
python -c "
from paperreview_api import poll_review, review_to_markdown, extract_verdict
review = poll_review('pt_xxx')
md = review_to_markdown(review)
with open('external.md', 'w') as f: f.write(md)
print(extract_verdict(review))
"
```

## Limitations

1. **No token recovery**: if you lose the token, you must re-submit
2. **PDF only**: only PDF files are accepted
3. **Rate limiting**: submitting too many papers in quick succession may be throttled
4. **No revision tracking**: paperreview.ai treats each submission independently
5. **Venue awareness**: the review style adapts to the venue, but venue names must match their expected format
