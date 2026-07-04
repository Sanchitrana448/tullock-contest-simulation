"""
experiment_02_r_sweep.py
------------------------
Sweeps the decisiveness parameter r across [0.5, 1.0, 1.5, 2.0, 3.0].

For each value of r:
- Runs synchronous BRD from 20 random starting points
- Records: convergence rate, iterations, total effort

Directly addresses Research Objective 1 from the dissertation.

Run with: python notebooks/experiment_02_r_sweep.py
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

# Parameters
r_values  = [0.5, 1.0, 1.5, 2.0, 3.0]
n_players = 2
V         = 10.0
n_seeds   = 20
max_iters = 2000

rng = np.random.default_rng(0)

print("Experiment 2: Sweeping decisiveness parameter r")
print("=" * 55)

summary = {}

for r in r_values:
    contest = TullockContest(n=n_players, r=r,
                             valuations=[V] * n_players)
    convergence_counts = []
    iteration_counts   = []
    final_efforts_list = []

    for seed in range(n_seeds):
        initial = rng.uniform(0.1, V * 0.8, size=n_players)
        result  = run_synchronous(contest, initial,
                                  max_iterations=max_iters)

        convergence_counts.append(result['converged'])
        if result['converged']:
            iteration_counts.append(result['iterations'])
        final_efforts_list.append(result['final_efforts'])

    conv_rate   = np.mean(convergence_counts)
    mean_iters  = np.mean(iteration_counts) if iteration_counts else np.nan
    mean_effort = np.mean([e.sum() for e in final_efforts_list])

    summary[r] = {
        'convergence_rate':  conv_rate,
        'mean_iterations':   mean_iters,
        'mean_total_effort': mean_effort,
    }

    print(f"r={r:.1f} | Conv. rate: {conv_rate*100:.0f}% | "
          f"Mean iters: {mean_iters:.1f} | "
          f"Mean total effort: {mean_effort:.4f}")


# Figure 4 - Convergence rate vs r
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar([str(r) for r in r_values],
       [summary[r]['convergence_rate'] * 100 for r in r_values],
       color='steelblue', edgecolor='white')
ax.set_xlabel("Decisiveness parameter r")
ax.set_ylabel("Convergence rate (%)")
ax.set_title("Convergence Rate of Synchronous BRD vs. r\n"
             f"(n={n_players} players, V={V}, "
             f"{n_seeds} random initialisations)")
ax.set_ylim(0, 110)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig04_convergence_rate_vs_r.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig04_convergence_rate_vs_r.png")


# Figure 5 - Mean iterations vs r
fig, ax = plt.subplots(figsize=(8, 4))
mean_iters_vals = [summary[r]['mean_iterations'] for r in r_values]
ax.plot([str(r) for r in r_values], mean_iters_vals,
        'o-', color='darkorange', markersize=8)
ax.set_xlabel("Decisiveness parameter r")
ax.set_ylabel("Mean iterations to convergence")
ax.set_title("Convergence Speed vs. Decisiveness Parameter r")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig05_convergence_speed_vs_r.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig05_convergence_speed_vs_r.png")


# Figure 6 - Rent dissipation vs r
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot([str(r) for r in r_values],
        [summary[r]['mean_total_effort'] for r in r_values],
        's-', color='green', markersize=8)
ax.set_xlabel("Decisiveness parameter r")
ax.set_ylabel("Mean total equilibrium effort")
ax.set_title("Rent Dissipation vs. Decisiveness Parameter r\n"
             "(tests Nitzan 1994 non-monotonicity prediction)")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig06_rent_dissipation_vs_r.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig06_rent_dissipation_vs_r.png")


# Save raw summary data
np.save("results/data/experiment_02_summary.npy", summary)
print()
print("Data saved to results/data/experiment_02_summary.npy")
print()
print("Experiment 2 complete.")