import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def box(ax, x, y, w, h, text, sub='', color='#E3F2FD', edge='#1565C0', fs=11):
    rect = mpatches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.08",
                                     facecolor=color, edgecolor=edge, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x, y+0.08, text, ha='center', va='center', fontsize=fs, fontweight='bold')
    if sub:
        ax.text(x, y-0.28, sub, ha='center', va='center', fontsize=8, color='#555')

def arrow(ax, x1, y1, x2, y2, color='#333', lw=1.8):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw))

def txt(ax, x, y, text, fs=9, color='#555', style='italic'):
    ax.text(x, y, text, fontsize=fs, color=color, style=style)

# ====== Dataflow ======
fig, ax = plt.subplots(figsize=(14, 4.5))
ax.set_xlim(0, 14)
ax.set_ylim(0, 4.5)
ax.axis('off')

box(ax, 1.0, 3.6, 2.2, 0.8, 'True state s', '64-dim one-hot', '#FFEBEE', '#C62828', 11)
box(ax, 1.0, 2.1, 2.2, 0.8, 'Observation o', 'M-dim projection', '#E3F2FD', '#1565C0', 11)
arrow(ax, 1.0, 3.2, 1.0, 2.5)
txt(ax, 2.5, 2.85, 'Random MLP E (frozen, 64->M)')

arrow(ax, 2.2, 2.1, 4.0, 2.6, '#2E7D32')
arrow(ax, 2.2, 2.1, 4.0, 2.1, '#E65100')

box(ax, 5.8, 2.6, 3.0, 0.8, 'SSL Encoder: M->64', 'Autoencoder pretraining', '#E8F5E9', '#2E7D32', 10)
arrow(ax, 7.4, 2.6, 9.0, 2.6, '#2E7D32')
box(ax, 10.2, 2.6, 1.6, 0.8, 'z', '64-dim latent', '#E8F5E9', '#2E7D32', 11)
txt(ax, 3.5, 2.95, 'Pipeline 1', 8, '#2E7D32')

box(ax, 10.8, 1.0, 3.2, 2.4, 'Double DQN', '', '#FFF3E0', '#E65100', 13)
ax.text(10.8, 0.65, 'input->256->256->4', ha='center', va='center', fontsize=10, color='#555')
ax.text(10.8, 0.3, 'Pipe1: z(64) / Pipe2: o(M)', ha='center', va='center', fontsize=8, color='#999')

arrow(ax, 10.2, 2.2, 10.2, 1.5, '#2E7D32')
arrow(ax, 2.2, 1.7, 9.2, 1.0, '#E65100')
txt(ax, 4.0, 1.6, 'Pipeline 2: DQN-only (no SSL)', 8, '#E65100')

box(ax, 1.0, 0.6, 2.8, 0.55, 'Identity: DQN directly on s (64-dim)', '', '#F3E5F5', '#7B1FA2', 9)

txt(ax, 7.0, 0.1, 'Core constraint: true state s is NEVER visible during training!', 10, '#C62828', 'normal')
plt.tight_layout(pad=0.5)
fig.savefig('/data/homework/RL/final2/paper/PLAN_dataflow.pdf', dpi=150, bbox_inches='tight')
plt.close()
print('Dataflow saved')


# ====== SSL Autoencoder ======
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3.5)
ax.axis('off')

box(ax, 1.0, 1.75, 1.8, 0.8, 'Observation o', 'M-dim', '#E3F2FD', '#1565C0', 11)
arrow(ax, 2.0, 1.75, 3.2, 1.75, '#2E7D32')
box(ax, 4.5, 1.75, 2.2, 0.8, 'Encoder', 'M -> 64', '#E8F5E9', '#2E7D32', 11)
arrow(ax, 5.7, 1.75, 6.8, 1.75, '#333')
box(ax, 7.5, 1.75, 0.9, 0.8, 'z', '64-dim', '#FFF9C4', '#F9A825', 11)
arrow(ax, 8.0, 1.75, 9.2, 1.75, '#E65100')
box(ax, 10.5, 1.75, 2.2, 0.8, 'Decoder', '64 -> M', '#FFF3E0', '#E65100', 11)

ax.annotate('', xy=(10.5, 0.9), xytext=(10.5, 1.35), arrowprops=dict(arrowstyle='->', color='#E65100', lw=1.8))
box(ax, 10.5, 0.5, 2.2, 0.6, 'o_hat', 'Reconstruction (M-dim)', '#FFF3E0', '#E65100', 10)

ax.annotate('', xy=(7.0, 0.5), xytext=(9.3, 0.5), arrowprops=dict(arrowstyle='<->', color='#C62828', lw=1.5))
ax.text(8.15, 0.25, 'L = ||o - o_hat||^2', ha='center', fontsize=13, color='#C62828', fontweight='bold')

ax.annotate('', xy=(1.0, 1.35), xytext=(1.0, 0.9), arrowprops=dict(arrowstyle='->', color='#1565C0', lw=1.2))
ax.annotate('', xy=(1.0, 0.5), xytext=(1.0, 0.9), arrowprops=dict(arrowstyle='->', color='#1565C0', lw=1.2))
arrow(ax, 2.0, 0.5, 6.9, 0.5, '#1565C0', 1.2)

txt(ax, 4.5, 2.8, 'After pretraining: freeze Encoder, DQN uses z as input', 10, '#2E7D32', 'normal')
txt(ax, 5.0, 0.0, 'Training data: all 64 states enumerated, zero sampling noise', 9, '#555')

plt.tight_layout(pad=0.5)
fig.savefig('/data/homework/RL/final2/paper/PLAN_ssl.pdf', dpi=150, bbox_inches='tight')
plt.close()
print('SSL saved')
