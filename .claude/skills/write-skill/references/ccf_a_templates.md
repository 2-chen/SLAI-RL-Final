# CCF-A Conference LaTeX Template Reference

Venue-specific LaTeX requirements, page limits, and compilation details for major CCF-A AI conferences.

## AAAI 2026

**Page limit**: 7 pages + 2 pages for references only (9 total)
**Template files**: `aaai2026.sty`, `aaai2026.bst`
**Document class**: `article`

```latex
\documentclass[letterpaper]{article}
\usepackage[submission]{aaai2026}

% Required packages
\usepackage{times}
\usepackage{helvet}
\usepackage{courier}
\usepackage{natbib}
\usepackage{caption}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{url}

% BANNED
% geometry, fullpage, setspace, titlesec, float, authblk, ulem, hyperref
% Note: AAAI prohibits hyperref

% Title
\title{Paper Title}
\author{Author One\textsuperscript{\rm 1}, Author Two\textsuperscript{\rm 2}}
\affiliations{
    \textsuperscript{\rm 1} Institution One, City, Country \\
    \textsuperscript{\rm 2} Institution Two, City, Country
}

\begin{document}
\maketitle
\begin{abstract}
...
\end{abstract}
```

**Compilation**:
```bash
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

**Key rules**:
- Single-blind review (author names visible)
- No page numbers
- No hyperref — citations are plain text
- References count toward the 2-page reference limit

---

## NeurIPS 2026

**Page limit**: 9 pages + unlimited appendix after references
**Template**: `neurips_2026.sty`

```latex
\documentclass{article}
\usepackage[preprint]{neurips_2026}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{hyperref}
\usepackage{url}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{graphicx}
\usepackage{natbib}

\title{Paper Title}
\author{Anonymous Author(s)}
\begin{document}
\maketitle
\begin{abstract}
...
\end{abstract}
```

**Key rules**:
- **Double-blind** — author names must be anonymized
- NeurIPS requires `\usepackage[preprint]{neurips_2026}` for submission
- Final version uses `\usepackage[final]{neurips_2026}`
- Acknowledgements in `\begin{ack}` environment

---

## ICML 2026

**Page limit**: 8 pages + unlimited appendix
**Template**: `icml2026.sty`

```latex
\documentclass{article}
\usepackage{icml2026}

% Required
\usepackage{natbib}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{graphicx}
```

**Key rules**:
- **Double-blind** — anonymize author list
- No author names in PDF metadata
- References in `\bibliographystyle{icml2026}`

---

## CVPR 2026

**Page limit**: 8 pages + unlimited references
**Template**: `cvpr.sty`

```latex
\documentclass[review]{cvpr}
\usepackage[review]{cvpr}

\usepackage{times}
\usepackage{epsfig}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{booktabs}

\def\cvprPaperID{****}
\def\confName{CVPR}
\def\confYear{2026}
```

**Key rules**:
- **Double-blind** — anonymize
- Paper ID required for submission
- CVPR provides its own `cvpr.sty` and `ieee_fullfirstname.bst`

---

## ACL 2026

**Page limit**: 8 pages + 4 pages appendix + unlimited references
**Template**: `acl.sty`

```latex
\documentclass[11pt,a4paper]{article}
\usepackage[review]{acl}

\usepackage{times}
\usepackage{latexsym}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{microtype}
\usepackage{amsmath}
\usepackage{graphicx}
```

**Key rules**:
- **Double-blind**
- `\usepackage[review]{acl}` for submission
- `\usepackage{acl}` for final
- `\includepdf` for appendix inclusion

---

## ICLR 2026

**Page limit**: 8 pages + unlimited appendix
**Template**: `iclr2026.sty`

```latex
\documentclass{article}
\usepackage{iclr2026}
\usepackage{times}
\usepackage{natbib}
\usepackage{hyperref}
\usepackage{amsmath}
```

**Key rules**:
- **Double-blind**
- OpenReview submission (no paper ID needed)
- `\usepackage{iclr2026}` for both submission and final

---

## IJCAI 2026

**Page limit**: 7 pages + 2 pages references = 9 total
**Template**: `ijcai2026.sty`

```latex
\documentclass{article}
\usepackage{ijcai2026}
```

**Key rules**:
- **Double-blind**
- Author names in separate `\author{}` and `\affiliation{}` commands
- No hyperref

---

## Cross-Venue Preamble Checklist

### Always Allowed
- `times`, `helvet`, `courier`
- `natbib`, `caption`, `graphicx`
- `amsmath`, `amssymb`, `amsfonts`
- `booktabs`
- `subcaption` (most venues)
- `multirow`, `array`
- `xcolor` (with `table`, `dvipsnames` options)
- `algorithm`, `algorithmic` (or `algorithm2e`)

### Venue-Dependent
| Package | AAAI | NeurIPS | ICML | CVPR | ACL | ICLR |
|---------|------|---------|------|------|-----|------|
| `hyperref` | **BANNED** | Allowed | Allowed | Allowed | Allowed | Allowed |
| `geometry` | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** |
| `authblk` | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** | Allowed |
| `fullpage` | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** |
| `setspace` | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** |
| `titlesec` | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** |
| `float` | **BANNED** | **BANNED** | **BANNED** | **BANNED** | Allowed | Allowed |
| `ulem` | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** | **BANNED** |

---

## Compilation Script (build.sh)

```bash
#!/usr/bin/env bash
set -euo pipefail

PAPER="${1:-paper}"
VENUE="${2:-aaai2026}"
TEXFILE="${PAPER}.tex"

echo "=== Compiling ${PAPER}.tex (${VENUE}) ==="

# Copy style files
cp templates/"${VENUE}".sty . 2>/dev/null || true
cp templates/"${VENUE}".bst . 2>/dev/null || true

# Compile
pdflatex -interaction=nonstopmode "${TEXFILE}"
bibtex "${PAPER}" 2>/dev/null || echo "(no bibliography needed)"
pdflatex -interaction=nonstopmode "${TEXFILE}"
pdflatex -interaction=nonstopmode "${TEXFILE}"

# Page count
PAGES=$(pdfinfo "${PAPER}.pdf" 2>/dev/null | grep Pages | awk '{print $2}')
echo "Pages: ${PAGES}"

# Warning summary
echo ""
echo "=== Warnings ==="
grep -c "Warning" "${PAPER}.log" 2>/dev/null || echo "0"
grep "LaTeX Warning" "${PAPER}.log" 2>/dev/null || true
grep "Overfull" "${PAPER}.log" 2>/dev/null || true
grep "Citation.*undefined" "${PAPER}.log" 2>/dev/null || true

echo ""
echo "=== Done ==="
echo "Output: ${PAPER}.pdf"
```

---

## Page-Limit Warning Thresholds

When compiling, warn the user at these thresholds:

| Venue | Warn at | Critical at |
|-------|---------|-------------|
| AAAI | 7 pages + 2 refs | 7 pages + 3 refs |
| NeurIPS | 9 pages | 10 pages |
| ICML | 8 pages | 9 pages |
| CVPR | 8 pages | 9 pages |
| ACL | 8 pages + 4 appendix | 8 pages + 5 appendix |
| ICLR | 8 pages | 9 pages |
| IJCAI | 7 pages + 2 refs | 7 pages + 3 refs |

When the paper hits the "warn at" threshold, suggest cuts: shorten related work, move details to appendix, condense figure captions, reduce verbose transitions.
