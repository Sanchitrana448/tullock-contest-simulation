"""
experiment_01_baseline.py
-------------------------
First experiment: baseline convergence for symmetric 2-player contest.
Produces the first real dissertation figures.

Run with: python notebooks/experiment_01_baseline.py
"""

import sys
sys.path.insert(0, '.')

import numpy as np
from src.contest import TullockContest
from src.dynamics import run_synchronous, run_asynchronous, run_inertial
from src.visualisation import (plot_convergence_trajectory,
                                plot_phase_portrait_2player)

print("Experiment 1: Baseline 2-player symmetric contest")
print("=" * 55)

# Setup
contest = TullockContest(n=2, r=1.0, valuations=[10.0, 10.0])
initial = np.array([8.0, 1.0])

# Run all three update rules
result_sync     = run_synchronous(contest, initial)
result_async    = run_asynchronous(contest, initial, seed=42)
result_inertial = run_inertial(contest, initial, lam=0.5)

print(f"Synchronous:    {result_sync['iterations']} iterations, "
      f"converged={result_sync['converged']}")
print(f"Asynchronous:   {result_async['iterations']} iterations, "
      f"converged={result_async['converged']}")
print(f"Inertial (l=0.5): {result_inertial['iterations']} iterations, "
      f"converged={result_inertial['converged']}")

print()
print("Producing figures...")

# Figure 1 - Synchronous convergence trajectory
plot_convergence_trajectory(
    result_sync, contest,
    title="Synchronous BRD - 2-player symmetric (V=10, r=1)",
    filename="fig01_sync_2player_convergence.png"
)

# Figure 2 - Inertial convergence trajectory
plot_convergence_trajectory(
    result_inertial, contest,
    title="Inertial BRD (l=0.5) - 2-player symmetric (V=10, r=1)",
    filename="fig02_inertial_2player_convergence.png"
)

# Figure 3 - Phase portrait
plot_phase_portrait_2player(
    contest,
    filename="fig03_phase_portrait_r1.png"
)

print()
print("All figures saved to results/figures/")