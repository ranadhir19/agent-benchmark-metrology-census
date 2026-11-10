# SOLUTION DESIGN — Area 1: Metrology of Agent-Benchmark Scores (Stage 5)

**Area:** agent-benchmark-metrology · **Stage:** 5 (Solutioning) · **Date:** 2026-10-30
**Gate state:** Investigation packet approved by Ranadhir Ghosh 2026-10-30, refinement R1 approved (RESEARCH_PACKET.md §5 addendum; STATE.md gate ledger). This document is design only — no code, no results.

---

## 1. The measurement problem, formalised

A published benchmark score for agent *i* is a mean over a finite design:

> Ŝ_i = (1/T) Σ_j (1/R_j) Σ_r Y_ijr

where j indexes tasks drawn from the benchmark's task set (size T), r indexes independent runs of agent i on task j (R_j runs), and Y_ijr is the run outcome — binary (score_binarized) as the primary endpoint, continuous partial credit (score_cont) as secondary. Under the random-effects model Y_ijr = p_ij + ε_ijr with p_ij the agent's per-task success propensity, the law of total variance splits a single run's outcome variance, for fixed agent i, into exactly the components the paper is about:

| Component | Definition (per agent i) | What generates it |
|---|---|---|
| Task sampling σ²_task(i) | Var_j(p_ij) — spread of the agent's propensities across the task population | Which tasks happen to be in the benchmark; the dominant term leaderboards' bootstrap CIs gesture at |
| Run-level σ²_run(i) | E_j[ Var_r(Y | i, j) ] = E_j[ p_ij(1 − p_ij) ] for binary Y | Agent stochasticity (sampling, tool use, self-correction paths) plus, under R1, environment non-determinism |
| Grader σ²_grader(i) | E[ Var(Y | frozen trajectory, re-grading) ] | Stochastic or model-based grading of a fixed artefact |
| Environment σ²_env(i) | E[ Var(Y | frozen agent policy & grading, re-run environment) ] | Live-environment drift, timing, external state |

**R1 fold-in (approved 2026-10-30):** where a corpus cannot separately identify σ²_env (no design re-runs the environment holding the agent's behaviour fixed — true of every public corpus in the packet), σ²_env is counted **within** σ²_run for the falsifier test, and the inseparability is reported as an estimability limit. The same treatment applies to σ²_grader where no re-grading of frozen trajectories exists: it is then either 0 by construction (deterministic programmatic grading, stated as such) or not identified (model-based grading without re-grades — reported as an estimability limit, never silently set to zero).

Design-level contributions to the published score's variance (unpaired task draws, R runs per task):

> Var(Ŝ_i) ≈ σ²_task / T + σ²_run / (T·R)   (+ grader analogue where identified)

Both levels are reported: **component level** (the falsifier's literal terms) and **design level** (what they do to a published number at the benchmark's actual T and R).

## 2. Estimands

Per benchmark B and agent i, on binary outcomes (continuous outcomes: same formulas with empirical within-cell variances replacing p(1−p)):

- **E1 — σ²_task(i):** Var_j(p_ij), the task-population variance of per-task propensities.
- **E2 — σ²_run(i):** E_j[p_ij(1−p_ij)], mean within-cell Bernoulli variance (environment folded in per R1).
- **E3 — σ²_grader(i):** identified only where the corpus re-grades frozen trajectories; otherwise an estimability-limit entry (with the deterministic-grader zero stated where grading is programmatic).
- **E4 — the falsifier statistic:** ρ = (σ²_run + σ²_grader) / σ²_task, pooled across agents (equal agent weights) per benchmark. **The thesis dies on a benchmark set if ρ < 0.10** (pre-registered threshold, §5 of the packet). Pooled per benchmark first; the cross-benchmark verdict requires ≥3 benchmarks (H-DATA gate).
- **E5 — MDE_B(R, T; δ-design):** the smallest two-agent gap detectable at 80% power, two-sided α = 0.05, under benchmark B's components, as a function of runs R and tasks T; and its inverse, **R_required(δ)** for δ ∈ {1, 3, 5} points.
- **E6 — audit verdicts (later stage):** published pairwise gaps vs E5 at the design actually used. (Defined here; executed in full Stage 7, not the pilot.)

## 3. Estimators (method of moments; no model fitting, CPU-trivial)

For cell (i, j) with n_ij ≥ 2 runs and empirical rate p̂_ij:

- Within-cell variance, unbiased for binary Y: s²_ij = (n_ij / (n_ij − 1)) · p̂_ij(1 − p̂_ij).
- **σ̂²_run(i)** = weighted mean of s²_ij over tasks (weights n_ij; equal-weight variant reported as sensitivity).
- **σ̂²_task(i)** = max(0, Var_j(p̂_ij) − mean_j[ p̂_ij(1 − p̂_ij) / n_ij ]) — observed spread of cell means minus its expected sampling inflation (the standard ANOVA moment correction; truncation at 0 reported when it binds).
- **Uncertainty:** cluster bootstrap over tasks (resample tasks with replacement within agent, recompute E1/E2/E4), percentile CIs; B = 2,000 resamples for the pilot, fixed seed. Small-sample caution per Bowyer et al. (packet source 9): CIs are reported as descriptive intervals, and the MDE uses a t-critical sensitivity alongside the normal value (§5).
- **Paired-design components for MDE:** for two agents on the *same* task set, σ²_task,diff = Var_j(p_Aj − p_Bj) estimated analogously from paired cell means (this is the design leaderboards actually use — same tasks, both agents). Unpaired variant (independent task draws) also computed; the paired number is primary.
- **Pooling:** per-agent components averaged with equal weights for the benchmark-level ρ; per-agent table retained (component dominance by agent is SQ4 material).

Why moments, not a fitted GLMM: the estimands are design quantities, the moment estimators are unbiased under the random-effects split without distributional assumptions on p_ij, they are exactly reproducible, and their failure modes (negative σ̂²_task) are visible rather than absorbed by a prior. A GLMM cross-check is a full-Stage-7 refinement, not the pilot's estimator.

## 4. The ≥3 benchmark set and its repeated-run sources

Selection rule (frozen here, applied at Stage 7): a benchmark enters the set iff (a) genuine repeated runs (n_ij ≥ 2 for a substantial share of agent×task cells) are publicly available at run level, (b) outcomes are binary or binarisable without judgement calls, (c) task identities are stable across runs. Candidate pool ≥6 for 3 slots (packet §1.5, R1 mitigation):

| # | Benchmark / corpus | Repeated-run source | Status |
|---|---|---|---|
| B1 | **METR task suite (HCAST + RE-Bench records)** | Local flagship-reused files `flagship_work/data/metr/runs_v1_0.jsonl`, `runs_v1_1.jsonl` (65,637 runs; fields task_id, model, score_binarized, score_cont, run_id) | **On disk now — pilot benchmark** |
| B2 | HAL corpus (`agentevals/hal_traces`, HF) | 21,730 rollouts, 9 benchmarks inside; per-benchmark subsets only (packet cap discipline) | Path verified in flagship audit; subset pull at full Stage 7 |
| B3 | τ-bench (retail/airline) | pass^k design — repeats public by construction | Path verified in packet; pull at full Stage 7 |
| B4 | SWE-Bench-Verified via Bjarnason et al. trajectories | 10 runs × 6 configs | Availability UNVERIFIED (packet) — census decides |
| B5 | de la Rubia coding-agent runs | 584 runs, 52× repeated pairings, GitHub | Census verifies repo/licence |
| B6 | CORE-Bench (inside HAL's span) | Public harness + HAL rollouts | Repeat structure re-verified at census |

**Pilot (bounded deep test): B1 only, end-to-end** — the smallest slice that exercises ingest → components → MDE → falsifier comparison. Slice-selection rule (frozen in the pre-registration, a deterministic function of coverage counts only, never of outcomes): within one METR version file and one task_source, the agent with the most tasks having ≥2 runs. The pilot reports ρ for that slice **against** the 0.10 threshold as an indicative reading; the falsifier's verdict proper requires ≥3 benchmarks and is reserved to full Stage 7. The H-DATA kill is assessed at the census level: B1 verified on disk; B2/B3 paths verified in the packet; if full Stage 7 finds <3 of the pool usable, the kill fires then.

**Anchor check (charter requirement):** before any variance estimate is trusted, recompute a published-style score from raw run-level records two independent ways (unweighted mean of score_binarized over the slice; METR's equal_task_weight-weighted mean) and report both — plus, in the harness, exact recovery of planted components on synthetic data (§6 of the coding stage; validate.py gate).

## 5. Minimum detectable effect at 80% power

For two agents compared on benchmark B with T shared tasks and R runs per task (paired design):

> SE_diff(R) = sqrt( σ²_task,diff / T + (σ²_run,A + σ²_run,B) / (T·R) )
> **MDE(R) = (z_{1−α/2} + z_{1−β}) · SE_diff(R)**, α = 0.05 two-sided, power 1−β = 0.80 ⇒ multiplier 1.960 + 0.842 = 2.802.

- **R_required(δ)** = ceil( (σ²_run,A + σ²_run,B) / ( T·(δ/2.802)² − σ²_task,diff ) ), with the honest edge case stated: if the denominator ≤ 0, **no number of runs suffices** — the task set itself must grow; the design table then reports T_required at the benchmark's actual R. This edge case is a headline-worthy result, not an error.
- Unpaired variant replaces σ²_task,diff with σ²_task,A + σ²_task,B.
- Sensitivity: t-critical values with df = T − 1 in place of z (Bowyer et al. caution for small T), reported alongside; conclusions drawn on the normal values, flagged where the t variant changes a verdict.
- Design table per benchmark (full Stage 7): MDE at R ∈ {1, 2, 4, 8, actual}, R_required for δ ∈ {0.01, 0.03, 0.05}, each next to the runs the benchmark's published reporting actually used (SQ1).

## 6. Analysis pipeline shape

```
ingest (per-source adapter -> canonical run table: benchmark, agent, task, run, y_bin, y_cont, grader_kind, env_fields?)
  -> harmonise (cell table: agent x task -> n_runs, successes; coverage report: cells with n>=2 share)
  -> components (per agent: sigma2_task, sigma2_run, [sigma2_grader | estimability-limit]; pooled rho + cluster-bootstrap CIs)
  -> mde (paired/unpaired SE, MDE(R) curve, R_required / T_required tables)
  -> falsifier comparison (rho vs 0.10, per benchmark; H-DATA census status)
  -> report artefacts (JSON + markdown tables; every number traceable to a run-table file hash)
```

Adapters isolate source quirks (METR JSONL now; HAL/τ-bench later) behind the canonical schema — the "real data schemas" requirement is met by building the METR adapter against the actual flagship files, fields as inspected 2026-10-30. All steps deterministic given a seed; all runs CPU-light and `nice`-compatible; per-benchmark subsets only (no big downloads).

## 7. Alternatives considered (charter requires ≥3 genuinely different approaches)

1. **Method-of-moments ANOVA decomposition (CHOSEN for the pilot).** Assumption-light, exactly reproducible, failure modes visible; the field's own ancestors (Bouthillier et al.) use this family. Weakness: no shrinkage for sparse cells; handled by the n_ij ≥ 2 restriction + bootstrap.
2. **Bayesian hierarchical / GLMM partial pooling.** Better small-cell behaviour and posterior intervals; costs: prior sensitivity on exactly the quantity under dispute, heavier compute, reproducibility burden. Reserved as a full-Stage-7 robustness cross-check, not the primary estimator.
3. **Design-based resampling only (bootstrap the published score under re-drawn tasks/runs).** Directly targets Var(Ŝ) at the design actually used; but it cannot attribute variance to named components — and attribution is the paper's estimand (E4 is a ratio of components). Used inside the chosen approach for CIs, not as the approach.

## 8. What this design deliberately does not do

No new agent runs (no API spend; confirmatory runs are a separate decision per the packet). No validity/shortcut analysis (sources 17–18's object, not this one). No re-reporting of the flagship's time-horizon identifiability results (overlap discipline). Grader/environment components are estimated only where a corpus identifies them; elsewhere they are reported as estimability limits under R1 — never imputed.
