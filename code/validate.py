#!/usr/bin/env python3
"""Stage 6 harness for Area 1 (agent-benchmark-metrology).

Honest scope statement: this harness validates the PIPELINE, not any
empirical claim. Stage B tests are SYNTHETIC anchor tests: data generated
with known planted variance components must be recovered by the estimators
within stated tolerances. Stage C tests are negative/edge tests: the
machinery must detect the falsifier's kill condition, refuse single-run
cells, and reproduce closed-form MDE values exactly. No real benchmark
data is touched here; the real-data anchor (recomputed published-style
scores from raw METR records) runs in code/pilot.py and is reported in
EXPERIMENTS.md.

Stage D (added 2026-10-31, Stage 6 return for the frozen Stage 7
addendum SS6.3): Arm B (GLMM / Bayesian partial pooling, code/glmm.py)
planted-component recovery on synthetic data generated from the Arm B
model itself (code/synth.generate_agent_logitnormal). TOLERANCES,
STATED BEFORE ANY ARM B FIT WAS RUN UNDER THIS HARNESS (SS6.3):
per configuration, the posterior-mean relative error must be
<= 0.35 for E1_B (sigma2_task) and <= 0.20 for E2_B (sigma2_run) —
the task tolerance mirrors Arm A's Stage B anchor (0.35); the run
tolerance is set looser than Arm A's 0.15 because the Arm B estimand
integrates over posterior draws of latent propensities rather than
plugging in cell rates. The pooled-rho recovery tolerance is 0.35.
Each Arm B check ALSO requires the SS6.4 diagnostic gates on the
primary fit: R-hat <= 1.01, bulk/tail ESS >= 400, zero divergences,
and no model-misfit flag (PPC p within [0.01, 0.99]). Sampler
settings are the frozen ones (addendum SS6.2): 4 chains, 2,000 +
2,000, target_accept 0.95, max_treedepth 12, census-seed chains.

Interpreter: run with the area venv (venv/bin/python) — Arm B needs
the PyMC stack pinned in code/requirements-lock.txt (addendum SS6.3);
Arm A checks run identically there (numpy/scipy pinned to the same
versions as the original Stage 6 environment).

Exit code 0 iff every check passes.
"""
import math
import os
import py_compile
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def stage_a_compile_import():
    code_dir = os.path.join(HERE, "code")
    files = [os.path.join(code_dir, f) for f in sorted(os.listdir(code_dir))
             if f.endswith(".py")]
    ok = True
    for f in files:
        try:
            py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError as e:
            ok = False
            print("compile error:", f, e)
    check("A1 compile all code modules", ok, f"{len(files)} files")
    try:
        from code import components, glmm, ingest, mde, synth  # noqa: F401
        check("A2 import all code modules", True)
    except Exception as e:  # noqa: BLE001
        check("A2 import all code modules", False, repr(e))


def _rel(est, truth):
    return abs(est - truth) / truth if truth else abs(est - truth)


def stage_b_anchor_recovery():
    import numpy as np
    from code import components, synth

    configs = [
        # (a, b, T, R) — Beta task-propensity families
        (2.0, 5.0, 300, 10),
        (5.0, 2.0, 300, 10),
        (1.0, 1.0, 300, 6),
        (8.0, 3.0, 250, 8),
    ]
    tol_task, tol_run = 0.35, 0.15
    for (a, b, T, R) in configs:
        truth = synth.beta_component_truth(a, b)
        passes_t = passes_r = 0
        errs_t, errs_r = [], []
        for seed in (11, 22, 33, 44, 55):
            n, k, _p = synth.generate_agent(a, b, T, R, seed=seed)
            est = components.estimate_components(n, k)
            et, er = _rel(est["sigma2_task"], truth["sigma2_task"]), \
                _rel(est["sigma2_run"], truth["sigma2_run"])
            errs_t.append(et); errs_r.append(er)
            passes_t += et <= tol_task
            passes_r += er <= tol_run
        ok = passes_t >= 4 and passes_r >= 4
        check(f"B anchor recovery Beta({a:g},{b:g}) T={T} R={R}", ok,
              f"planted task={truth['sigma2_task']:.4f} run={truth['sigma2_run']:.4f}; "
              f"median rel err task={np.median(errs_t):.3f} run={np.median(errs_r):.3f}; "
              f"seeds within tol: task {passes_t}/5 run {passes_r}/5")

    # Grader anchor: frozen items, flip prob q -> planted variance q(1-q)
    q, T, G = 0.10, 2000, 6
    grades = synth.generate_frozen_grades(T, q, G, seed=7)
    est_g = components.estimate_grader_variance(grades)
    check("B grader recovery q=0.10", _rel(est_g, q * (1 - q)) <= 0.15,
          f"planted={q * (1 - q):.4f} est={est_g:.4f}")


def stage_c_negative_and_closed_form():
    import numpy as np
    from code import components, mde

    # C1: deterministic agent (each task always passes or always fails)
    #     -> run variance exactly 0, rho = 0: falsifier kill condition visible.
    T, R = 200, 6
    k = np.array([R if j % 3 else 0 for j in range(T)])
    n = np.full(T, R)
    est = components.estimate_components(n, k)
    check("C1 deterministic agent -> sigma2_run = 0, rho = 0",
          est["sigma2_run"] == 0.0 and est["rho"] == 0.0,
          f"sigma2_task={est['sigma2_task']:.4f} sigma2_run={est['sigma2_run']}")

    # C2: homogeneous tasks (all p equal) -> task component ~ 0.
    rng = np.random.default_rng(3)
    k2 = rng.binomial(10, 0.3, size=400)
    est2 = components.estimate_components(np.full(400, 10), k2)
    check("C2 homogeneous tasks -> sigma2_task ~ 0",
          est2["sigma2_task"] < 0.004,
          f"sigma2_task={est2['sigma2_task']:.5f} (raw {est2['sigma2_task_raw']:.5f})")

    # C3: single-run cells must be refused, not silently estimated.
    try:
        components.estimate_components(np.ones(5, dtype=int),
                                       np.array([1, 0, 1, 0, 1]))
        check("C3 single-run cells refused", False, "no error raised")
    except ValueError:
        check("C3 single-run cells refused", True, "ValueError raised")

    # C4: closed-form MDE. T=100, run_var_sum=0.32, task_term=0.
    got = mde.mde(100, 1, 0.32, 0.0)
    want = mde.Z_MULT * math.sqrt(0.32 / 100.0)
    check("C4 MDE closed form", abs(got - want) < 1e-12,
          f"mde={got:.6f} want={want:.6f}")

    # C5: MDE strictly decreasing in R; required_runs consistent with MDE.
    vals = [mde.mde(100, R, 0.32, 0.01) for R in (1, 2, 4, 8)]
    mono = all(x > y for x, y in zip(vals, vals[1:]))
    rr = mde.required_runs(0.05, 100, 0.32, 0.01)
    consistent = rr is not None and mde.mde(100, rr, 0.32, 0.01) <= 0.05 \
        and (rr == 1 or mde.mde(100, rr - 1, 0.32, 0.01) > 0.05)
    check("C5 MDE monotone in R + required_runs consistent",
          mono and consistent, f"required_runs(0.05)={rr}")

    # C6: task-term-dominated design -> no R suffices; tasks must grow.
    rr2 = mde.required_runs(0.01, 50, 0.30, 0.25)
    tt2 = mde.required_tasks(0.01, 4, 0.30, 0.25)
    check("C6 runs-infeasible edge -> None + finite required_tasks",
          rr2 is None and isinstance(tt2, int) and tt2 > 50,
          f"required_runs={rr2} required_tasks={tt2}")

    # C7: identical re-grades -> grader variance exactly 0.
    # Each item's grade is constant across its 5 re-grades (rows constant).
    g = np.repeat(np.array([0, 1, 1, 0, 1])[:, None], 5, axis=1)
    check("C7 deterministic grading -> grader variance 0",
          components.estimate_grader_variance(g) == 0.0)


def stage_d_arm_b_recovery():
    import numpy as np
    from code import glmm, synth

    # Tolerances stated in this file's docstring BEFORE any fit ran.
    tol_e1, tol_e2, tol_rho = 0.35, 0.20, 0.35
    configs = [
        # (mu, tau, T, R, generation seed) — planted from the Arm B model
        (0.0, 1.0, 250, 10, 101),
        (-1.0, 0.6, 250, 10, 202),
    ]
    fits, truths = [], []
    for (mu, tau, T, R, seed) in configs:
        n, k, _p, truth = synth.generate_agent_logitnormal(mu, tau, T, R,
                                                           seed=seed)
        fit = glmm.fit_binary_agent(n, k)
        fits.append(fit)
        truths.append(truth)
        e1 = _rel(fit["E1_B"]["mean"], truth["sigma2_task"])
        e2 = _rel(fit["E2_B"]["mean"], truth["sigma2_run"])
        dg = fit["diagnostics"]
        ok = (e1 <= tol_e1 and e2 <= tol_e2 and dg["diagnostic_pass"]
              and not fit["model_misfit_flag"])
        check(f"D Arm B recovery mu={mu:g} tau={tau:g} T={T} R={R}", ok,
              f"planted task={truth['sigma2_task']:.4f} run={truth['sigma2_run']:.4f}; "
              f"rel err E1={e1:.3f} (tol {tol_e1}) E2={e2:.3f} (tol {tol_e2}); "
              f"rhat_max={dg['rhat_max']:.3f} ess_min={min(dg['ess_bulk_min'], dg['ess_tail_min']):.0f} "
              f"div={dg['divergences']} ppc_p={fit['ppc_p']:.3f}")

    # Pooled rho (E4_B) across the two synthetic agents vs planted pooled
    # rho (Arm A construction: ratio of equal-weight mean components).
    pooled = glmm.pooled_rho_binary(fits)
    planted_rho = float(np.mean([t["sigma2_run"] for t in truths])
                        / np.mean([t["sigma2_task"] for t in truths]))
    er = _rel(pooled["rho_B_mean"], planted_rho)
    check("D Arm B pooled rho recovery", er <= tol_rho,
          f"planted pooled rho={planted_rho:.4f} est={pooled['rho_B_mean']:.4f} "
          f"rel err={er:.3f} (tol {tol_rho})")

    # Negative: Arm B primary fits refuse single-run cells (SS6.2 rule),
    # exactly as Arm A does (C3); the labelled sensitivity path admits them.
    try:
        glmm.fit_binary_agent(np.ones(5, dtype=int), np.array([1, 0, 1, 0, 1]))
        check("D Arm B single-run cells refused", False, "no error raised")
    except ValueError:
        check("D Arm B single-run cells refused", True, "ValueError raised")


def main():
    stage_a_compile_import()
    stage_b_anchor_recovery()
    stage_c_negative_and_closed_form()
    stage_d_arm_b_recovery()
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    print("OVERALL:", "PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
