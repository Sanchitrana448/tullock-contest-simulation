"""
experiment_03_n_sweep.py
------------------------
Sweeps the number of players n across [2, 3, 5, 10, 20].

For each value of n:
- Runs synchronous BRD from 20 random starting points
- Records: convergence rate, iterations, total effort

Directly addresses Research Objective 2 from the dissertation.

Run with: python notebooks/experiment_03_n_sweep.py
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
n_values  = [2, 3, 5, 10, 20]
r         = 1.0
V         = 10.0
n_seeds   = 20
max_iters = 2000

rng = np.random.default_rng(0)

print("Experiment 3: Sweeping number of players n")
print("=" * 55)

summary = {}

for n in n_values:
    contest = TullockContest(n=n, r=r,
                             valuations=[V] * n)
    convergence_counts = []
    iteration_counts   = []
    final_efforts_list = []
    analytical_x_star  = contest.analytical_symmetric_equilibrium()

    for seed in range(n_seeds):
        initial = rng.uniform(0.1, V * 0.8, size=n)
        result  = run_synchronous(contest, initial,
                                  max_iterations=max_iters)

        convergence_counts.append(result['converged'])
        if result['converged']:
            iteration_counts.append(result['iterations'])
        final_efforts_list.append(result['final_efforts'])

    conv_rate    = np.mean(convergence_counts)
    mean_iters   = np.mean(iteration_counts) if iteration_counts else np.nan
    mean_effort  = np.mean([e.sum() for e in final_efforts_list])

    summary[n] = {
        'convergence_rate':  conv_rate,
        'mean_iterations':   mean_iters,
        'mean_total_effort': mean_effort,
        'analytical_x_star': analytical_x_star,
        'analytical_total':  analytical_x_star * n,
    }

    print(f"n={n:2d} | Conv. rate: {conv_rate*100:.0f}% | "
          f"Mean iters: {mean_iters:.1f} | "
          f"Total effort: {mean_effort:.4f} | "
          f"Analytical total: {analytical_x_star * n:.4f}")


# Figure 7 - Convergence rate vs n
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar([str(n) for n in n_values],
       [summary[n]['convergence_rate'] * 100 for n in n_values],
       color='steelblue', edgecolor='white')
ax.set_xlabel("Number of players (n)")
ax.set_ylabel("Convergence rate (%)")
ax.set_title("Convergence Rate of Synchronous BRD vs. n\n"
             f"(r={r}, V={V}, {n_seeds} random initialisations)")
ax.set_ylim(0, 110)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig07_convergence_rate_vs_n.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig07_convergence_rate_vs_n.png")


# Figure 8 - Mean iterations vs n
fig, ax = plt.subplots(figsize=(8, 4))
mean_iters_vals = [summary[n]['mean_iterations'] for n in n_values]
ax.plot([str(n) for n in n_values], mean_iters_vals,
        'o-', color='darkorange', markersize=8)
ax.set_xlabel("Number of players (n)")
ax.set_ylabel("Mean iterations to convergence")
ax.set_title("Convergence Speed vs. Number of Players n")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig08_convergence_speed_vs_n.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig08_convergence_speed_vs_n.png")


# Figure 9 - Total effort vs n (simulation vs analytical)
fig, ax = plt.subplots(figsize=(8, 4))
sim_totals        = [summary[n]['mean_total_effort'] for n in n_values]
analytical_totals = [summary[n]['analytical_total'] for n in n_values]
ax.plot([str(n) for n in n_values], sim_totals,
        'o-', color='steelblue', markersize=8,
        label='Simulation')
ax.plot([str(n) for n in n_values], analytical_totals,
        's--', color='darkorange', markersize=8,
        label='Analytical (Tullock 1980)')
ax.set_xlabel("Number of players (n)")
ax.set_ylabel("Total equilibrium effort")
ax.set_title("Total Effort vs. Number of Players\n"
             "(Simulation vs. Analytical benchmark)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig09_total_effort_vs_n.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig09_total_effort_vs_n.png")


# Save raw data
np.save("results/data/experiment_03_summary.npy", summary)
print()
print("Data saved to results/data/experiment_03_summary.npy")
print()
print("Experiment 3 complete.")