"""
visualisation.py
----------------
All plotting functions for the dissertation.
Saves figures to results/figures/ automatically.
"""

import numpy as np
from pathlib import Path

FIGURE_DIR = Path(__file__).resolve().parents[1] / "results" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    _MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    cm = None
    _MATPLOTLIB_AVAILABLE = False

if _MATPLOTLIB_AVAILABLE:
    plt.rcParams.update({
        'figure.dpi': 150,
        'font.size': 11,
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'legend.fontsize': 10,
        'lines.linewidth': 2,
    })

def _ensure_matplotlib():
    if not _MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "Matplotlib is required for visualization. "
            "Install it with 'pip install matplotlib'."
        )


def plot_convergence_trajectory(result, contest, title=None, filename=None):
    """
    Plot how each player's effort evolves over iterations.

    Parameters
    ----------
    result : dict (output from run_synchronous / run_asynchronous etc.)
    contest : TullockContest
    title : str (optional)
    filename : str (optional, saves to results/figures/ if given)
    """
    _ensure_matplotlib()
    trajectory = result['trajectory']
    n_iters, n_players = trajectory.shape

    fig, ax = plt.subplots(figsize=(9, 5))
    colours = cm.tab10(np.linspace(0, 1, n_players))

    for i in range(n_players):
        ax.plot(trajectory[:, i], color=colours[i],
                label=f'Player {i+1}')

    try:
        x_star = contest.analytical_symmetric_equilibrium()
        ax.axhline(x_star, color='black', linestyle='--',
                   linewidth=1.5,
                   label=f'Nash equilibrium (x*={x_star:.3f})')
    except (ValueError, AssertionError):
        pass

    ax.set_xlabel("Iteration")
    ax.set_ylabel("Effort")
    ax.set_title(title or
                 f"Best-Response Dynamics (n={contest.n}, r={contest.r})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if filename:
        path = FIGURE_DIR / filename
        plt.savefig(str(path), bbox_inches='tight')
        print(f"Saved: {path}")

    plt.show()
    plt.close()


def plot_phase_portrait_2player(contest, grid_size=20, filename=None):
    """
    Phase portrait for a 2-player contest.

    Shows arrows pointing from current efforts toward
    best responses. Nash equilibrium is where arrows
    have zero length.

    Only works for n=2.
    """
    assert contest.n == 2, "Phase portrait only for 2-player contests"

    from src.best_response import compute_all_best_responses

    x_max = contest.valuations.max() * 0.8
    xs = np.linspace(0.01, x_max, grid_size)
    X1, X2 = np.meshgrid(xs, xs)

    U = np.zeros_like(X1)
    V_field = np.zeros_like(X2)

    for i in range(grid_size):
        for j in range(grid_size):
            efforts = np.array([X1[i, j], X2[i, j]])
            br = compute_all_best_responses(contest, efforts)
            U[i, j] = br[0] - X1[i, j]
            V_field[i, j] = br[1] - X2[i, j]

    _ensure_matplotlib()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.quiver(X1, X2, U, V_field, alpha=0.7, color='steelblue')

    try:
        x_star = contest.analytical_symmetric_equilibrium()
        ax.plot(x_star, x_star, 'r*', markersize=15,
                label=f'Nash equilibrium ({x_star:.2f}, {x_star:.2f})')
        ax.legend()
    except (ValueError, AssertionError):
        pass

    ax.set_xlabel("Player 1 effort (x1)")
    ax.set_ylabel("Player 2 effort (x2)")
    ax.set_title(f"Phase Portrait - 2-player contest (r={contest.r})")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if filename:
        path = FIGURE_DIR / filename
        plt.savefig(str(path), bbox_inches='tight')
        print(f"Saved: {path}")

    plt.show()
    plt.close()


def plot_rent_dissipation(results_by_r, filename=None):
    """
    Plot total equilibrium effort vs r.

    Parameters
    ----------
    results_by_r : dict mapping r -> final_efforts array
    """
    r_vals = sorted(results_by_r.keys())
    dissipation = [results_by_r[r].sum() for r in r_vals]

    _ensure_matplotlib()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(r_vals, dissipation, 'o-', color='darkorange')
    ax.set_xlabel("Decisiveness parameter r")
    ax.set_ylabel("Total equilibrium effort (rent dissipation)")
    ax.set_title("Rent Dissipation vs. Decisiveness Parameter")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if filename:
        path = FIGURE_DIR / filename
        plt.savefig(str(path), bbox_inches='tight')
        print(f"Saved: {path}")

    plt.show()
    plt.close()