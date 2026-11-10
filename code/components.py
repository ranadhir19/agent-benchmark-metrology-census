"""Variance-component estimators (method of moments) + cluster bootstrap.

Model (per agent): Y_ijr = p_ij + eps, binary Y.
  sigma2_task = Var_j(p_ij)                      (task sampling)
  sigma2_run  = E_j[p_ij (1 - p_ij)]             (run-level; environment
                                                  folded in under R1)
Estimators (SOLUTION_DESIGN.md SS3):
  s2_ij        = (n/(n-1)) * phat_ij (1 - phat_ij)   unbiased within-cell var
  sigma2_run   = n-weighted mean of s2_ij over tasks with n_ij >= 2
  sigma2_task  = max(0, Var(phat_ij) - mean_j[ phat_ij(1-phat_ij)/n_ij ])
Grader component: identified only from re-grades of frozen items
(estimate_grader_variance); otherwise callers report an estimability limit.
"""
import numpy as np


def _cell_stats(n, k):
    n = np.asarray(n, dtype=float)
    k = np.asarray(k, dtype=float)
    if np.any(n < 2):
        raise ValueError("insufficient repeats: every cell needs n_ij >= 2")
    phat = k / n
    return n, phat


def estimate_components(n, k):
    """Return dict with sigma2_task, sigma2_run, rho for one agent.

    n, k: per-task run counts and binary successes (all n >= 2).
    rho = sigma2_run / sigma2_task (grader = 0 by construction where grading
    is deterministic; see design SS2/E3). rho is inf if sigma2_task == 0 and
    sigma2_run > 0, nan if both are 0.
    """
    n, phat = _cell_stats(n, k)
    s2 = (n / (n - 1.0)) * phat * (1.0 - phat)
    sigma2_run = float(np.average(s2, weights=n))
    var_phat = float(np.var(phat, ddof=1)) if len(phat) > 1 else 0.0
    inflation = float(np.mean(phat * (1.0 - phat) / n))
    sigma2_task_raw = var_phat - inflation
    sigma2_task = max(0.0, sigma2_task_raw)
    if sigma2_task > 0:
        rho = sigma2_run / sigma2_task
    elif sigma2_run > 0:
        rho = float("inf")
    else:
        rho = float("nan")
    return {
        "sigma2_task": sigma2_task,
        "sigma2_task_raw": sigma2_task_raw,
        "sigma2_task_truncated": bool(sigma2_task_raw < 0),
        "sigma2_run": sigma2_run,
        "rho": rho,
        "n_tasks": int(len(phat)),
        "mean_runs_per_task": float(np.mean(n)),
    }


def estimate_components_continuous(cell_values):
    """Continuous-outcome analogue: cell_values = list of per-task run arrays.

    sigma2_run = mean within-cell sample variance (ddof=1, n-weighted);
    sigma2_task = Var(cell means) - mean(within-cell var / n_j).
    """
    means, wvars, ns = [], [], []
    for vals in cell_values:
        v = np.asarray(vals, dtype=float)
        if len(v) < 2:
            raise ValueError("insufficient repeats: every cell needs n_ij >= 2")
        means.append(float(np.mean(v)))
        wvars.append(float(np.var(v, ddof=1)))
        ns.append(len(v))
    means = np.array(means); wvars = np.array(wvars); ns = np.array(ns, dtype=float)
    sigma2_run = float(np.average(wvars, weights=ns))
    var_means = float(np.var(means, ddof=1)) if len(means) > 1 else 0.0
    sigma2_task = max(0.0, var_means - float(np.mean(wvars / ns)))
    return {"sigma2_task": sigma2_task, "sigma2_run": sigma2_run,
            "n_tasks": int(len(means))}


def estimate_grader_variance(grades):
    """Grader variance from re-grades of frozen items.

    grades: 2D array-like, items x re-grades of 0/1 grades for the SAME
    frozen trajectories. Returns mean per-item unbiased variance — the
    planted/estimand quantity E[Var(grade | frozen item)].
    """
    g = np.asarray(grades, dtype=float)
    if g.ndim != 2 or g.shape[1] < 2:
        raise ValueError("need >= 2 re-grades per frozen item")
    p = g.mean(axis=1)
    per_item = (g.shape[1] / (g.shape[1] - 1.0)) * p * (1.0 - p)
    return float(np.mean(per_item))


def paired_task_diff_variance(n_a, k_a, n_b, k_b):
    """sigma2_task,diff = Var_j(p_Aj - p_Bj), moment-corrected, paired tasks.

    Inputs are aligned per-task arrays for two agents on the SAME task set.
    """
    na, pa = _cell_stats(n_a, k_a)
    nb, pb = _cell_stats(n_b, k_b)
    if len(pa) != len(pb):
        raise ValueError("paired design needs the same task set for both agents")
    d = pa - pb
    var_d = float(np.var(d, ddof=1)) if len(d) > 1 else 0.0
    inflation = float(np.mean(pa * (1 - pa) / na + pb * (1 - pb) / nb))
    return max(0.0, var_d - inflation)


def bootstrap_components(n, k, B=2000, seed=20261030):
    """Cluster bootstrap over tasks for one agent's components and rho.

    Returns dict of percentile CIs (2.5%, 97.5%) per quantity.
    """
    n = np.asarray(n, dtype=float); k = np.asarray(k, dtype=float)
    T = len(n)
    rng = np.random.default_rng(seed)
    draws = {"sigma2_task": [], "sigma2_run": [], "rho": []}
    for _ in range(B):
        idx = rng.integers(0, T, size=T)
        est = estimate_components(n[idx], k[idx])
        draws["sigma2_task"].append(est["sigma2_task"])
        draws["sigma2_run"].append(est["sigma2_run"])
        draws["rho"].append(est["rho"])
    out = {}
    for key, vals in draws.items():
        v = np.asarray(vals, dtype=float)
        v = v[np.isfinite(v)]
        if len(v) == 0:
            out[key] = (float("nan"), float("nan"))
        else:
            out[key] = (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))
    return out


def pooled_rho(per_agent):
    """Benchmark-level rho: ratio of equal-weight mean components."""
    st = float(np.mean([a["sigma2_task"] for a in per_agent]))
    sr = float(np.mean([a["sigma2_run"] for a in per_agent]))
    rho = sr / st if st > 0 else (float("inf") if sr > 0 else float("nan"))
    return {"sigma2_task_pooled": st, "sigma2_run_pooled": sr, "rho_pooled": rho}
