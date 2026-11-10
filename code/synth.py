"""Synthetic data with KNOWN variance components (harness anchor).

Task propensities p_j ~ Beta(a, b):
  planted sigma2_task = ab / ((a+b)^2 (a+b+1))
  planted sigma2_run  = E[p(1-p)] = ab / ((a+b)(a+b+1))
Outcomes Y_jr ~ Bernoulli(p_j). Recovery of the planted components by the
moment estimators in components.py is the Stage 6 anchor check.
"""
import numpy as np


def beta_component_truth(a, b):
    s = a + b
    return {
        "sigma2_task": a * b / (s * s * (s + 1.0)),
        "sigma2_run": a * b / (s * (s + 1.0)),
    }


def generate_agent(a, b, T, R, seed):
    """Return (n, k) per-task arrays for one synthetic agent."""
    rng = np.random.default_rng(seed)
    p = rng.beta(a, b, size=T)
    k = rng.binomial(R, p)
    n = np.full(T, R, dtype=int)
    return n, k, p


def generate_agent_logitnormal(mu, tau, T, R, seed):
    """Synthetic agent from the Arm B model itself (addendum SS6.2):
    v_j ~ Normal(0, tau), p_j = sigmoid(mu + v_j), Y_jr ~ Bernoulli(p_j).

    Planted components are the probability-scale quantities of the
    REALISED task population (the frozen estimand definitions):
      sigma2_task = Var_j(p_j) (ddof=1),  sigma2_run = mean_j p_j(1-p_j).
    Returns (n, k, p, truth) with truth carrying those planted values.
    """
    rng = np.random.default_rng(seed)
    v = rng.normal(0.0, tau, size=T)
    p = 1.0 / (1.0 + np.exp(-(mu + v)))
    k = rng.binomial(R, p)
    n = np.full(T, R, dtype=int)
    truth = {
        "sigma2_task": float(np.var(p, ddof=1)),
        "sigma2_run": float(np.mean(p * (1.0 - p))),
    }
    truth["rho"] = truth["sigma2_run"] / truth["sigma2_task"]
    return n, k, p, truth


def generate_frozen_grades(T, q, n_regrades, seed):
    """Frozen items re-graded with flip probability q.

    True item outcomes fixed; each re-grade flips with prob q, so the
    planted grader variance is q(1-q). Returns items x re-grades array.
    """
    rng = np.random.default_rng(seed)
    truth = rng.integers(0, 2, size=T)
    flips = rng.random((T, n_regrades)) < q
    grades = np.where(flips, 1 - truth[:, None], truth[:, None])
    return grades
