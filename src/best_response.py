"""
best_response.py
----------------
Given everyone else's effort levels, computes the best (optimal)
effort for a single player.
"""

import numpy as np
from src.contest import TullockContest


def _minimize_scalar_bounded(func, bounds, xatol=1e-10, maxiter=200):
    """Minimise a scalar function on a bounded interval with golden-section search."""
    a, b = bounds
    phi = (np.sqrt(5) - 1) / 2
    c = b - phi * (b - a)
    d = a + phi * (b - a)
    fc = func(c)
    fd = func(d)

    for _ in range(maxiter):
        if abs(b - a) < xatol:
            break
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a)
            fc = func(c)
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a)
            fd = func(d)

    return c if fc < fd else d


def compute_best_response(contest, player_index, others_efforts,
                          x_min=1e-8, x_max=100.0):
    """
    Find player i's best response to competitors' effort levels.

    Solves:
        max_{x_i >= 0} pi_i(x_i, x_{-i})

    We minimise the NEGATIVE payoff (since scipy only minimises).

    Parameters
    ----------
    contest : TullockContest
    player_index : int
        Which player (0-indexed) is best-responding.
    others_efforts : array of shape (n-1,)
        Current effort levels of all OTHER players.
    x_min : float
        Minimum effort to search over.
    x_max : float
        Maximum effort to search over.

    Returns
    -------
    float : best-response effort level for player i.
    """

    def payoff_to_maximise(x_i):
        efforts = np.insert(others_efforts, player_index, x_i)
        return -contest.payoff(efforts, player_index)

    best_x = _minimize_scalar_bounded(
        payoff_to_maximise,
        bounds=(x_min, x_max),
        xatol=1e-10
    )

    return best_x


def compute_all_best_responses(contest, efforts):
    """
    Compute the best response for every player given current efforts.

    Parameters
    ----------
    contest : TullockContest
    efforts : array of shape (n,)

    Returns
    -------
    array of shape (n,) : best-response effort for each player.
    """
    n = contest.n
    best_responses = np.zeros(n)

    for i in range(n):
        others = np.delete(efforts, i)
        best_responses[i] = compute_best_response(
            contest, i, others
        )

    return best_responses