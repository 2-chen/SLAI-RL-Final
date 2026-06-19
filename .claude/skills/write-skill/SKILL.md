---
name: write-skill
description: "CCF-A conference paper writing skill — produces LaTeX manuscripts targeting top AI conferences (NeurIPS, ICML, AAAI, CVPR, ACL, etc.) with publication-quality figures, professional tables, rigorous academic expression, and strict page-limit compliance. Covers the full pipeline: section architecture → argument construction → full draft → figure/table generation → polishing → LaTeX compilation → PDF output. 7 modes: full, draft-only, section, figures, polish, compile, plan. Triggers on: write paper, write LaTeX paper, CCF paper, conference paper, draft paper, 写论文, 写会议论文, 撰写论文, LaTeX写作."
metadata:
  version: "1.0"
  last_updated: "2026-05-28"
---

# Write Skill — CCF-A Conference Paper Writing

Writes LaTeX manuscripts targeting CCF-A AI conferences. Combines structured academic writing patterns (from nature-writing), publication-quality figure generation (from nature-figure), rigorous language polishing (from nature-polishing), and multi-format LaTeX compilation (from academic-paper) into a single focused writing pipeline.

## Quick Start

**Minimal command:**
```
Write a paper on "Diffusion Models for Molecular Graph Generation"
```

**With venue specified:**
```
Write a NeurIPS 2026 paper on "Federated Learning with Differential Privacy for Medical Imaging"
```

**From existing research materials:**
```
Write paper from workspace/my_research/ — use the literature review and experiment results
```

**Execution flow:**
1. Config — venue, paper type, page budget, existing materials
2. Architecture — section outline, claim-evidence chain, figure/table plan
3. Draft — section-by-section writing with academic register
4. Figures & Tables — publication-quality generation
5. Polish — language refinement to Nature-level clarity
6. Compile — LaTeX → PDF, citation check, page-limit verification

---

## Trigger Conditions

### Trigger Keywords

**English**: write paper, write LaTeX paper, CCF paper, conference paper, AAAI paper, NeurIPS paper, ICML paper, CVPR paper, ACL paper, draft paper, draft manuscript, write manuscript, paper writing, academic writing, conference submission, compile LaTeX, format paper, generate figures for paper, write section, polish paper

**繁體中文**: 寫論文, 寫會議論文, 撰寫論文, LaTeX寫作, 論文寫作, CCF論文, 寫LaTeX, 論文排版, 論文圖表, 論文潤色, 寫草稿, 生成圖表

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Literature search / finding references | `search-skill` |
| Peer review of a paper | `review-skill` |
| Running GPU experiments | `experiment-skill` |
| Full research-to-publication pipeline | `pipeline-skill` |

---

## CCF-A Venue Quick Reference

| Venue | Page Limit | Extra Pages | Template | Style File | Deadline Pattern |
|-------|-----------|-------------|----------|------------|-----------------|
| **NeurIPS** | 9 pages | unlimited appendix | `neurips_2026.sty` | `\usepackage[preprint]{neurips_2026}` | May abstract, Sep full |
| **ICML** | 8 pages | unlimited appendix | `icml2026.sty` | `\usepackage{icml2026}` | Jan abstract, Feb full |
| **AAAI** | 7 pages + 2 refs | none | `aaai2026.sty` | `\usepackage[submission]{aaai2026}` | Aug abstract, Sep full |
| **CVPR** | 8 pages | unlimited refs | `cvpr.sty` | `\documentclass[review]{cvpr}` | Nov abstract, Mar full |
| **ACL** | 8 pages + 4 appendix | unlimited refs | `acl.sty` | `\usepackage{acl}` | Feb abstract, Jun full |
| **ICLR** | 8 pages | unlimited appendix | `iclr2026.sty` | `\usepackage{iclr2026}` | Sep full |
| **IJCAI** | 7 pages + 2 refs | none | `ijcai2026.sty` | `\usepackage{ijcai2026}` | Jan abstract, Feb full |
| **KDD** | 9 pages | none | `kdd.sty` | `\usepackage{kdd}` | Feb full |
| **SIGIR** | 9 pages | none | `sigir.sty` | `\usepackage{sigir}` | Feb full |
| **MM** | 8 pages + 2 refs | none | `acmmm.sty` | `\usepackage{acmmm}` | Apr full |

When the user specifies a CCF-A venue, the skill loads the corresponding template defaults. If no venue is specified, defaults to AAAI 2026 format. The `templates/` directory contains starter `.sty` and `.tex.j2` files for each venue.

---

## Modes

| Mode | Trigger | What It Does |
|------|---------|-------------|
| `full` | "write a paper", "写论文" | Complete pipeline: config → architecture → draft → figures → polish → compile |
| `draft-only` | "draft paper", "write draft" | Architecture → full-text draft (no figure generation, no compile) |
| `section` | "write introduction", "write method" | Write or rewrite a single section with architecture alignment |
| `figures` | "generate figures", "make charts" | Figure contract → generation → LaTeX integration |
| `polish` | "polish paper", "refine language" | Language polish to Nature-level clarity and conciseness |
| `compile` | "compile paper", "build PDF" | LaTeX compilation + citation check + page-limit verification |
| `plan` | "plan paper", "paper outline" | Socratic chapter-by-chapter outline planning (no drafting) |

Default mode: `full`.

---

## Workflow Detail

### Mode: full — Complete Paper

**Phase 0: Configuration**
1. Identify the target venue (CCF-A conference or "general")
2. Confirm paper type: method paper (default for AI), resource, survey, or theoretical
3. Assess existing materials: literature review, experiment results, figures, drafts
4. Set page budget and word count targets per section
5. Produce a configuration summary for user confirmation

**Phase 1: Architecture**
1. Build the central argument chain:
   ```
   field problem → bottleneck → prior work gap → our approach → evidence → implication → boundary
   ```
2. Design section outline with word budget:
   | Section | % of total | Typical length (8-page paper) |
   |---------|-----------|-------------------------------|
   | Abstract | 4% | ~150-200 words |
   | Introduction | 15% | ~700-900 words |
   | Related Work | 10% | ~450-600 words |
   | Method | 25% | ~1200-1500 words |
   | Experiments | 30% | ~1400-1800 words |
   | Discussion / Analysis | 8% | ~400-500 words |
   | Conclusion | 3% | ~150-200 words |
   | References | 5% | ~1 page |
3. Plan figure and table placement:
   - Method overview figure (1 page wide, schematic)
   - Main results table (comparison with baselines)
   - Ablation study figure/table
   - Qualitative/visualization figure (if applicable)
4. Map evidence to each claim — no unsupported assertion

**Phase 2: Section-by-Section Drafting**

Each section follows a specific architecture drawn from nature-writing patterns:

*Abstract* — `context → problem → gap → approach → key result → implication → boundary`:
- Open with the field-scale problem
- State why current approaches fail to fully solve it
- Present the core contribution in one sentence
- Report the strongest quantitative result
- Close with implication, not generic "promising results"

*Introduction* — `field stake → bottleneck → prior attempts → unresolved gap → present study`:
- Paragraph 1: field context + urgency
- Paragraph 2: bottleneck + limitations of existing approaches
- Paragraph 3: what this paper does + how it addresses the gap
- Paragraph 4: contributions (numbered list, 3-4 items)

*Related Work* — topic synthesis, not paper-by-paper list:
- Group by technical topic and mechanism
- Each paragraph: `topic scope → representative methods → limitation → distinction from our work`
- Use "Unlike [method] which [limitation], our approach [advantage]"

*Method* — pipeline from overview to details:
- Opening: overview figure + one-paragraph pipeline description
- Then: module 1, module 2, module 3, ...
- Each module: motivation → design → technical advantage → implementation detail
- Use `\begin{figure*}[t]` for method overview

*Experiments* — evidence ladder:
- Setup: datasets, baselines, metrics, implementation details
- Main results: comparison table against SOTA
- Ablation: component contribution analysis
- Analysis: qualitative results, case studies, error analysis
- Claim-first opening for each subsection: "To test [X], we [Y]."

*Conclusion* — bounded contribution:
- Central advance in one sentence
- Key evidence summary
- Limitation statement
- Plausible future direction

**Phase 3: Figures & Tables**

For each planned figure, establish a contract before generating code:
1. Core conclusion: one-sentence claim the figure defends
2. Evidence chain: map each panel to the claim
3. Journal/export spec: dimensions, format (PDF for LaTeX `\includegraphics`), font consistency

Figure generation follows nature-figure standards:
```python
import matplotlib as mpl
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Times New Roman", "DejaVu Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
})
```

Tables use `booktabs` style — no vertical rules, minimal horizontal rules:
```latex
\usepackage{booktabs}
\begin{table}[t]
  \centering
  \caption{Comparison with state-of-the-art methods.}
  \label{tab:main}
  \begin{tabular}{@{}lcccc@{}}
    \toprule
    Method & Metric A & Metric B & Metric C & Avg \\
    \midrule
    Baseline 1 & 72.3 & 68.1 & 81.2 & 73.9 \\
    Baseline 2 & 74.1 & 70.3 & 82.5 & 75.6 \\
    \textbf{Ours} & \textbf{78.9} & \textbf{74.2} & \textbf{85.1} & \textbf{79.4} \\
    \bottomrule
  \end{tabular}
\end{table}
```

**Phase 4: Polish**

Apply nature-polishing standards:
- Every sentence carries one clear message
- Claims are calibrated: `show` > `demonstrate` > `suggest` > `indicate` > `may` > `could`
- No unsupported novelty claims ("first", "novel", "revolutionary" without evidence)
- Conciseness: remove hedging pileups, "delve into", "leverage", "furthermore" overuse
- Paragraph-flow check: one paragraph = one message, strong opening sentence
- Reader empathy: relevance → novelty → trust → reuse → meaning

**Phase 5: Compilation**
1. Ensure LaTeX preamble includes required packages:
   ```latex
   \usepackage{times, helvet, courier}
   \usepackage{natbib, caption, graphicx, booktabs}
   \usepackage{amsmath, amssymb, amsfonts}
   \usepackage[colorlinks,citecolor=blue,linkcolor=red]{hyperref}
   ```
2. Banned packages per most CCF-A templates:
   `geometry`, `fullpage`, `setspace`, `titlesec`, `float`, `authblk`, `ulem`
3. Run `pdflatex → bibtex → pdflatex → pdflatex` compilation sequence
4. Check:
   - Page limit compliance (warn if over)
   - All citations resolve (no `[?]` markers)
   - All figures and tables referenced in text
   - No overfull hbox warnings
5. Report: compilation status, page count, warning summary

### Mode: draft-only

Phases 1-2 only: architecture → full draft. No figure generation or compilation. Output: `.tex` file ready for figures and compilation.

### Mode: section

Write or rewrite a single named section. Load the existing paper context. Apply the section-specific architecture from Phase 2. Ensure alignment with neighboring sections (transition sentences).

### Mode: figures

1. Read the paper context (or user-provided data)
2. Establish figure contract for each planned figure
3. Generate Python/R plotting code
4. Render to PDF (LaTeX-compatible)
5. Provide `\includegraphics` code with proper `\label` and `\caption`

### Mode: polish

1. Read the paper text
2. Apply Phase 4 polishing rules
3. Rebuild weak paragraphs using reverse outlining
4. Check claim calibration, conciseness, flow
5. Output polished `.tex` with change notes

### Mode: compile

1. Run Phase 5 compilation
2. Report compilation status, page count, warnings
3. If compilation fails, diagnose and fix LaTeX errors

### Mode: plan

1. Socratic interview to refine paper concept
2. Output: detailed section outline + argument blueprint + figure/table plan
3. No prose drafted — ready for user review before writing

---

## LaTeX Quality Standards

### Preamble Requirements

```latex
\documentclass[review]{<venue_class>}

% Required
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{helvet}
\usepackage{courier}
\usepackage{natbib}
\usepackage{caption}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{hyperref}

% Conditionally allowed (check venue)
\usepackage{subcaption}
\usepackage{multirow}
\usepackage{array}
\usepackage{xcolor}
\usepackage{algorithm}
\usepackage{algorithmic}
```

### Figure Integration

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{figures/method_overview.pdf}
  \caption{Overview of the proposed method. (a) ... (b) ... (c) ...}
  \label{fig:overview}
\end{figure}
```

- Use PDF vector format for all figures
- Font sizes in figures must match body text (8pt)
- All subfigures labeled with (a), (b), (c)
- Captions are self-contained mini-abstracts

### Table Standards

- `booktabs` style only: `\toprule`, `\midrule`, `\bottomrule`
- No vertical rules (`|` in tabular preamble)
- Bold best results per column
- Underline second-best (convention varies by venue)
- Sorted by primary metric descending

### Citation Format

- Use `\citep{}` for parenthetical, `\citet{}` for textual
- All citations in `references.bib` — no hardcoded references
- BibTeX entries include: author, title, year, venue, DOI (if available)

---

## Output Structure

```
<workspace>/paper/
├── paper.tex              # Main LaTeX source
├── references.bib         # BibTeX bibliography
├── figures/               # All figures in PDF format
│   ├── method_overview.pdf
│   ├── main_results.pdf
│   ├── ablation.pdf
│   └── qualitative.pdf
├── tables/                # Table source (.tex fragments)
│   ├── main_comparison.tex
│   └── ablation_table.tex
├── <venue>.sty            # Conference style file
├── <venue>.bst            # Bibliography style file
├── paper.pdf              # Compiled PDF
└── build.sh               # Compilation script
```

---

## Safety & Quality Rules

1. **Never fabricate results** — all data must come from user-provided experiments or literature
2. **Claim calibration** — match claim verbs to evidence strength; "show" requires statistical significance
3. **Page-limit compliance** — warn if draft exceeds venue limit; suggest cuts
4. **Citation integrity** — every claim referencing prior work must have a citation; no unsupported assertions
5. **Figure reproducibility** — provide the Python/R code that generated every figure
6. **Template compliance** — always use the venue-specific style file; check banned package list
7. **No AI-generation markers** — avoid phrase patterns that signal LLM generation (hedging pileups, excessive "furthermore"/"moreover", formulaic transitions)
8. **Single-source truth** — the `.tex` file is the canonical source; all changes go through it

## Reference Loading

- Read [ccf_a_templates.md](references/ccf_a_templates.md) for venue-specific LaTeX template requirements
- Read [writing_patterns.md](references/writing_patterns.md) for section-level writing architectures and examples
- Read [figure_table_design.md](references/figure_table_design.md) for publication-quality figure and table standards
