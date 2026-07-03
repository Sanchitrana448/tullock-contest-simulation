"""
test_validation.py
------------------
Validates the simulation against known analytical results.

CRITICAL TEST: For the symmetric Tullock contest with
linear costs and r=1, the analytical Nash equilibrium is:
    x* = V * (n-1) / n^2

All three update rules must converge to this value.
"""




import sys
sys.path.insert(0, '.')


import numpy as np
from src.contest import TullockContest
from src.dynamics import run_synchronous, run_asynchronous, run_inertial


def test_symmetric_2player():
    print("=" * 60)
    print("TEST: 2-player symmetric contest (V=10, r=1, alpha=1)")
    print("Expected Nash equilibrium: x* = 2.5 for both players")
    print("=" * 60)

    contest = TullockContest(n=2, r=1.0, valuations=[10.0, 10.0])
    x_star = contest.analytical_symmetric_equilibrium()
    print(f"Analytical x* = {x_star}")

    initial = np.array([8.0, 1.0])
    print(f"Starting from: {initial}")
    print()

    result_sync = run_synchronous(contest, initial)
    print(f"[Synchronous]    Converged: {result_sync['converged']}, "
          f"Iterations: {result_sync['iterations']}, "
          f"Final efforts: {np.round(result_sync['final_efforts'], 4)}")
    assert np.allclose(result_sync['final_efforts'], x_star, atol=1e-4), \
        f"FAILED: Expected {x_star}, got {result_sync['final_efforts']}"
    print("  PASSED")

    result_async = run_asynchronous(contest, initial, seed=42)
    print(f"[Asynchronous]   Converged: {result_async['converged']}, "
          f"Iterations: {result_async['iterations']}, "
          f"Final efforts: {np.round(result_async['final_efforts'], 4)}")
    assert np.allclose(result_async['final_efforts'], x_star, atol=1e-4), \
        f"FAILED: Expected {x_star}, got {result_async['final_efforts']}"
    print("  PASSED")

    result_inertial = run_inertial(contest, initial, lam=0.5)
    print(f"[Inertial l=0.5] Converged: {result_inertial['converged']}, "
          f"Iterations: {result_inertial['iterations']}, "
          f"Final efforts: {np.round(result_inertial['final_efforts'], 4)}")
    assert np.allclose(result_inertial['final_efforts'], x_star, atol=1e-4), \
        f"FAILED: Expected {x_star}, got {result_inertial['final_efforts']}"
    print("  PASSED")


def test_symmetric_5player():
    print()
    print("=" * 60)
    print("TEST: 5-player symmetric contest (V=10, r=1, alpha=1)")
    print("Expected Nash equilibrium: x* = 1.6 for all players")
    print("=" * 60)

    contest = TullockContest(n=5, r=1.0, valuations=[10.0]*5)
    x_star = contest.analytical_symmetric_equilibrium()
    print(f"Analytical x* = {x_star}")

    initial = np.array([5.0, 1.0, 3.0, 2.0, 4.0])
    result = run_synchronous(contest, initial)
    print(f"[Synchronous]  Converged: {result['converged']}, "
          f"Iterations: {result['iterations']}, "
          f"Final efforts: {np.round(result['final_efforts'], 4)}")
    assert np.allclose(result['final_efforts'], x_star, atol=1e-4), \
        f"FAILED: Expected {x_star}, got {result['final_efforts']}"
    print("  PASSED")


if __name__ == "__main__":
    test_symmetric_2player()
    test_symmetric_5player()
    print()
    print("=" * 60)
    print("ALL VALIDATION TESTS PASSED")
    print("Simulation correctly recovers known analytical equilibria.")
    print("=" * 60)