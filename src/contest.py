"""
contest.py
----------
Defines the Tullock contest model.

The contest success function is:
    p_i(x) = x_i^r / sum_j(x_j^r)

Player i's payoff is:
    pi_i(x) = p_i(x) * V_i - c(x_i)

where c(x_i) is the cost function (linear by default: c(x_i) = x_i).
"""

import numpy as np


class TullockContest:
    """
    Represents a Tullock contest with n players.

    Parameters
    ----------
    n : int
        Number of players.
    r : float
        Decisiveness parameter (r > 0). Controls how much effort
        differences affect winning probability.
    valuations : array-like of shape (n,)
        V_i for each player. How much each player values the prize.
    alpha : float
        Cost function exponent. alpha=1 means linear costs c(x)=x.
        alpha=2 means convex costs c(x)=x^2.
    """

    def __init__(self, n, r, valuations, alpha=1.0):
        self.n = n
        self.r = r
        self.valuations = np.array(valuations, dtype=float)
        self.alpha = alpha

        assert n >= 2, "Need at least 2 players"
        assert r > 0, "Decisiveness parameter r must be positive"
        assert len(self.valuations) == n, "Need one valuation per player"
        assert all(v > 0 for v in self.valuations), "All valuations must be positive"
        assert alpha >= 1, "Cost exponent alpha must be >= 1"

    def winning_probability(self, efforts):
        """
        Compute the winning probability for each player.

        p_i(x) = x_i^r / sum_j(x_j^r)

        Parameters
        ----------
        efforts : array of shape (n,)
            Current effort level of each player.

        Returns
        -------
        probs : array of shape (n,)
            Winning probability for each player.
        """
        efforts = np.array(efforts, dtype=float)

        if np.all(efforts == 0):
            return np.ones(self.n) / self.n

        powered = efforts ** self.r
        total = np.sum(powered)

        return powered / total

    def cost(self, effort):
        """
        Compute cost for a given effort level.
        c(x) = x^alpha

        Parameters
        ----------
        effort : float

        Returns
        -------
        float
        """
        return effort ** self.alpha

    def payoff(self, efforts, player_index):
        """
        Compute the payoff for one player.

        pi_i = p_i(x) * V_i - c(x_i)

        Parameters
        ----------
        efforts : array of shape (n,)
        player_index : int

        Returns
        -------
        float
        """
        probs = self.winning_probability(efforts)
        prob_win = probs[player_index]
        valuation = self.valuations[player_index]
        effort_cost = self.cost(efforts[player_index])

        return prob_win * valuation - effort_cost

    def all_payoffs(self, efforts):
        """
        Compute payoffs for all players at once.

        Parameters
        ----------
        efforts : array of shape (n,)

        Returns
        -------
        array of shape (n,)
        """
        return np.array([self.payoff(efforts, i) for i in range(self.n)])

    def total_effort(self, efforts):
        """Sum of all players efforts."""
        return np.sum(efforts)

    def analytical_symmetric_equilibrium(self):
        """
        Closed-form Nash equilibrium for the SYMMETRIC case.

        Only valid when:
        - All valuations are equal
        - r = 1
        - alpha = 1

        Formula (Tullock 1980):
            x* = V * (n-1) / n^2

        Used to VALIDATE the simulation.

        Returns
        -------
        float : equilibrium effort (same for all players)
        """
        V = self.valuations[0]
        n = self.n

        if not np.allclose(self.valuations, V):
            raise ValueError(
                "Analytical formula only valid for equal valuations."
            )
        if self.r != 1.0:
            raise ValueError(
                "Analytical formula only valid for r=1."
            )
        if self.alpha != 1.0:
            raise ValueError(
                "Analytical formula only valid for alpha=1."
            )

        return V * (n - 1) / (n ** 2)