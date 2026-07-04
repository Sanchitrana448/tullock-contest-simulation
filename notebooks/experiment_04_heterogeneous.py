"""
experiment_04_heterogeneous.py
------------------------------
Tests heterogeneous player valuations.

Compares symmetric (equal valuations) vs asymmetric
(different valuations) contests.

Checks whether Cornes & Hartley (2005) prediction holds:
higher valuation players should exert more effort at equilibrium.

Run with: python notebooks/experiment_04_heterogeneous.py
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

rng = np.random.default_rng(0)
n_seeds   = 20
max_iters = 500

print("Experiment 4: Heterogeneous player valuations")
print("=" * 55)

# ── Case 1: Symmetric baseline ────────────────────────────
print("\nCase 1: Symmetric (V1=V2=10)")
contest_sym = TullockContest(n=2, r=1.0,
                             valuations=[10.0, 10.0])
sym_results = []
for _ in range(n_seeds):
    initial = rng.uniform(0.1, 8.0, size=2)
    result  = run_synchronous(contest_sym, initial,
                              max_iterations=max_iters)
    sym_results.append(result)

sym_conv = np.mean([r['converged'] for r in sym_results])
sym_efforts = np.mean([r['final_efforts']
                       for r in sym_results], axis=0)
print(f"Convergence rate: {sym_conv*100:.0f}%")
print(f"Mean final efforts: P1={sym_efforts[0]:.4f}, "
      f"P2={sym_efforts[1]:.4f}")
print(f"Analytical x*=2.5 for both players")


# ── Case 2: Mild asymmetry ────────────────────────────────
print("\nCase 2: Mild asymmetry (V1=8, V2=12)")
contest_mild = TullockContest(n=2, r=1.0,
                              valuations=[8.0, 12.0])
mild_results = []
for _ in range(n_seeds):
    initial = rng.uniform(0.1, 8.0, size=2)
    result  = run_synchronous(contest_mild, initial,
                              max_iterations=max_iters)
    mild_results.append(result)

mild_conv = np.mean([r['converged'] for r in mild_results])
mild_efforts = np.mean([r['final_efforts']
                        for r in mild_results], axis=0)
print(f"Convergence rate: {mild_conv*100:.0f}%")
print(f"Mean final efforts: P1={mild_efforts[0]:.4f}, "
      f"P2={mild_efforts[1]:.4f}")
print(f"Cornes & Hartley prediction: P2 effort > P1 effort "
      f"(higher valuation = more effort)")
if mild_efforts[1] > mild_efforts[0]:
    print("Prediction CONFIRMED")
else:
    print("Prediction NOT confirmed")


# ── Case 3: Strong asymmetry ──────────────────────────────
print("\nCase 3: Strong asymmetry (V1=2, V2=18)")
contest_strong = TullockContest(n=2, r=1.0,
                                valuations=[2.0, 18.0])
strong_results = []
for _ in range(n_seeds):
    initial = rng.uniform(0.1, 8.0, size=2)
    result  = run_synchronous(contest_strong, initial,
                              max_iterations=max_iters)
    strong_results.append(result)

strong_conv = np.mean([r['converged'] for r in strong_results])
strong_efforts = np.mean([r['final_efforts']
                          for r in strong_results], axis=0)
print(f"Convergence rate: {strong_conv*100:.0f}%")
print(f"Mean final efforts: P1={strong_efforts[0]:.4f}, "
      f"P2={strong_efforts[1]:.4f}")
if strong_efforts[1] > strong_efforts[0]:
    print("Prediction CONFIRMED")
else:
    print("Prediction NOT confirmed")


# ── Case 4: Valuation sweep ───────────────────────────────
print("\nCase 4: Sweeping V2 while V1=10 fixed")
v2_values = [5.0, 8.0, 10.0, 12.0, 15.0, 20.0]
p1_efforts = []
p2_efforts = []

for v2 in v2_values:
    contest = TullockContest(n=2, r=1.0,
                             valuations=[10.0, v2])
    seed_efforts = []
    for _ in range(n_seeds):
        initial = rng.uniform(0.1, 8.0, size=2)
        result  = run_synchronous(contest, initial,
                                  max_iterations=max_iters)
        if result['converged']:
            seed_efforts.append(result['final_efforts'])

    if seed_efforts:
        mean_e = np.mean(seed_efforts, axis=0)
        p1_efforts.append(mean_e[0])
        p2_efforts.append(mean_e[1])
    else:
        p1_efforts.append(np.nan)
        p2_efforts.append(np.nan)

    print(f"V2={v2:.0f} | P1 effort: {p1_efforts[-1]:.4f} | "
          f"P2 effort: {p2_efforts[-1]:.4f}")


# ── Figure 10: Effort vs valuation ────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(v2_values, p1_efforts, 'o-', color='steelblue',
        markersize=8, label='Player 1 (V1=10, fixed)')
ax.plot(v2_values, p2_efforts, 's-', color='darkorange',
        markersize=8, label='Player 2 (V2 varies)')
ax.axvline(10, color='grey', linestyle='--',
           alpha=0.5, label='Symmetric point (V2=10)')
ax.set_xlabel("Player 2 valuation (V2)")
ax.set_ylabel("Equilibrium effort")
ax.set_title("Equilibrium Effort vs. Valuation\n"
             "(tests Cornes & Hartley 2005 prediction)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig10_effort_vs_valuation.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig10_effort_vs_valuation.png")


# ── Figure 11: Comparison bar chart ──────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
cases    = ['Symmetric\nV1=V2=10',
            'Mild asymmetry\nV1=8, V2=12',
            'Strong asymmetry\nV1=2, V2=18']
p1_bars  = [sym_efforts[0], mild_efforts[0], strong_efforts[0]]
p2_bars  = [sym_efforts[1], mild_efforts[1], strong_efforts[1]]
x        = np.arange(len(cases))
width    = 0.35

ax.bar(x - width/2, p1_bars, width, label='Player 1',
       color='steelblue')
ax.bar(x + width/2, p2_bars, width, label='Player 2',
       color='darkorange')
ax.set_xlabel("Contest type")
ax.set_ylabel("Mean equilibrium effort")
ax.set_title("Equilibrium Efforts Under Symmetric vs Asymmetric Valuations")
ax.set_xticks(x)
ax.set_xticklabels(cases)
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("results/figures/fig11_symmetric_vs_asymmetric.png",
            bbox_inches='tight')
plt.show()
plt.close()
print("Saved: results/figures/fig11_symmetric_vs_asymmetric.png")


# Save data
summary = {
    'symmetric':      {'convergence': sym_conv,
                       'efforts': sym_efforts},
    'mild_asymmetry': {'convergence': mild_conv,
                       'efforts': mild_efforts},
    'strong_asymmetry':{'convergence': strong_conv,
                        'efforts': strong_efforts},
    'valuation_sweep': {'v2_values': v2_values,
                        'p1_efforts': p1_efforts,
                        'p2_efforts': p2_efforts},
}
np.save("results/data/experiment_04_summary.npy", summary)
print()
print("Data saved to results/data/experiment_04_summary.npy")
print()
print("Experiment 4 complete.")