"""Reconstruction quality analysis and latent space visualization."""

import json
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from sklearn.manifold import TSNE

M_VALUES = [128, 256, 512, 1024]


def plot_reconstruction_quality(results_dir: str, output_dir: str):
    """Plot SSL reconstruction loss vs M, plus compress_dqn (64→16→64)."""
    os.makedirs(output_dir, exist_ok=True)

    # SSL→DQN reconstruction losses (random projection → autoencoder)
    ssl_final_losses = {M: [] for M in M_VALUES}
    for fpath in glob.glob(os.path.join(results_dir, "ssl_dqn_*.json")):
        with open(fpath) as f:
            r = json.load(f)
        M = r.get("M")
        if M in ssl_final_losses:
            ssl_final_losses[M].append(r.get("ssl_final_loss", 0))

    # Compress→DQN reconstruction loss (64→16→64, no random projection)
    compress_losses = []
    for fpath in glob.glob(os.path.join(results_dir, "compress_dqn_*.json")):
        with open(fpath) as f:
            r = json.load(f)
        compress_losses.append(r.get("ssl_final_loss", 0))

    fig, ax = plt.subplots(figsize=(8, 5))
    # SSL→DQN bars
    means = []
    stds = []
    labels = [str(m) for m in M_VALUES]
    for M in M_VALUES:
        losses = ssl_final_losses[M]
        if losses:
            means.append(np.mean(losses))
            stds.append(np.std(losses))
        else:
            means.append(0)
            stds.append(0)
    x = np.arange(len(M_VALUES))
    ax.bar(x, means, yerr=stds, color="#2196F3", alpha=0.7,
           capsize=5, tick_label=labels, label="SSL→DQN (random proj→AE)")

    # Compress→DQN bar (positioned to the right)
    if compress_losses:
        cp_mean = np.mean(compress_losses)
        cp_std = np.std(compress_losses)
        ax.bar(len(M_VALUES), cp_mean, yerr=cp_std if cp_std > 0 else None,
               color="#E91E63", alpha=0.7, capsize=5)

    # Set tick labels
    all_labels = [str(m) for m in M_VALUES]
    if compress_losses:
        all_labels.append("16\n(Compress)")
    ax.set_xticks(range(len(all_labels)))
    ax.set_xticklabels(all_labels)

    ax.set_xlabel("Observation / Bottleneck Dimension", fontsize=12)
    ax.set_ylabel("MSE Reconstruction Loss", fontsize=12)
    ax.set_title("Autoencoder Reconstruction Quality", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "reconstruction_quality.png"), dpi=150)
    fig.savefig(os.path.join(output_dir, "reconstruction_quality.pdf"))
    plt.close()
    print(f"Saved reconstruction quality to {output_dir}/reconstruction_quality.png")


def plot_final_performance(results_dir: str, output_dir: str):
    """Grouped bar chart: final success rate — all pipelines side by side."""
    os.makedirs(output_dir, exist_ok=True)

    def final_success_rate(r):
        curve = r.get("eval_success_rates", [])
        if curve:
            return curve[-1][1]
        return 0

    results = {}
    for fpath in glob.glob(os.path.join(results_dir, "*.json")):
        with open(fpath) as f:
            r = json.load(f)
        pipeline = r["pipeline"]
        M = r.get("M", 64)
        results.setdefault((pipeline, M), []).append(final_success_rate(r))

    PIPELINE_LABELS = {"ssl_dqn": "SSL→DQN", "random_dqn": "DQN-only",
                       "compress_dqn": "Compress→DQN", "identity": "Identity"}
    PIPELINE_COLORS = {"ssl_dqn": "#2196F3", "random_dqn": "#FF9800",
                       "compress_dqn": "#E91E63", "identity": "#4CAF50"}
    FIXED_PIPELINES = [
        ("identity", 64, "Identity\n64d one-hot"),
    ]
    COMPRESS_DIMS = [1, 2, 16]
    COMPRESS_COLOR = "#E91E63"

    # Build categories
    categories = []
    cat_colors = []
    for pipeline, M, label in FIXED_PIPELINES:
        if (pipeline, M) in results:
            categories.append((label, pipeline, M))
            cat_colors.append(PIPELINE_COLORS[pipeline])
    for d in COMPRESS_DIMS:
        if ("compress_dqn", d) in results:
            categories.append((f"Compress→DQN\nd={d}", "compress_dqn", d))
            cat_colors.append(COMPRESS_COLOR)
    for M in M_VALUES:
        if ("ssl_dqn", M) in results:
            categories.append((f"SSL→DQN\nM={M}", "ssl_dqn", M))
            cat_colors.append(PIPELINE_COLORS["ssl_dqn"])
    for M in M_VALUES:
        if ("random_dqn", M) in results:
            categories.append((f"DQN-only\nM={M}", "random_dqn", M))
            cat_colors.append(PIPELINE_COLORS["random_dqn"])

    means = []
    stds = []
    for _, pipeline, M in categories:
        vals = results.get((pipeline, M), [])
        means.append(np.mean(vals))
        stds.append(np.std(vals))

    labels = [c[0] for c in categories]
    x = np.arange(len(categories))

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(x, means, yerr=stds, color=cat_colors, alpha=0.85,
           capsize=4, edgecolor="white", linewidth=0.5)

    # Annotate values
    for i, (m, s) in enumerate(zip(means, stds)):
        ax.text(i, m + s + 0.015, f"{m:.2f}", ha="center", va="bottom",
                fontsize=8, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Final Success Rate", fontsize=12)
    ax.set_title("Final Performance: Success Rate", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylim(0, 1.25)

    # Group separator lines
    dqn_start = next((i for i, (_, p, _) in enumerate(categories) if p == "random_dqn"), None)
    if dqn_start is not None:
        ax.axvline(x=dqn_start - 0.5, color="gray", linestyle=":", alpha=0.4, linewidth=1)

    legend_elements = [
        Patch(facecolor=PIPELINE_COLORS["identity"], alpha=0.85, label="Identity  64d one-hot"),
        Patch(facecolor=COMPRESS_COLOR, alpha=0.85, label="Compress→DQN  d∈{1,2,16} learned"),
        Patch(facecolor=PIPELINE_COLORS["ssl_dqn"], alpha=0.85, label="SSL→DQN  random proj → AE → DQN"),
        Patch(facecolor=PIPELINE_COLORS["random_dqn"], alpha=0.85, label="DQN-only  random proj → DQN"),
    ]
    ax.legend(handles=legend_elements, fontsize=9, loc="upper right",
              framealpha=0.9, ncol=2)

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "final_performance.png"), dpi=150)
    fig.savefig(os.path.join(output_dir, "final_performance.pdf"))
    plt.close()
    print(f"Saved final performance to {output_dir}/final_performance.png")


if __name__ == "__main__":
    import sys
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_output"
    plot_reconstruction_quality(results_dir, output_dir)
    plot_final_performance(results_dir, output_dir)
