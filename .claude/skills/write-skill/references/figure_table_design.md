# Publication-Quality Figure & Table Design

Standards for generating submission-grade figures and tables for CCF-A conferences.

## Figure Design Pipeline

### Step 1: Figure Contract (Before Any Code)

For each planned figure, define:
1. **Core conclusion**: the one-sentence claim this figure must defend
2. **Evidence chain**: map each panel to the claim — drop panels that don't carry unique evidence
3. **Archetype**: classify as `quantitative grid`, `schematic-led composite`, `image plate + quant`, or `asymmetric mixed-modality`
4. **Export spec**: dimensions, format (PDF for LaTeX `\includegraphics`), font consistency with body text

### Step 2: Style Configuration

```python
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# Nature-grade rcParams
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Times New Roman", "DejaVu Sans", "Arial", "sans-serif"],
    "font.size": 8,                     # body text size for figures
    "axes.titlesize": 9,                # slightly larger for subplot titles
    "axes.labelsize": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "svg.fonttype": "none",             # editable text in SVG
    "pdf.fonttype": 42,                 # editable TrueType in PDF
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})
```

### Step 3: Color Palette

**Default palette** — accessible, print-friendly:
```python
# Colorblind-safe qualitative palette (Wong, 2011)
COLORS = {
    "blue":   "#0072B2",
    "orange": "#E69F00",
    "green":  "#009E73",
    "red":    "#D55E00",
    "purple": "#CC79A7",
    "brown":  "#8B6914",
    "pink":   "#F0E442",
    "grey":   "#999999",
}

# Directional: green for gains, red for drops
GAIN_COLOR = "#009E73"
DROP_COLOR = "#D55E00"
NEUTRAL_COLOR = "#999999"
```

**Rules**:
- Prefer unified method families across panels over maximal hue separation
- Use the same color for the same method across all figures
- Reserve red/green for directional cues (improvement/degradation)
- Grey out baselines in ablation figures to focus attention on your method

### Step 4: Figure Dimensions

**Single-column figures**:
```python
fig, ax = plt.subplots(figsize=(3.35, 2.0))  # ~8.5cm wide
```

**Double-column (full-width) figures**:
```python
fig, ax = plt.subplots(figsize=(7.0, 3.5))   # ~17.8cm wide
```

**Square panel for qualitative images**:
```python
fig, ax = plt.subplots(figsize=(3.35, 3.35))
```

### Step 5: Export

```python
# For LaTeX — PDF vector format
fig.savefig("figures/figure_name.pdf", format="pdf", bbox_inches="tight", pad_inches=0.02)

# For preview — PNG
fig.savefig("figures/figure_name.png", format="png", dpi=300, bbox_inches="tight")
```

---

## Common Figure Types

### Type 1: Bar Chart Comparison

Good for: comparing methods on a few metrics.
```python
methods = ["A", "B", "C", "Ours"]
values = [72.3, 74.1, 71.8, 78.9]
colors = [NEUTRAL_COLOR]*3 + [COLORS["blue"]]

fig, ax = plt.subplots(figsize=(3.35, 2.0))
bars = ax.bar(methods, values, color=colors, width=0.6, edgecolor="white", linewidth=0.5)
# Add value labels
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f"{val:.1f}", ha="center", va="bottom", fontsize=7)
ax.set_ylabel("Accuracy (%)")
ax.spines["left"].set_visible(False)
ax.yaxis.grid(True, alpha=0.3)
ax.set_axisbelow(True)
```

### Type 2: Line Plot (Training Curves / Trends)

Good for: convergence, parameter sensitivity, epoch-wise trends.
```python
fig, ax = plt.subplots(figsize=(3.35, 2.0))
for label, data, color in zip(labels, curves, ["#999999", "#999999", COLORS["blue"]]):
    ax.plot(x, data, label=label, color=color, linewidth=1.2, alpha=0.9)
ax.legend(fontsize=7)
ax.set_xlabel("Epoch")
ax.set_ylabel("Loss")
```

### Type 3: Scatter / Bubble

Good for: embedding visualization, trade-off analysis.
```python
fig, ax = plt.subplots(figsize=(3.35, 2.5))
ax.scatter(x, y, s=sizes, c=colors, alpha=0.6, edgecolors="white", linewidth=0.3)
```

### Type 4: Multi-Panel Composite

Good for: combining method overview + quantitative results.
```python
fig = plt.figure(figsize=(7.0, 5.0))
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
ax1 = fig.add_subplot(gs[0, :])   # top: method diagram (full width)
ax2 = fig.add_subplot(gs[1, 0])   # bottom-left: metric 1
ax3 = fig.add_subplot(gs[1, 1])   # bottom-center: metric 2
ax4 = fig.add_subplot(gs[1, 2])   # bottom-right: metric 3
# Label subfigures
for ax, label in zip([ax1, ax2, ax3, ax4], ["(a)", "(b)", "(c)", "(d)"]):
    ax.text(-0.08, 1.05, label, transform=ax.transAxes, fontsize=9, fontweight="bold")
```

---

## Table Design Standards

### Booktabs Style (Required)

```latex
% In preamble
\usepackage{booktabs}

% Table
\begin{table}[t]
  \centering
  \caption{Comparison with state-of-the-art methods on Dataset X.
           Best results in \textbf{bold}, second-best \underline{underlined}.}
  \label{tab:main_results}
  \begin{tabular}{@{}l c c c c@{}}
    \toprule
    Method & Metric A $\uparrow$ & Metric B $\uparrow$ & Metric C $\downarrow$ & Params (M) \\
    \midrule
    \multicolumn{5}{@{}l}{\small \textit{Conventional Methods}} \\
    \addlinespace
    Method A (2023) & 72.3 & 68.1 & 0.42 & 45 \\
    Method B (2024) & 74.1 & 70.3 & 0.38 & 52 \\
    \addlinespace
    \multicolumn{5}{@{}l}{\small \textit{Recent Methods}} \\
    \addlinespace
    Method C (2025) & 76.8 & 72.5 & 0.32 & 38 \\
    Method D (2025) & \underline{77.2} & 73.0 & 0.30 & 41 \\
    \addlinespace
    \textbf{Ours (full)}      & \textbf{78.9} & \textbf{74.2} & \textbf{0.28} & 35 \\
    \textbf{Ours (light)}     & 77.5 & 73.0 & \underline{0.29} & \textbf{22} \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Table Design Rules

1. **No vertical rules** — period. `\begin{tabular}{@{}l c c c@{}}`
2. **Minimal horizontal rules** — `\toprule`, `\midrule`, `\bottomrule` only
3. **Group rows** with `\addlinespace` for visual separation
4. **Bold best**, underline second-best per column
5. **Arrow indicators**: `$\uparrow$` for higher-is-better, `$\downarrow$` for lower-is-better
6. **Column alignment**: left-align text columns, center-align numeric columns
7. **Caption is self-contained**: reader should understand the table without reading body text
8. **Avoid `\resizebox`**: if the table doesn't fit, restructure it (fewer columns, shorter headers)

### Ablation Table Pattern

```latex
\begin{table}[t]
  \centering
  \caption{Ablation study on model components.}
  \label{tab:ablation}
  \begin{tabular}{@{}l c c c@{}}
    \toprule
    Configuration & Accuracy $\uparrow$ & F1 $\uparrow$ & $\Delta$ \\
    \midrule
    Baseline (no components) & 65.2 & 62.1 & — \\
    + Component A           & 70.1 & 67.8 & +4.9 \\
    + Component B           & 73.5 & 71.2 & +3.4 \\
    + Component C           & 76.8 & 74.5 & +3.3 \\
    \textbf{All (full)}     & \textbf{78.9} & \textbf{74.2} & \textbf{+13.7} \\
    \bottomrule
  \end{tabular}
\end{table}
```

---

## Quick Reference: Figure Checklist

Before finalizing any figure:
- [ ] Conclusion: Can you state the one-sentence claim this figure defends?
- [ ] Redundancy: Does every panel carry unique evidence? (Drop panels that don't)
- [ ] Font size: Are all text elements ≥7pt (readable in print)?
- [ ] Color: Is the figure interpretable in grayscale?
- [ ] Format: Exported as PDF vector (not PNG raster)?
- [ ] Labeling: All axes labeled, legend present if needed?
- [ ] Consistency: Same color = same method across all figures in the paper?
- [ ] Caption: Self-contained mini-abstract for the figure?

## Quick Reference: Table Checklist

Before finalizing any table:
- [ ] Booktabs style: `\toprule`, `\midrule`, `\bottomrule` only?
- [ ] No vertical rules: `@{...}` in tabular preamble?
- [ ] Bold/underline: Best/second-best clearly marked?
- [ ] Arrow indicators: `$\uparrow$` / `$\downarrow$` on metric headers?
- [ ] Sorted: Rows sorted by primary metric?
- [ ] Caption: Self-contained and informative?
- [ ] Fit: Table fits within text width without `\resizebox`?
