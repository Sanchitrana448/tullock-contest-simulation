"""
analysis.py
-----------
Formal statistical analysis of simulation results.

Computes:
1. Convergence rate tables across parameter space
2. Convergence speed statistics
3. Rent dissipation analysis
4. Eigenvalue-based stability analysis
5. Deviation from analytical benchmarks
"""

import numpy as np
from src.contest import TullockContest
from src.dynamics import run_synchronous, run_inertial
from src.best_response import compute_all_best_responses


# ── 1. Convergence Statistics ─────────────────────────────

def convergence_statistics(contest, n_seeds=50,
                           max_iterations=500,
                           tolerance=1e-6,
                           seed=0):
    """
    Run multiple random initialisations and compute
    detailed convergence statistics.

    Parameters
    ----------
    contest : TullockContest
    n_seeds : int
    max_iterations : int
    tolerance : float
    seed : int

    Returns
    -------
    dict with keys:
        convergence_rate   : float — fraction that converged
        mean_iterations    : float — mean iters among converged
        std_iterations     : float — std of iterations
        min_iterations     : int
        max_iterations_val : int
        mean_final_efforts : array — mean equilibrium efforts
        std_final_efforts  : array — std of equilibrium efforts
        n_converged        : int
        n_diverged         : int
    """
    rng = np.random.default_rng(seed)
    n   = contest.n
    V   = contest.valuations.max()

    converged_iters   = []
    diverged_count    = 0
    final_efforts_all = []

    for _ in range(n_seeds):
        initial = rng.uniform(0.1, V * 0.8, size=n)
        result  = run_synchronous(
            contest, initial,
            max_iterations=max_iterations,
            tolerance=tolerance
        )

        if result['converged']:
            converged_iters.append(result['iterations'])
            final_efforts_all.append(result['final_efforts'])
        else:
            diverged_count += 1

    n_converged = len(converged_iters)

    return {
        'convergence_rate':    n_converged / n_seeds,
        'mean_iterations':     np.mean(converged_iters)
                               if converged_iters else np.nan,
        'std_iterations':      np.std(converged_iters)
                               if converged_iters else np.nan,
        'min_iterations':      np.min(converged_iters)
                               if converged_iters else np.nan,
        'max_iterations_val':  np.max(converged_iters)
                               if converged_iters else np.nan,
        'mean_final_efforts':  np.mean(final_efforts_all, axis=0)
                               if final_efforts_all
                               else np.full(n, np.nan),
        'std_final_efforts':   np.std(final_efforts_all, axis=0)
                               if final_efforts_all
                               else np.full(n, np.nan),
        'n_converged':         n_converged,
        'n_diverged':          diverged_count,
    }


# ── 2. Benchmark Deviation ────────────────────────────────

def benchmark_deviation(contest, stats):
    """
    Compute deviation of simulated equilibrium from
    analytical benchmark (symmetric case only).

    Parameters
    ----------
    contest : TullockContest
    stats : dict (output of convergence_statistics)

    Returns
    -------
    dict with keys:
        analytical_x_star  : float or None
        simulated_mean     : float
        absolute_error     : float or None
        relative_error_pct : float or None
    """
    simulated_mean = np.mean(stats['mean_final_efforts'])

    try:
        x_star = contest.analytical_symmetric_equilibrium()
        abs_error = abs(simulated_mean - x_star)
        rel_error = abs_error / x_star * 100
    except ValueError:
        x_star    = None
        abs_error = None
        rel_error = None

    return {
        'analytical_x_star':   x_star,
        'simulated_mean':      simulated_mean,
        'absolute_error':      abs_error,
        'relative_error_pct':  rel_error,
    }


# ── 3. Rent Dissipation Analysis ──────────────────────────

def rent_dissipation_analysis(contest, stats):
    """
    Analyse rent dissipation at the simulated equilibrium.

    Rent dissipation = total effort / prize value
    Over-dissipation occurs when this ratio > 1.

    Parameters
    ----------
    contest : TullockContest
    stats : dict (output of convergence_statistics)

    Returns
    -------
    dict with keys:
        total_effort        : float
        prize_value         : float
        dissipation_ratio   : float
        over_dissipation    : bool
        per_player_effort   : array
        per_player_share    : array
    """
    efforts      = stats['mean_final_efforts']
    total_effort = np.sum(efforts)
    prize_value  = np.sum(contest.valuations)

    return {
        'total_effort':      total_effort,
        'prize_value':       prize_value,
        'dissipation_ratio': total_effort / prize_value,
        'over_dissipation':  total_effort > prize_value,
        'per_player_effort': efforts,
        'per_player_share':  efforts / total_effort
                             if total_effort > 0
                             else np.full(contest.n, np.nan),
    }


# ── 4. Eigenvalue Stability Analysis ─────────────────────

def eigenvalue_stability(contest, equilibrium_efforts,
                         delta=1e-5):
    """
    Assess stability of an equilibrium via eigenvalue analysis
    of the Jacobian of best response mappings.

    The spectral radius (largest absolute eigenvalue) determines
    stability:
        < 1 : stable (attracting) — dynamics converge
        = 1 : neutral
        > 1 : unstable (repelling) — dynamics diverge

    This directly operationalises the Szidarovszky & Okuguchi
    (1997) contraction mapping condition.

    Parameters
    ----------
    contest : TullockContest
    equilibrium_efforts : array of shape (n,)
        The equilibrium point to analyse.
    delta : float
        Step size for numerical Jacobian computation.

    Returns
    -------
    dict with keys:
        eigenvalues      : array of complex eigenvalues
        spectral_radius  : float — max absolute eigenvalue
        is_stable        : bool — spectral radius < 1
        jacobian         : array — the Jacobian matrix
    """
    n       = contest.n
    x0      = np.array(equilibrium_efforts, dtype=float)
    br0     = compute_all_best_responses(contest, x0)
    jacobian = np.zeros((n, n))

    # Numerical Jacobian: d(BR_i) / d(x_j)
    for j in range(n):
        x_plus      = x0.copy()
        x_plus[j]  += delta
        br_plus     = compute_all_best_responses(contest, x_plus)
        jacobian[:, j] = (br_plus - br0) / delta

    eigenvalues     = np.linalg.eigvals(jacobian)
    spectral_radius = np.max(np.abs(eigenvalues))

    return {
        'eigenvalues':     eigenvalues,
        'spectral_radius': spectral_radius,
        'is_stable':       spectral_radius < 1.0,
        'jacobian':        jacobian,
    }


# ── 5. Full Parameter Space Report ───────────────────────

def generate_full_report(r_values, n_values,
                         V=10.0, n_seeds=30,
                         max_iterations=500):
    """
    Generate a complete analysis report across
    the full r x n parameter space.

    Parameters
    ----------
    r_values : list of float
    n_values : list of int
    V : float — prize value
    n_seeds : int
    max_iterations : int

    Returns
    -------
    dict mapping (n, r) -> analysis results
    """
    report = {}

    for n in n_values:
        for r in r_values:
            contest = TullockContest(
                n=n, r=r, valuations=[V] * n
            )
            stats = convergence_statistics(
                contest,
                n_seeds=n_seeds,
                max_iterations=max_iterations
            )
            bench = benchmark_deviation(contest, stats)
            diss  = rent_dissipation_analysis(contest, stats)

            # Eigenvalue analysis only if converged
            if stats['n_converged'] > 0:
                eq_efforts = stats['mean_final_efforts']
                eig = eigenvalue_stability(
                    contest, eq_efforts
                )
            else:
                eig = {
                    'spectral_radius': np.nan,
                    'is_stable':       False,
                    'eigenvalues':     None,
                    'jacobian':        None,
                }

            report[(n, r)] = {
                'stats': stats,
                'benchmark': bench,
                'dissipation': diss,
                'eigenvalue': eig,
            }

    return report


def print_report_summary(report, r_values, n_values):
    """
    Print a formatted summary table of the full report.
    """
    print("=" * 75)
    print("FULL ANALYSIS REPORT SUMMARY")
    print("=" * 75)

    for n in n_values:
        print(f"\nn = {n} players")
        print("-" * 75)
        print(f"{'r':>6} | {'Conv%':>6} | "
              f"{'MeanIter':>9} | {'TotalEffort':>12} | "
              f"{'SpectralR':>10} | {'Stable':>7}")
        print("-" * 75)

        for r in r_values:
            s  = report[(n, r)]['stats']
            d  = report[(n, r)]['dissipation']
            e  = report[(n, r)]['eigenvalue']

            conv_pct  = f"{s['convergence_rate']*100:.0f}%"
            mean_iter = (f"{s['mean_iterations']:.1f}"
                         if not np.isnan(s['mean_iterations'])
                         else "N/A")
            tot_eff   = f"{d['total_effort']:.4f}"
            spec_r    = (f"{e['spectral_radius']:.4f}"
                         if not np.isnan(e['spectral_radius'])
                         else "N/A")
            stable    = ("Yes" if e['is_stable'] else "No")

            print(f"{r:>6.1f} | {conv_pct:>6} | "
                  f"{mean_iter:>9} | {tot_eff:>12} | "
                  f"{spec_r:>10} | {stable:>7}")