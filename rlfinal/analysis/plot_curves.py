"""Pipeline comparison: learning curves, sample efficiency, summary table."""

import json
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PIPELINE_LABELS = {
    "ssl_dqn": "SSL→DQN",
    "random_dqn": "DQN-only",
    "compress_dqn": "Compress→DQN",
    "identity": "Identity",
}
PIPELINE_COLORS = {
    "ssl_dqn": "#2196F3",
    "random_dqn": "#FF9800",
    "compress_dqn": "#E91E63",
    "identity": "#4CAF50",
}
PIPELINE_LINESTYLE = {
    "ssl_dqn": "-",
    "random_dqn": "--",
    "compress_dqn": "-.",
    "identity": ":",
}
M_VALUES = [128, 256, 512, 1024]
FIXED_PIPELINES = [
    ("identity", 64, "Identity\n64d (one-hot)"),
]
# Compress→DQN has multiple bottleneck dimensions
COMPRESS_DIMS = [1, 2, 16]
COMPRESS_COLOR = "#E91E63"  # pink family


def load_results(results_dir: str) -> dict:
    """Load all result JSON files, keyed by (pipeline, M, seed)."""
    results = {}
    for fpath in glob.glob(os.path.join(results_dir, "*.json")):
        with open(fpath) as f:
            r = json.load(f)
        pipeline = r["pipeline"]
        M = r.get("M", 64)
        seed = r["seed"]
        results[(pipeline, M, seed)] = r
    return results


def _gather_curve(results, pipeline, M):
    """Gather and average curves for (pipeline, M) across all seeds. Returns (mean, std, episodes)."""
    curves = []
    for (p_key, m_key, s_key), r in results.items():
        if p_key == pipeline and m_key == M:
            curve = np.array([v for _, v in r.get("eval_success_rates", [])])
            if len(curve) > 0:
                curves.append(curve)
    if not curves:
        return None, None, None
    max_len = max(len(c) for c in curves)
    padded = []
    for c in curves:
        if len(c) < max_len:
            c = np.pad(c, (0, max_len - len(c)), constant_values=c[-1])
        padded.append(c)
    mean = np.mean(padded, axis=0)
    std = np.std(padded, axis=0)
    episodes = np.arange(100, (max_len + 1) * 100, 100)[:len(mean)]
    return mean, std, episodes


def plot_learning_curves(results: dict, output_dir: str):
    """Single consolidated learning curve: all 4 pipelines, 8 line variants."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(13, 7))

    # ---- SSL→DQN (varying M: random proj → AE → 64d bottleneck → DQN) ----
    for M in M_VALUES:
        mean, std, episodes = _gather_curve(results, "ssl_dqn", M)
        if mean is not None:
            alpha = 0.35 + 0.65 * ((M - 128) / (1024 - 128))  # lighter→darker
            ax.plot(episodes, mean, color=PIPELINE_COLORS["ssl_dqn"],
                    linestyle=PIPELINE_LINESTYLE["ssl_dqn"], linewidth=1.8, alpha=alpha,
                    label=f"SSL→DQN  M={M}")
            ax.fill_between(episodes, mean - std, mean + std,
                            color=PIPELINE_COLORS["ssl_dqn"], alpha=0.07)

    # ---- DQN-only (varying M: random projection → DQN, no AE) ----
    for M in M_VALUES:
        mean, std, episodes = _gather_curve(results, "random_dqn", M)
        if mean is not None:
            alpha = 0.35 + 0.65 * ((M - 128) / (1024 - 128))
            ax.plot(episodes, mean, color=PIPELINE_COLORS["random_dqn"],
                    linestyle=PIPELINE_LINESTYLE["random_dqn"], linewidth=1.8, alpha=alpha,
                    label=f"DQN-only  M={M}")
            ax.fill_between(episodes, mean - std, mean + std,
                            color=PIPELINE_COLORS["random_dqn"], alpha=0.07)

    # ---- Compress→DQN (64 → learned Dd → DQN, D ∈ {1,2,16}) ----
    compress_linestyles = {1: ":", 2: "--", 16: "-."}
    for d in COMPRESS_DIMS:
        mean, std, episodes = _gather_curve(results, "compress_dqn", d)
        if mean is not None:
            alpha = 0.45 + 0.55 * (d / 16)  # darker = more dims
            ax.plot(episodes, mean, color=COMPRESS_COLOR,
                    linestyle=compress_linestyles.get(d, "-."), linewidth=2.2, alpha=alpha,
                    label=f"Compress→DQN  d={d}")
            ax.fill_between(episodes, mean - std, mean + std,
                            color=COMPRESS_COLOR, alpha=0.06)

    # ---- Identity (64d one-hot, no compression) ----
    mean, std, episodes = _gather_curve(results, "identity", 64)
    if mean is not None:
        ax.plot(episodes, mean, color=PIPELINE_COLORS["identity"],
                linestyle=PIPELINE_LINESTYLE["identity"], linewidth=2.5,
                label="Identity  (64d one-hot)")
        ax.fill_between(episodes, mean - std, mean + std,
                        color=PIPELINE_COLORS["identity"], alpha=0.12)

    ax.set_xlabel("Episode", fontsize=13)
    ax.set_ylabel("Success Rate", fontsize=13)
    ax.set_title("DQN Learning Curves: All Pipelines", fontsize=14, fontweight="bold")
    ax.set_ylim(-0.05, 1.1)
    ax.grid(True, alpha=0.25)

    # Legend: manual groups
    legend_elements = [
        Patch(facecolor=PIPELINE_COLORS["ssl_dqn"], edgecolor="none", alpha=0.7,
              label="SSL→DQN  (random proj → AE → DQN)"),
        Patch(facecolor=PIPELINE_COLORS["random_dqn"], edgecolor="none", alpha=0.7,
              label="DQN-only  (random proj → DQN)"),
        Patch(facecolor=COMPRESS_COLOR, edgecolor="none", alpha=0.7,
              label="Compress→DQN  d∈{1,2,16} learned"),
        Patch(facecolor=PIPELINE_COLORS["identity"], edgecolor="none",
              label="Identity  64d one-hot"),
    ]
    ax.legend(handles=legend_elements, fontsize=10, loc="lower right",
              framealpha=0.9, ncol=1)

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "learning_curves.png"), dpi=150)
    fig.savefig(os.path.join(output_dir, "learning_curves.pdf"))
    plt.close()
    print(f"Saved learning curves to {output_dir}/learning_curves.png")


def plot_sample_efficiency(results: dict, output_dir: str):
    """Grouped bar chart: episodes to 90% success — all pipelines side by side."""
    os.makedirs(output_dir, exist_ok=True)

    def episodes_to_threshold(r, threshold=0.9):
        curve = r.get("eval_success_rates", [])
        for ep, val in curve:
            if val >= threshold:
                return ep
        if curve:
            return curve[-1][0]
        return 5000

    # Build categories: each unique (pipeline, M) with enough data
    categories = []   # list of (label, pipeline, M)
    cat_colors = []

    # Identity (fixed)
    for pipeline, M, label in FIXED_PIPELINES:
        if any(p_key == pipeline and m_key == M for (p_key, m_key, _) in results):
            categories.append((label, pipeline, M))
            cat_colors.append(PIPELINE_COLORS[pipeline])

    # Compress→DQN: one bar per bottleneck dim
    for d in COMPRESS_DIMS:
        if any(p_key == "compress_dqn" and m_key == d for (p_key, m_key, _) in results):
            categories.append((f"Compress→DQN\nd={d}", "compress_dqn", d))
            cat_colors.append(COMPRESS_COLOR)

    # SSL→DQN: one bar per M
    for M in M_VALUES:
        if any(p_key == "ssl_dqn" and m_key == M for (p_key, m_key, _) in results):
            categories.append((f"SSL→DQN\nM={M}", "ssl_dqn", M))
            cat_colors.append(PIPELINE_COLORS["ssl_dqn"])

    # DQN-only: one bar per M
    for M in M_VALUES:
        if any(p_key == "random_dqn" and m_key == M for (p_key, m_key, _) in results):
            categories.append((f"DQN-only\nM={M}", "random_dqn", M))
            cat_colors.append(PIPELINE_COLORS["random_dqn"])

    means = []
    stds = []
    for _, pipeline, M in categories:
        vals = []
        for (p_key, m_key, s_key), r in results.items():
            if p_key == pipeline and m_key == M:
                vals.append(episodes_to_threshold(r))
        means.append(np.mean(vals))
        stds.append(np.std(vals))

    labels = [c[0] for c in categories]
    x = np.arange(len(categories))

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(x, means, yerr=stds, color=cat_colors, alpha=0.85,
                  capsize=4, edgecolor="white", linewidth=0.5)

    # Annotate values on bars
    for i, (m, s) in enumerate(zip(means, stds)):
        ax.text(i, m + s + 30, f"{m:.0f}", ha="center", va="bottom",
                fontsize=8, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Episodes to 90% Success Rate", fontsize=12)
    ax.set_title("Sample Efficiency: Episodes to 90% Success Rate", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylim(0, max(means) + max(stds) + 150)

    # Group separator lines
    sep_positions = []
    # After identity
    id_end = next((i for i, (_, p, _) in enumerate(categories) if p != "identity"), None)
    if id_end is not None:
        sep_positions.append(id_end - 0.5)
    # After compress_dqn
    compress_end = next((i for i, (_, p, _) in enumerate(categories) if p not in ("identity", "compress_dqn")), None)
    if compress_end is not None:
        sep_positions.append(compress_end - 0.5)
    # After ssl_dqn
    dqn_start = next((i for i, (_, p, _) in enumerate(categories) if p == "random_dqn"), None)
    if dqn_start is not None:
        sep_positions.append(dqn_start - 0.5)

    for sep_x in sep_positions:
        ax.axvline(x=sep_x, color="gray", linestyle=":", alpha=0.4, linewidth=1)

    # Legend
    legend_elements = [
        Patch(facecolor=PIPELINE_COLORS["identity"], alpha=0.85, label="Identity  64d one-hot"),
        Patch(facecolor=COMPRESS_COLOR, alpha=0.85, label="Compress→DQN  d∈{1,2,16} learned"),
        Patch(facecolor=PIPELINE_COLORS["ssl_dqn"], alpha=0.85, label="SSL→DQN  random proj → AE → DQN"),
        Patch(facecolor=PIPELINE_COLORS["random_dqn"], alpha=0.85, label="DQN-only  random proj → DQN"),
    ]
    ax.legend(handles=legend_elements, fontsize=9, loc="upper left",
              framealpha=0.9, ncol=2)

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "sample_efficiency.png"), dpi=150)
    fig.savefig(os.path.join(output_dir, "sample_efficiency.pdf"))
    plt.close()
    print(f"Saved sample efficiency to {output_dir}/sample_efficiency.png")


def print_summary_table(results: dict):
    """Print a summary table of results."""
    print("\n" + "=" * 80)
    print("SUMMARY: Episodes to 90% Success Rate (± std over seeds)")
    print("=" * 80)
    print(f"{'Pipeline':<16}", end="")
    for M in M_VALUES:
        print(f"  M={M:<8}", end="")
    print()

    def episodes_to_threshold(r, threshold=0.9):
        curve = r.get("eval_success_rates", [])
        for ep, val in curve:
            if val >= threshold:
                return ep
        return None

    for pipeline in ["ssl_dqn", "random_dqn"]:
        print(f"{PIPELINE_LABELS[pipeline]:<16}", end="")
        for M in M_VALUES:
            vals = []
            for (p_key, m_key, s_key), r in results.items():
                if p_key == pipeline and m_key == M:
                    v = episodes_to_threshold(r)
                    if v is not None:
                        vals.append(v)
            if vals:
                print(f"  {np.mean(vals):.0f}±{np.std(vals):.0f}   ", end="")
            else:
                print(f"  {'N/A':<12}", end="")
        print()

    # Identity
    id_vals = []
    for (p_key, m_key, s_key), r in results.items():
        if p_key == "identity":
            v = episodes_to_threshold(r)
            if v is not None:
                id_vals.append(v)
    if id_vals:
        print(f"{'Identity (64d)':<16}  Mean: {np.mean(id_vals):.0f}±{np.std(id_vals):.0f} episodes")

    # Compress→DQN
    cp_vals = []
    for (p_key, m_key, s_key), r in results.items():
        if p_key == "compress_dqn":
            v = episodes_to_threshold(r)
            if v is not None:
                cp_vals.append(v)
    if cp_vals:
        print(f"{'Compress→DQN (16d)':<16}  Mean: {np.mean(cp_vals):.0f}±{np.std(cp_vals):.0f} episodes")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_output"
    results = load_results(results_dir)
    print(f"Loaded {len(results)} experiment results")
    plot_learning_curves(results, output_dir)
    plot_sample_efficiency(results, output_dir)
    print_summary_table(results)
