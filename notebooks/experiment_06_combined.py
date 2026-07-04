"""
experiment_06_combined.py
-------------------------
Combined parameter sweep: varies both r and n simultaneously.

Produces a heatmap showing convergence rate across the full
r x n parameter space. This is the headline figure of the
dissertation — showing exactly where dynamics converge and
where they fail.

Run with: python notebooks/experiment_06_combined.py
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("results/figures", exist_ok=True)
os.makedirs("results/data", exist_ok=True)

from src.contest import TullockContest
from src.dynamics import run_synchronous

rng       = np.random.default_rng(0)
n_seeds   = 10
max_iters = 300

r_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
n_values = [2, 3, 5, 10, 20]
V        = 10.0

print("Experiment 6: Combined r x n parameter sweep")
print("=" * 55)
print(f"Grid: {len(r_values)} r values x {len(n_values)} n values")
print(f"Seeds per cell: {n_seeds}")
print()

# Build convergence rate grid
conv_grid = np.zeros((len(n_values), len(r_values)))

for i, n in enumerate(n_values):
    for j, r in enumerate(r_values):
        contest    = TullockContest(n=n, r=r,
                                    valuations=[V] * n)
        conv_count = []
        for _ in range(n_seeds):
            initial = rng.uniform(0.1, V * 0.8, size=n)
            result  = run_synchronous(contest, initial,
                                      max_iterations=max_iters)
            conv_count.append(result['converged'])
        rate              = np.mean(conv_count)
        conv_grid[i, j]   = rate
        print(f"n={n:2d}, r={r:.1f} | Conv. rate: {rate*100:.0f}%")


# ── Figure 15: Convergence heatmap ────────────────────────
fig, ax = plt.subplots(figsize=(11, 6))
im = ax.imshow(conv_grid * 100,
               cmap='RdYlGn',
               aspect='auto',
               vmin=0, vmax=100)

# Labels
ax.set_xticks(range(len(r_values)))
ax.set_xticklabels([str(r) for r in r_values])
ax.set_yticks(range(len(n_values)))
ax.set_yticklabels([str(n) for n in n_values])
ax.set_xlabel("Decisiveness parameter r")
ax.set_ylabel("Number of players (n)")
ax.set_title("Convergence Rate of Synchronous BRD\n"
             "Across r x n Parameter Space (%)")

# Add percentage text inside each cell
for i in range(len(n_values)):
    for j in range(len(r_values)):
        val  = conv_grid[i, j] * 100
        color = 'white' if val < 40 or val > 80 else 'black'
        ax.text(j, i, f'{val:.0f}%',
                ha='center', va='center',
                fontsize=9, color=color, fontweight='bold')

plt.colorbar(im, ax=ax, label='Convergence rate (%)')
plt.tight_layout()
plt.savefig("results/figures/fig15_convergence_heatmap.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("\nSaved: results/figures/fig15_convergence_heatmap.png")


# ── Figure 16: Convergence rate vs r for each n ───────────
fig, ax = plt.subplots(figsize=(9, 5))
colours = ['steelblue', 'darkorange', 'green', 'red', 'purple']

for i, n in enumerate(n_values):
    ax.plot(r_values,
            conv_grid[i, :] * 100,
            'o-', color=colours[i],
            markersize=7,
            label=f'n={n}')

ax.set_xlabel("Decisiveness parameter r")
ax.set_ylabel("Convergence rate (%)")
ax.set_title("Convergence Rate vs. r for Different n Values")
ax.legend(title="Players")
ax.grid(True, alpha=0.3)
ax.set_ylim(-5, 110)
plt.tight_layout()
plt.savefig("results/figures/fig16_convergence_by_n_and_r.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig16_convergence_by_n_and_r.png")


# ── Summary table ─────────────────────────────────────────
print()
print("Summary: Convergence rate (%) across r x n")
print("-" * 55)
header = "n\\r  " + "  ".join([f"{r:>5.1f}" for r in r_values])
print(header)
for i, n in enumerate(n_values):
    row = f"n={n:2d} " + "  ".join(
        [f"{conv_grid[i,j]*100:>5.0f}%" for j in range(len(r_values))]
    )
    print(row)


# Save data
np.save("results/data/experiment_06_conv_grid.npy", conv_grid)
np.save("results/data/experiment_06_r_values.npy", r_values)
np.save("results/data/experiment_06_n_values.npy", n_values)
print()
print("Data saved to results/data/")
print()
print("Experiment 6 complete.")
print()
print("=" * 55)
print("ALL 6 EXPERIMENTS COMPLETE")
print("Total dissertation figures produced: 16")
print("=" * 55)