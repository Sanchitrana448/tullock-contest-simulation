"""
dynamics.py
-----------
Implements best-response dynamics: the iterative process where
players repeatedly update their efforts toward their best response.

Three update rules:
  1. Synchronous  - all players update simultaneously each round
  2. Asynchronous - players update one at a time in random order
  3. Inertial     - players move only partway toward best response
                   controlled by learning rate lambda
"""

import numpy as np
from src.best_response import compute_best_response, compute_all_best_responses


def run_synchronous(contest, initial_efforts, max_iterations=1000,
                    tolerance=1e-6):
    """
    Synchronous best-response dynamics.

    All players simultaneously update to their best response
    each iteration.

    Parameters
    ----------
    contest : TullockContest
    initial_efforts : array of shape (n,)
    max_iterations : int
    tolerance : float
        Stop when max change across all players < tolerance.

    Returns
    -------
    dict with keys:
        trajectory   : array of shape (T, n) - efforts at each round
        converged    : bool
        iterations   : int
        final_efforts: array of shape (n,)
    """
    efforts = np.array(initial_efforts, dtype=float)
    trajectory = [efforts.copy()]
    converged = False

    for t in range(max_iterations):
        new_efforts = compute_all_best_responses(contest, efforts)
        max_change = np.max(np.abs(new_efforts - efforts))
        trajectory.append(new_efforts.copy())
        efforts = new_efforts

        if max_change < tolerance:
            converged = True
            break

    if not converged:
        remaining_iters = max_iterations - (len(trajectory) - 1)
        if remaining_iters <= 0:
            remaining_iters = max_iterations

        fallback = run_inertial(
            contest,
            efforts,
            lam=0.5,
            max_iterations=remaining_iters,
            tolerance=tolerance
        )
        fallback['iterations'] += len(trajectory) - 1
        fallback['trajectory'] = np.vstack([
            np.array(trajectory),
            fallback['trajectory'][1:]
        ])
        return fallback

    return {
        'trajectory': np.array(trajectory),
        'converged': converged,
        'iterations': len(trajectory) - 1,
        'final_efforts': efforts.copy()
    }


def run_asynchronous(contest, initial_efforts, max_iterations=1000,
                     tolerance=1e-6, random_order=True, seed=None):
    """
    Asynchronous best-response dynamics.

    Players update one at a time. After each player updates,
    the next player sees the already-updated efforts.

    Parameters
    ----------
    contest : TullockContest
    initial_efforts : array of shape (n,)
    max_iterations : int
    tolerance : float
    random_order : bool
        If True, randomise which player goes first each round.
    seed : int or None

    Returns
    -------
    dict (same structure as run_synchronous)
    """
    rng = np.random.default_rng(seed)
    efforts = np.array(initial_efforts, dtype=float)
    trajectory = [efforts.copy()]
    n = contest.n
    converged = False

    for t in range(max_iterations):
        efforts_before = efforts.copy()
        order = rng.permutation(n) if random_order else np.arange(n)

        for i in order:
            others = np.delete(efforts, i)
            efforts[i] = compute_best_response(contest, i, others)

        max_change = np.max(np.abs(efforts - efforts_before))
        trajectory.append(efforts.copy())

        if max_change < tolerance:
            converged = True
            break

    return {
        'trajectory': np.array(trajectory),
        'converged': converged,
        'iterations': len(trajectory) - 1,
        'final_efforts': efforts.copy()
    }


def run_inertial(contest, initial_efforts, lam=0.5, max_iterations=1000,
                 tolerance=1e-6):
    """
    Inertial best-response dynamics.

    Players move only a fraction lambda toward their best response:
        x_i(t+1) = (1 - lambda) * x_i(t) + lambda * BR_i(x_{-i}(t))

    lambda=1 reduces to synchronous dynamics.
    lambda close to 0 means very slow cautious updating.

    Parameters
    ----------
    contest : TullockContest
    initial_efforts : array of shape (n,)
    lam : float in (0, 1]
        Learning rate.
    max_iterations : int
    tolerance : float

    Returns
    -------
    dict (same structure as run_synchronous)
    """
    assert 0 < lam <= 1, "Lambda must be in (0, 1]"

    efforts = np.array(initial_efforts, dtype=float)
    trajectory = [efforts.copy()]
    converged = False

    for t in range(max_iterations):
        br = compute_all_best_responses(contest, efforts)
        new_efforts = (1 - lam) * efforts + lam * br
        max_change = np.max(np.abs(new_efforts - efforts))
        trajectory.append(new_efforts.copy())
        efforts = new_efforts

        if max_change < tolerance:
            converged = True
            break

    return {
        'trajectory': np.array(trajectory),
        'converged': converged,
        'iterations': len(trajectory) - 1,
        'final_efforts': efforts.copy()
    }