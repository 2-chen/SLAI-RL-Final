# Literature Search Strategies

Query formulation techniques and search patterns for effective academic literature retrieval.

## Query Formulation

### From Topic to Query

A good search query balances specificity and coverage. Process:

1. **Extract key concepts** from the research topic
2. **Identify synonyms** for each concept
3. **Build Boolean queries** combining concepts
4. **Test and refine** based on result count and relevance

### Example Transformation

| Research Topic | Search Query |
|---------------|-------------|
| "Improving few-shot learning through adaptive prompt optimization for cross-domain NLP" | `few-shot learning AND prompt optimization AND cross-domain NLP` |
| "Diffusion models for molecular generation and drug discovery" | `diffusion model AND (molecule generation OR drug discovery)` |
| "Federated learning with differential privacy for medical imaging" | `federated learning AND differential privacy AND (medical imaging OR healthcare)` |

### Query Templates

```
# Broad search (more results)
<concept_1> <concept_2>

# Focused search (Boolean)
<concept_1> AND <concept_2> AND <concept_3>

# Synonym expansion
<concept_1> AND (<synonym_a> OR <synonym_b>)

# Exclusion (remove noise)
<concept_1> AND <concept_2> ANDNOT <noise_term>
```

## Search Expansion

When initial results are too few (<10 papers):

1. **Synonym expansion**: Add alternative terms for each concept
2. **Broader concepts**: Move up one level of abstraction
3. **Remove constraints**: Drop the most restrictive AND clause
4. **Language variants**: Try British vs American spelling

When results are too many (>100 papers):

1. **Add constraints**: Add year filter, venue filter, or method constraint
2. **Narrow concepts**: Use more specific terminology
3. **Add exclusion**: Filter out tangentially related areas

## Relevance Assessment

After retrieval, assess each paper's relevance to the research question:

| Level | Criteria | Action |
|-------|----------|--------|
| **Direct** | Same problem, same/similar method | Deep read |
| **High** | Same problem, different method OR different problem, same method | Read abstract + method |
| **Moderate** | Related problem or related method | Read abstract |
| **Low** | Tangentially connected | Note existence, skip details |
| **Background** | Citation-worthy but not directly applicable | Add to bibliography |

## Quality Filters

When prioritizing papers for deep reading:

1. **Citation count** — indicates impact (but biased toward older papers)
2. **Venue tier** — top conferences/journals have higher bar
3. **Recency** — newer papers reflect current state (CS/AI: ≤3 years)
4. **Author track record** — established researchers in the field
5. **Code availability** — papers with open-source code are more reproducible
6. **Replication status** — has the work been independently reproduced?

## Search Strategy Documentation

For reproducibility, document every search:

```markdown
## Search Strategy

**Topic**: Federated learning with differential privacy for medical imaging
**Date**: 2026-05-28

### Queries Used

1. `federated learning AND differential privacy AND medical imaging`
   - arXiv: 15 results, Semantic Scholar: 12 results, OpenAlex: 18 results
   
2. `federated learning AND healthcare AND privacy-preserving`
   - arXiv: 8 results, Semantic Scholar: 10 results, OpenAlex: 14 results

3. `(federated OR distributed) AND (differential privacy OR secure aggregation) AND (medical OR clinical)`
   - arXiv: 11 results, Semantic Scholar: 9 results, OpenAlex: 20 results

### Inclusion Criteria
- Published 2021-2026
- English language
- Peer-reviewed or high-quality preprint
- Addresses both federated learning AND privacy protection

### Exclusion Criteria
- Federated learning without privacy mechanism
- Differential privacy outside of federated/decentralized setting
- Non-medical/healthcare applications (unless method is directly transferable)
```

## Common Pitfalls

1. **Too narrow too early** — start broad, then narrow based on what exists
2. **Missing key synonyms** — "contrastive learning" vs "self-supervised learning" vs "representation learning"
3. **Ignoring adjacent fields** — methods often transfer across domains
4. **Over-relying on one source** — arXiv misses paywalled journal articles; S2 misses some preprints
5. **Citation count bias** — seminal papers dominate but newer work may be more relevant
6. **Not reading beyond the abstract** — abstracts can be misleading about actual contributions
