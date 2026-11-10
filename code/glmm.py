"""Arm B — hierarchical Bayesian / GLMM partial pooling (CO-PRIMARY).

Implements EXPERIMENTS_ADDENDUM_STAGE7.md SS6.2 exactly as frozen
(2026-10-31T16:00:07Z). Both arms estimate the SAME estimands E1-E6 on
the SAME cells (SS6 preamble); this module is the model-based arm.

Binary model (per benchmark, per agent i; cells with n_ij >= 2):
    Y_ijr ~ Bernoulli(p_ij),  logit(p_ij) = mu_i + v_ij,
    v_ij ~ Normal(0, tau_i) i.i.d. across tasks j.
Probability-scale derivation (SS6.2): for each posterior draw, compute
p_ij over the agent's observed tasks, then
    E1_B(i) = Var_j(p_ij)          (ddof=1, the area convention of
                                    code/components.py)
    E2_B(i) = mean_j[p_ij (1 - p_ij)]
E4_B pools per-agent draws with equal agent weights, rho_B computed
draw-by-draw (pooled_rho_binary below), exactly as E4 does for Arm A.

Grader facet (only where a corpus re-grades frozen trajectories):
    logit(p_ijg) = mu_i + v_ij + w_ijg,  w_ijg ~ Normal(0, tau_g,i),
    E3_B(i) = E_j[ Var_g(p_ijg) ] per draw (Var over re-grades, ddof=1).

Continuous secondary endpoint (same nesting, original scale):
    Y_ijr = mu_i + v_ij + eps_ijr,  v_ij ~ Normal(0, tau_i),
    eps_ijr ~ Normal(0, sigma_i);  E1_B(i) = tau_i^2, E2_B(i) = sigma_i^2
read from the posterior directly.

Priors (fixed; SS6.2): mu_i ~ Normal(0, 2.5^2); tau_i, tau_g,i,
sigma_i ~ Half-Normal(0, 1). Continuous arm: mu_i ~ Normal(0, 2.5^2)
where the score is in [0, 1], Normal(0, 5^2) otherwise — the choice is
determined by the corpus's recorded score range, passed in as
score_range (see the interpretation note in fit_continuous_agent).
Prior sensitivity (pre-specified, always reported alongside, never
replaces the primary): tau priors widened to Half-Normal(0, 2) and
mu_i ~ Normal(0, 5^2) — pass prior="sensitivity".

Sampler (fixed; SS6.2/SS7.2): NUTS, 4 chains, 2,000 warm-up + 2,000
post-warm-up draws per chain, target_accept = 0.95, max_treedepth = 12,
chain seeds = census seed (20261031) + chain index.

Diagnostics and failure ladder (SS6.4): R-hat <= 1.01 and bulk/tail
ESS >= 400 for mu_i, tau_i (tau_g,i where fitted) and the derived
E1_B / E2_B / rho_B; zero divergent transitions tolerated; posterior
predictive check on cell success counts (discrepancy = variance of
cell proportions across tasks), p < 0.01 or p > 0.99 flags the fit
model-misfit; prior-sensitivity shift of the benchmark rho_B posterior
mean > 0.05 flags prior-sensitive. On a first diagnostic failure
(R-hat / ESS / divergences) exactly ONE remediation is permitted —
target_accept = 0.99, warm-up doubled to 4,000, all else unchanged —
implemented by fit_binary_agent_checked; both runs are retained in
its return value. A fit still failing, or flagged model-misfit, is
recorded FAILED / FLAGGED by the caller; no third attempt exists.

Sparse cells (SS6.2): the n_ij >= 2 inclusion rule is Arm A's and is
unchanged — primary fits REFUSE cells with n_ij < 2 (ValueError,
mirroring components._cell_stats). All-success and all-failure cells
are retained. The labelled sensitivity fit including n_ij = 1 cells
is fit_binary_agent(..., include_singletons=True); it is never the
primary reading and never enters a verdict.
"""
import numpy as np

CENSUS_SEED = 20261031
N_CHAINS = 4
TUNE = 2000
DRAWS = 2000
TARGET_ACCEPT = 0.95
MAX_TREEDEPTH = 12
REMEDIATION_TARGET_ACCEPT = 0.99
REMEDIATION_TUNE = 4000

RHAT_MAX = 1.01
ESS_MIN = 400
PPC_FLAG_LO, PPC_FLAG_HI = 0.01, 0.99
PRIOR_SENSITIVITY_RHO_SHIFT = 0.05


def _pm():
    import pymc as pm
    return pm


def _az():
    import arviz as az
    return az


def _chain_seeds(seed):
    return [seed + c for c in range(N_CHAINS)]


def _expand_binary(n, k):
    """(n, k) per-task cells -> long (task_index, y) Bernoulli arrays."""
    n = np.asarray(n, dtype=int)
    k = np.asarray(k, dtype=int)
    task_idx = np.repeat(np.arange(len(n)), n)
    y = np.concatenate([
        np.concatenate([np.ones(int(kj)), np.zeros(int(nj - kj))])
        for nj, kj in zip(n, k)
    ]).astype(int)
    return task_idx, y


def _sample(model, seed, target_accept, tune, draws):
    pm = _pm()
    # PyMC 5.16: target_accept / max_treedepth are NUTS constructor
    # arguments; passing them as pm.sample kwargs routes them to
    # step_kwargs, which rejects max_treedepth. The frozen settings
    # themselves (SS6.2) are unchanged — only their API route.
    with model:
        step = pm.NUTS(target_accept=target_accept,
                       max_treedepth=MAX_TREEDEPTH)
        idata = pm.sample(
            draws=draws, tune=tune, chains=N_CHAINS, cores=N_CHAINS,
            step=step, random_seed=_chain_seeds(seed), progressbar=False,
        )
    return idata


def _diagnostics(idata, derived):
    """SS6.4 diagnostics. `derived`: dict name -> (chain, draw) array.

    Returns rhat/ess maxima/minima over the model parameters present in
    the posterior (mu, tau, tau_g, sigma) plus the derived estimands,
    the divergence count, and the boolean diagnostic pass (PPC and
    prior-sensitivity flags are computed by the callers — they are
    flags, not remediation triggers).
    """
    az = _az()
    post = idata.posterior
    params = [v for v in ("mu", "tau", "tau_g", "sigma") if v in post]
    rhat_vals, ess_bulk_vals, ess_tail_vals = [], [], []
    if params:
        r = az.rhat(idata, var_names=params)
        eb = az.ess(idata, var_names=params, method="bulk")
        et = az.ess(idata, var_names=params, method="tail")
        for v in params:
            rhat_vals.append(float(np.max(
                np.asarray(r[v].values, dtype=float))))
            ess_bulk_vals.append(float(np.min(
                np.asarray(eb[v].values, dtype=float))))
            ess_tail_vals.append(float(np.min(
                np.asarray(et[v].values, dtype=float))))
    import xarray as xr
    der_ds = xr.Dataset(
        {name: (("chain", "draw"), arr) for name, arr in derived.items()})
    if derived:
        r = az.rhat(der_ds)
        eb = az.ess(der_ds, method="bulk")
        et = az.ess(der_ds, method="tail")
        for name in derived:
            rhat_vals.append(float(np.max(np.asarray(r[name].values, dtype=float))))
            ess_bulk_vals.append(float(np.min(np.asarray(eb[name].values, dtype=float))))
            ess_tail_vals.append(float(np.min(np.asarray(et[name].values, dtype=float))))
    divergences = int(np.asarray(
        idata.sample_stats["diverging"].values).sum())
    rhat_max = max(rhat_vals) if rhat_vals else float("nan")
    ess_bulk_min = min(ess_bulk_vals) if ess_bulk_vals else float("nan")
    ess_tail_min = min(ess_tail_vals) if ess_tail_vals else float("nan")
    passed = bool(rhat_max <= RHAT_MAX and ess_bulk_min >= ESS_MIN
                  and ess_tail_min >= ESS_MIN and divergences == 0)
    return {
        "rhat_max": rhat_max, "ess_bulk_min": ess_bulk_min,
        "ess_tail_min": ess_tail_min, "divergences": divergences,
        "diagnostic_pass": passed,
    }


def _summarise(draws_2d):
    flat = np.asarray(draws_2d, dtype=float).reshape(-1)
    return {
        "mean": float(np.mean(flat)),
        "ci95": (float(np.percentile(flat, 2.5)),
                 float(np.percentile(flat, 97.5))),
        "draws": draws_2d,
        "draws_flat": flat,
    }


def fit_binary_agent(n, k, *, seed=CENSUS_SEED, prior="primary",
                     include_singletons=False, target_accept=TARGET_ACCEPT,
                     tune=TUNE, draws=DRAWS):
    """Fit the SS6.2 binary GLMM for one agent.

    n, k: per-task run counts and successes (Arm A conventions).
    Primary fits require every n_ij >= 2; include_singletons=True is
    the labelled sensitivity fit of SS6.2 and admits n_ij == 1.
    prior="sensitivity" applies the pre-specified widened priors.
    Returns posterior summaries + per-draw E1_B / E2_B + SS6.4
    diagnostics (incl. the PPC model-misfit flag).
    """
    pm = _pm()
    n = np.asarray(n, dtype=int)
    k = np.asarray(k, dtype=int)
    if include_singletons:
        if np.any(n < 1):
            raise ValueError("cells need n_ij >= 1")
    elif np.any(n < 2):
        raise ValueError("insufficient repeats: every cell needs n_ij >= 2")
    if np.any(k < 0) or np.any(k > n):
        raise ValueError("success counts must satisfy 0 <= k_ij <= n_ij")
    task_idx, y = _expand_binary(n, k)
    if prior not in ("primary", "sensitivity"):
        raise ValueError("prior must be 'primary' or 'sensitivity'")
    mu_sd = 2.5 if prior == "primary" else 5.0
    tau_sd = 1.0 if prior == "primary" else 2.0
    return _fit_binary_finish(n, k, task_idx, y, seed=seed, prior=prior,
                              mu_sd=mu_sd, tau_sd=tau_sd,
                              target_accept=target_accept, tune=tune,
                              draws=draws)


def _fit_binary_finish(n, k, task_idx, y, *, seed, prior, mu_sd, tau_sd,
                       target_accept, tune, draws):
    pm = _pm()
    T = len(n)
    with pm.Model() as model:
        mu = pm.Normal("mu", 0.0, mu_sd)
        tau = pm.HalfNormal("tau", tau_sd)
        v = pm.Normal("v", 0.0, tau, shape=T)
        pm.Bernoulli("y", logit_p=mu + v[task_idx], observed=y)
        idata = _sample(model, seed, target_accept, tune, draws)
    post = idata.posterior
    mu_d = np.asarray(post["mu"].values)              # (chain, draw)
    v_d = np.asarray(post["v"].values)                # (chain, draw, T)
    p = 1.0 / (1.0 + np.exp(-(mu_d[:, :, None] + v_d)))
    e1 = np.var(p, axis=2, ddof=1)
    e2 = np.mean(p * (1.0 - p), axis=2)
    diag = _diagnostics(idata, {"E1_B": e1, "E2_B": e2})
    # PPC: discrepancy = variance of cell proportions across tasks.
    rng = np.random.default_rng(seed)
    prop_obs = k / n
    disc_obs = float(np.var(prop_obs, ddof=1))
    flat_p = p.reshape(-1, T)
    nrep = flat_p.shape[0]
    k_rep = rng.binomial(n[None, :], flat_p)
    disc_rep = np.var(k_rep / n[None, :], axis=1, ddof=1)
    ppc_p = float(np.mean(disc_rep >= disc_obs)) if nrep else float("nan")
    return {
        "arm": "B", "endpoint": "binary", "prior": prior,
        "n_tasks": int(T), "n_obs": int(len(y)),
        "mu": _summarise(mu_d), "tau": _summarise(
            np.asarray(post["tau"].values)),
        "E1_B": _summarise(e1), "E2_B": _summarise(e2),
        "ppc_p": ppc_p,
        "model_misfit_flag": bool(ppc_p < PPC_FLAG_LO or ppc_p > PPC_FLAG_HI),
        "diagnostics": diag,
    }


def fit_binary_agent_checked(n, k, *, seed=CENSUS_SEED, prior="primary"):
    """SS6.4 failure ladder around fit_binary_agent (binary endpoint).

    Runs the primary fit; on a diagnostic failure (R-hat / ESS /
    divergences) applies the single permitted remediation
    (target_accept = 0.99, warm-up 4,000) exactly once. Both runs are
    retained. Status: PASS / REMEDIATED_PASS / FAILED; a model-misfit
    flag (PPC) is carried as 'FLAGGED' alongside, per SS6.4(2).
    """
    primary = fit_binary_agent(n, k, seed=seed, prior=prior)
    out = {"primary": primary, "remediation": None,
           "fit_used": "primary", "status": "PASS"}
    if primary["diagnostics"]["diagnostic_pass"]:
        if primary["model_misfit_flag"]:
            out["status"] = "FLAGGED"
        return out
    remed = fit_binary_agent(n, k, seed=seed, prior=prior,
                             target_accept=REMEDIATION_TARGET_ACCEPT,
                             tune=REMEDIATION_TUNE)
    out["remediation"] = remed
    if remed["diagnostics"]["diagnostic_pass"]:
        out["fit_used"] = "remediation"
        out["status"] = "REMEDIATED_PASS" if not remed["model_misfit_flag"] \
            else "FLAGGED"
    else:
        out["fit_used"] = "remediation"
        out["status"] = "FAILED"
    return out


def pooled_rho_binary(fits):
    """E4_B for one benchmark from per-agent fit_binary_agent results.

    Equal agent weights, rho_B computed draw-by-draw (SS6.2): for each
    draw index, rho = mean_i E2_B(i) / mean_i E1_B(i) — Arm A's pooled
    construction (components.pooled_rho) applied per draw. Draw counts
    must agree across agents (same frozen sampler settings).
    """
    e1 = [f["E1_B"]["draws_flat"] for f in fits]
    e2 = [f["E2_B"]["draws_flat"] for f in fits]
    if len({len(x) for x in e1}) != 1:
        raise ValueError("per-agent draw counts differ; cannot pool draws")
    e1m = np.mean(np.vstack(e1), axis=0)
    e2m = np.mean(np.vstack(e2), axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        rho = np.where(e1m > 0, e2m / e1m, np.nan)
    return {"rho_B_mean": float(np.nanmean(rho)),
            "rho_B_ci95": (float(np.nanpercentile(rho, 2.5)),
                           float(np.nanpercentile(rho, 97.5))),
            "rho_B_draws": rho, "n_agents": len(fits)}


def prior_sensitivity_flag(rho_primary, rho_sensitivity):
    """SS6.4: widening the priors moving the benchmark rho_B posterior
    mean by more than 0.05 flags the fit prior-sensitive."""
    shift = abs(rho_sensitivity["rho_B_mean"] - rho_primary["rho_B_mean"])
    return {"rho_shift": float(shift),
            "prior_sensitive_flag": bool(shift > PRIOR_SENSITIVITY_RHO_SHIFT)}


def fit_grader_agent(grades, *, seed=CENSUS_SEED, prior="primary",
                     target_accept=TARGET_ACCEPT, tune=TUNE, draws=DRAWS):
    """Grader facet (SS6.2) for one agent: grades = items x re-grades
    of 0/1 grades for the SAME frozen trajectories (the input
    convention of components.estimate_grader_variance).

    logit(p_ijg) = mu_i + v_ij + w_ijg, v ~ N(0, tau_i),
    w ~ N(0, tau_g,i); E3_B(i) = E_j[ Var_g(p_ijg) ] per draw.
    Fitted ONLY where a corpus re-grades frozen trajectories; where
    no re-grades exist the caller records the SS6.2 estimability
    limit instead of calling this.
    """
    pm = _pm()
    g = np.asarray(grades, dtype=int)
    if g.ndim != 2 or g.shape[1] < 2:
        raise ValueError("need >= 2 re-grades per frozen item")
    T, G = g.shape
    item_idx = np.repeat(np.arange(T), G)
    y = g.reshape(-1)
    mu_sd = 2.5 if prior == "primary" else 5.0
    tau_sd = 1.0 if prior == "primary" else 2.0
    if prior not in ("primary", "sensitivity"):
        raise ValueError("prior must be 'primary' or 'sensitivity'")
    with pm.Model() as model:
        mu = pm.Normal("mu", 0.0, mu_sd)
        tau = pm.HalfNormal("tau", tau_sd)
        tau_g = pm.HalfNormal("tau_g", tau_sd)
        v = pm.Normal("v", 0.0, tau, shape=T)
        w = pm.Normal("w", 0.0, tau_g, shape=T * G)
        pm.Bernoulli("y", logit_p=mu + v[item_idx] + w, observed=y)
        idata = _sample(model, seed, target_accept, tune, draws)
    post = idata.posterior
    mu_d = np.asarray(post["mu"].values)
    v_d = np.asarray(post["v"].values)                # (chain, draw, T)
    w_d = np.asarray(post["w"].values).reshape(
        mu_d.shape[0], mu_d.shape[1], T, G)
    p = 1.0 / (1.0 + np.exp(-(mu_d[:, :, None, None]
                              + v_d[:, :, :, None] + w_d)))
    e3 = np.mean(np.var(p, axis=3, ddof=1), axis=2)
    diag = _diagnostics(idata, {"E3_B": e3})
    return {
        "arm": "B", "endpoint": "binary-grader", "prior": prior,
        "n_items": int(T), "n_regrades": int(G),
        "mu": _summarise(mu_d),
        "tau": _summarise(np.asarray(post["tau"].values)),
        "tau_g": _summarise(np.asarray(post["tau_g"].values)),
        "E3_B": _summarise(e3),
        "diagnostics": diag,
    }


def fit_continuous_agent(cell_values, *, score_range, seed=CENSUS_SEED,
                         prior="primary", target_accept=TARGET_ACCEPT,
                         tune=TUNE, draws=DRAWS):
    """Continuous secondary endpoint (SS6.2): same nesting, original
    scale. cell_values = list of per-task run arrays (the input
    convention of components.estimate_components_continuous).

    E1_B(i) = tau_i^2 and E2_B(i) = sigma_i^2, read from the posterior.

    Prior for mu_i: Normal(0, 2.5^2) where the score is in [0, 1],
    Normal(0, 5^2) otherwise — chosen from score_range, the corpus's
    recorded score range at ingest (never from results).
    INTERPRETATION NOTE (recorded at build, Stage 6 return
    2026-10-31): SS6.2 phrases the [0, 1] case as 'on the score
    scale's logit'; the model form and the direct read-off of
    tau_i^2 / sigma_i^2 pin the fit to the ORIGINAL scale (a
    logit-scale fit would not estimate Arm A's estimands, which SS6
    requires both arms to share), so the phrase is implemented as
    the prior-scale choice only. Flagged for Stage 8 / parent
    confirmation; the binary arm — the primary endpoint — is
    unaffected by this reading either way.
    """
    pm = _pm()
    cells = [np.asarray(v, dtype=float) for v in cell_values]
    if any(len(v) < 2 for v in cells):
        raise ValueError("insufficient repeats: every cell needs n_ij >= 2")
    T = len(cells)
    task_idx = np.concatenate([
        np.full(len(v), j) for j, v in enumerate(cells)])
    y = np.concatenate(cells)
    lo, hi = float(score_range[0]), float(score_range[1])
    in_unit = (lo >= 0.0 and hi <= 1.0)
    if prior == "primary":
        mu_sd = 2.5 if in_unit else 5.0
        tau_sd = 1.0
    elif prior == "sensitivity":
        mu_sd, tau_sd = 5.0, 2.0
    else:
        raise ValueError("prior must be 'primary' or 'sensitivity'")
    with pm.Model() as model:
        mu = pm.Normal("mu", 0.0, mu_sd)
        tau = pm.HalfNormal("tau", tau_sd)
        sigma = pm.HalfNormal("sigma", tau_sd)
        v = pm.Normal("v", 0.0, tau, shape=T)
        pm.Normal("y", mu=mu + v[task_idx], sigma=sigma, observed=y)
        idata = _sample(model, seed, target_accept, tune, draws)
    post = idata.posterior
    tau_d = np.asarray(post["tau"].values)
    sigma_d = np.asarray(post["sigma"].values)
    e1 = tau_d ** 2
    e2 = sigma_d ** 2
    diag = _diagnostics(idata, {"E1_B": e1, "E2_B": e2})
    return {
        "arm": "B", "endpoint": "continuous", "prior": prior,
        "n_tasks": int(T), "n_obs": int(len(y)),
        "score_range": (lo, hi), "mu_prior_sd": mu_sd,
        "mu": _summarise(np.asarray(post["mu"].values)),
        "tau": _summarise(tau_d), "sigma": _summarise(sigma_d),
        "E1_B": _summarise(e1), "E2_B": _summarise(e2),
        "diagnostics": diag,
    }
