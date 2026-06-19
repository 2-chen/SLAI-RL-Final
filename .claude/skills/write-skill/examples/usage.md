# Write Skill — Usage Examples

## Example 1: Full Paper (AAAI 2026)

**User:**
```
Write an AAAI 2026 paper on "Improving Few-Shot Learning through Adaptive Prompt Optimization for Cross-Domain NLP".
I have experiment results in workspace/fewshot_prompt/experiment/results.json and a literature review in workspace/fewshot_prompt/literature/literature_review.md.
```

**Skill executes (full mode):**
1. **Config**: AAAI 2026, method paper, 7 pages + 2 for references. Materials: lit review + experiment results.
2. **Architecture**: Builds outline → user confirms.
3. **Draft**: Writes complete 9-page paper — abstract, intro (5 paragraphs), related work (4 topic clusters), method (3 modules), experiments (3 datasets, 6 baselines), conclusion.
4. **Figures**: Generates 4 figures — method overview (full-width schematic), main results bar chart, ablation study bar chart, t-SNE visualization.
5. **Tables**: 2 tables — main comparison (booktabs), ablation study.
6. **Polish**: Cuts 200 words to fit page limit, adjusts claim verbs, removes 12 "furthermore"/"moreover" instances.
7. **Compile**: `pdflatex → bibtex → pdflatex → pdflatex`. 9 pages. 0 citation errors. PDF ready.

**Output:**
```
workspace/fewshot_prompt/paper/
├── paper.tex
├── references.bib
├── figures/
│   ├── method_overview.pdf
│   ├── main_results.pdf
│   ├── ablation.pdf
│   └── tsne_visualization.pdf
├── aaai2026.sty
├── aaai2026.bst
├── paper.pdf
└── build.sh
```

## Example 2: Write Only the Introduction

**User:**
```
Write the introduction for my NeurIPS paper on "Diffusion Models for Molecular Conformation Generation".
The paper proposes GeoDiff, a diffusion model that operates directly on 3D molecular coordinates.
SOTA methods (CVGAE, GraphDG, ConfVAE) either produce unrealistic geometries or are too slow.
```

**Skill executes (section mode):**
1. Reads paper context from user description
2. Drafts 5-paragraph introduction:
   - P1: Molecular conformation generation is critical for drug discovery
   - P2: Existing methods trade off between accuracy and speed
   - P3: Prior work (CVGAE, GraphDG, ConfVAE) — what they do, what they miss
   - P4: GeoDiff: diffusion on 3D coordinates, key insight
   - P5: Contributions (3 items): (1) first diffusion model for conformer generation, (2) achieves SOTA on GEOM-QM9 and GEOM-Drugs, (3) 100× faster than ConfVAE

## Example 3: Generate Figures

**User:**
```
Generate figures for my paper. I have these results:
- Main comparison: Method A=72.3, Method B=74.1, Method C=76.8, Ours=78.9 on Dataset X
- Ablation: removing component A drops to 70.1, removing B to 73.5, removing C to 76.8
- Training curves: loss values from logs/training.json
```

**Skill executes (figures mode):**
1. Establishes contracts for 3 figures
2. Generates Python code with nature-figure rcParams
3. Renders PDFs: `main_results.pdf`, `ablation.pdf`, `training_curves.pdf`
4. Provides LaTeX integration:
```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{figures/main_results.pdf}
  \caption{Comparison with state-of-the-art methods on Dataset X.}
  \label{fig:main_results}
\end{figure}
```

## Example 4: Polish Existing Draft

**User:**
```
Polish this paper draft: workspace/my_paper/paper.tex
It's currently 10 pages but the AAAI limit is 7+2. Also the writing feels "LLM-generated."
```

**Skill executes (polish mode):**
1. Reads paper, identifies structural issues:
   - Introduction too long (1.5 pages → should be ~1 page)
   - Related work is a paper-by-paper catalog
   - 14 instances of "furthermore"/"moreover"
   - Conclusion restates abstract
2. Applies cuts:
   - Shortens intro: merges paragraphs 2-3, removes redundant examples
   - Rewrites related work: groups by topic, adds limitation pivots
   - Condenses method: moves implementation details to appendix
3. Cleans language:
   - Replaces hedging pileups
   - Calibrates claim verbs
   - Removes formulaic transitions
4. Output: 8.5 pages (7 + 1.5 refs). Reports: "Cut 1.5 pages, removed 38 instances of AI-writing markers."

## Example 5: Plan Mode — Guided Outline

**User:**
```
Help me plan a paper. I have results on "Test-Time Adaptation for Medical Image Segmentation" but I don't know how to structure the paper.
```

**Skill executes (plan mode):**
```
Q: What's the one-sentence argument of your paper?

User: TTA methods work for natural images but fail on medical images 
      because of domain-specific challenges — we identify these challenges 
      and propose fixes.

Q: What's your strongest piece of evidence?

User: On 3 medical imaging benchmarks (BraTS, ACDC, M&Ms), our method 
      improves segmentation Dice by 5-8% over standard TTA.

Q: What's the boundary of your claim?

User: We only tested on MRI, not CT or X-ray. And we assume source model is available.

→ Produces outline:
  1. Introduction (1 page)
     - Medical image segmentation challenge → domain shift in deployment
     - TTA promise + failure on medical data → 3 specific challenges
     - Our approach: diagnose + fix → 5-8% Dice improvement
  2. Related Work (0.7 pages)
     - Medical image segmentation, domain adaptation, test-time adaptation
  3. Method (2 pages)
     - Preliminaries: TTA for segmentation
     - Challenge 1 + fix, Challenge 2 + fix, Challenge 3 + fix
  4. Experiments (2.5 pages)
     - Setup (3 datasets, 6 baselines)
     - Main results, per-challenge ablation, qualitative
  5. Discussion (0.5 pages)
     - Why standard TTA fails on medical images
     - Limitations (MRI only, source model dependency)
  6. Conclusion (0.3 pages)

  Figure plan: method overview (full-width), main results bar chart, 
               qualitative comparison, challenge-specific analysis

→ Ready to write? Switch to full mode or draft-only.
```

## Example 6: Compile and Debug

**User:**
```
Compile my paper: workspace/my_paper/paper.tex (NeurIPS 2026)
```

**Skill executes (compile mode):**
```
=== Compiling paper.tex (NeurIPS 2026) ===

Run 1: pdflatex ... 3 warnings
Run 2: bibtex ... OK
Run 3: pdflatex ... 1 warning
Run 4: pdflatex ... 0 warnings

Pages: 8 (limit: 9) ✓

Warnings:
  - Overfull \hbox (lines 234-236): equation exceeds text width
  - Citation "smith2023" undefined → missing from references.bib

Fixes applied:
  - Line 234: split equation across two lines with \begin{aligned}
  - Added "smith2023" entry to references.bib from DOI lookup

Recompiled: 8 pages, 0 warnings, 0 citation errors.

Output: workspace/my_paper/paper.pdf ✓
```
