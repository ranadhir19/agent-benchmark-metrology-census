"""Minimum detectable effects and design tables (SOLUTION_DESIGN.md SS5).

Paired design (same T tasks for both agents, R runs per task):
  SE_diff(R) = sqrt( sigma2_task_diff / T + (s2_run_A + s2_run_B) / (T R) )
  MDE(R)     = (z_{1-a/2} + z_{1-b}) * SE_diff(R),  a=0.05, power=0.80
             -> multiplier 2.8016 (normal) or t-based sensitivity.
Unpaired: sigma2_task_diff replaced by sigma2_task_A + sigma2_task_B.
"""
import math

from scipy import stats

Z_MULT = float(stats.norm.ppf(0.975) + stats.norm.ppf(0.80))  # 2.8016


def se_diff(T, R, run_var_sum, task_term):
    return math.sqrt(task_term / T + run_var_sum / (T * R))


def mde(T, R, run_var_sum, task_term, df=None):
    """MDE at 80% power, two-sided alpha=0.05.

    df=None -> normal critical values; df=T-1 -> t sensitivity (Bowyer et al.).
    """
    if df is None:
        mult = Z_MULT
    else:
        mult = float(stats.t.ppf(0.975, df) + stats.t.ppf(0.80, df))
    return mult * se_diff(T, R, run_var_sum, task_term)


def required_runs(delta, T, run_var_sum, task_term, mult=Z_MULT):
    """Smallest integer R with MDE(R) <= delta, or None if no R suffices.

    None happens when the task term alone already exceeds the delta budget:
    (delta/mult)^2 <= task_term / T  -> the task set must grow instead.
    """
    budget = (delta / mult) ** 2 - task_term / T
    if budget <= 0:
        return None
    return max(1, math.ceil(run_var_sum / (T * budget)))


def required_tasks(delta, R, run_var_sum, task_term, mult=Z_MULT):
    """Smallest integer T with MDE <= delta at fixed R (always solvable)."""
    per_task = task_term + run_var_sum / R
    return max(1, math.ceil(per_task / (delta / mult) ** 2))


def design_table(T, run_var_sum, task_term, deltas=(0.01, 0.03, 0.05),
                 runs_grid=(1, 2, 4, 8)):
    """Rows: MDE at each R in runs_grid; required runs per delta (or the
    required-tasks fallback at the grid's largest R when runs cannot do it)."""
    rows = {"T": T, "mde_by_runs": {}, "required": {}}
    for R in runs_grid:
        rows["mde_by_runs"][R] = {
            "normal": mde(T, R, run_var_sum, task_term),
            "t_sensitivity": mde(T, R, run_var_sum, task_term, df=T - 1),
        }
    for d in deltas:
        rr = required_runs(d, T, run_var_sum, task_term)
        entry = {"required_runs": rr}
        if rr is None:
            entry["required_tasks_at_max_grid_R"] = required_tasks(
                d, max(runs_grid), run_var_sum, task_term)
        rows["required"][d] = entry
    return rows
