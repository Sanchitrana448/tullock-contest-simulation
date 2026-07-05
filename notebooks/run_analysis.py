"""
run_analysis.py
---------------
Runs the full formal analysis and prints the complete
report with all statistics needed for the dissertation.

Run with: python notebooks/run_analysis.py
"""

import sys
sys.path.insert(0, '.')

import numpy as np
import os

os.makedirs("results/data", exist_ok=True)

from src.analysis import generate_full_report, print_report_summary

r_values = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
n_values = [2, 3, 5, 10, 20]
V        = 10.0

print("Running full analysis report...")
print(f"Grid: {len(r_values)} r values x {len(n_values)} n values")
print()

report = generate_full_report(
    r_values=r_values,
    n_values=n_values,
    V=V,
    n_seeds=10,
    max_iterations=200
)

print_report_summary(report, r_values, n_values)

np.save("results/data/full_analysis_report.npy", report)
print()
print("Report saved to results/data/full_analysis_report.npy")
print()
print("Analysis complete.")