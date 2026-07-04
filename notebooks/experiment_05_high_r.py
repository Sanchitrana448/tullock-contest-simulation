"""
experiment_05_high_r.py
-----------------------
Probes high r values in detail to characterise
non-convergence behaviour.

Investigates:
1. Exactly where convergence breaks down between r=2 and r=3
2. Whether non-convergence means cycling or chaotic behaviour
3. Whether inertial dynamics can rescue convergence at high r

Run with: python notebooks/experiment_05_high_r.py
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("results/figures", exist_ok=True)
os.makedirs("results/data", exist_ok=True)

from src.contest import TullockContest
from src.dynamics import run_synchronous, run_inertial

rng = np.random.default_rng(0)
n_seeds   = 20
max_iters = 500

print("Experiment 5: Probing high r non-convergence")
print("=" * 55)


# ── Part 1: Fine-grained r sweep ─────────────────────────
print("\nPart 1: Fine-grained r sweep (r from 2.0 to 3.5)")
r_fine    = [2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.5]
conv_rates = []

for r in r_fine:
    contest = TullockContest(n=2, r=r, valuations=[10.0, 10.0])
    conv_count = []
    for _ in range(n_seeds):
        initial = rng.uniform(0.1, 8.0, size=2)
        result  = run_synchronous(contest, initial,
                                  max_iterations=max_iters)
        conv_count.append(result['converged'])
    rate = np.mean(conv_count)
    conv_rates.append(rate)
    print(f"r={r:.1f} | Conv. rate: {rate*100:.0f}%")


# ── Part 2: What does non-convergence look like? ──────────
print("\nPart 2: Trajectory at r=3.0 (non-convergent case)")
contest_high = TullockContest(n=2, r=3.0,
                              valuations=[10.0, 10.0])
initial = np.array([4.0, 1.0])
result_high  = run_synchronous(contest_high, initial,
                               max_iterations=100)
trajectory   = result_high['trajectory']
print(f"First 10 effort pairs (Player1, Player2):")
for t in range(min(10, len(trajectory))):
    print(f"  t={t}: ({trajectory[t,0]:.4f}, {trajectory[t,1]:.4f})")


# ── Part 3: Can inertial dynamics rescue convergence? ─────
print("\nPart 3: Inertial dynamics at r=3.0")
lambda_values = [0.8, 0.5, 0.3, 0.1]

for lam in lambda_values:
    conv_count = []
    for _ in range(n_seeds):
        initial = rng.uniform(0.1, 8.0, size=2)
        result  = run_inertial(contest_high, initial,
                               lam=lam,
                               max_iterations=max_iters)
        conv_count.append(result['converged'])
    rate = np.mean(conv_count)
    print(f"lambda={lam:.1f} | Conv. rate: {rate*100:.0f}%")


# ── Figure 12: Fine-grained convergence rate vs r ─────────
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot([str(r) for r in r_fine], 
        [c * 100 for c in conv_rates],
        'o-', color='steelblue', markersize=8)
ax.axhline(50, color='red', linestyle='--',
           alpha=0.5, label='50% threshold')
ax.set_xlabel("Decisiveness parameter r")
ax.set_ylabel("Convergence rate (%)")
ax.set_title("Fine-Grained Convergence Rate vs. r\n"
             "(identifying exact breakdown point)")
ax.set_ylim(-5, 110)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig12_fine_r_convergence.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("\nSaved: results/figures/fig12_fine_r_convergence.png")


# ── Figure 13: Non-convergent trajectory at r=3.0 ─────────
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(trajectory[:, 0], color='steelblue',
        label='Player 1')
ax.plot(trajectory[:, 1], color='darkorange',
        label='Player 2')
ax.set_xlabel("Iteration")
ax.set_ylabel("Effort")
ax.set_title("Non-Convergent Trajectory at r=3.0\n"
             "(cycling behaviour)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig13_nonconvergent_trajectory.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig13_nonconvergent_trajectory.png")


# ── Figure 14: Inertial rescue at r=3.0 ───────────────────
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar([str(l) for l in lambda_values],
       [np.mean([run_inertial(
           contest_high,
           rng.uniform(0.1, 8.0, size=2),
           lam=l,
           max_iterations=max_iters)['converged']
        for _ in range(n_seeds)]) * 100
        for l in lambda_values],
       color='green', edgecolor='white')
ax.set_xlabel("Learning rate (lambda)")
ax.set_ylabel("Convergence rate (%)")
ax.set_title("Inertial Dynamics at r=3.0\n"
             "(can slower updating rescue convergence?)")
ax.set_ylim(0, 110)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig14_inertial_rescue.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig14_inertial_rescue.png")


# Save data
summary = {
    'r_fine':     r_fine,
    'conv_rates': conv_rates,
    'trajectory_r3': trajectory,
}
np.save("results/data/experiment_05_summary.npy", summary)
print()
print("Data saved to results/data/experiment_05_summary.npy")
print()
print("Experiment 5 complete.")