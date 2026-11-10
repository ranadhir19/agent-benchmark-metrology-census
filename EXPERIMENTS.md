# EXPERIMENTS — Area 1: Metrology of Agent-Benchmark Scores (Stage 7)

**Area:** agent-benchmark-metrology · **Stage:** 7 (Experimentation)
**Status:** BOUNDED DEEP TEST ONLY. This document freezes the pre-registration
before any pilot result, records the pilot result, and STOPS. Full Stage 7
(≥3 benchmarks, leaderboard-gap audit) is NOT authorised by this pass.

---

## 1. PRE-REGISTRATION — FROZEN 2026-10-30 (before any pilot result)

**Gate note:** the investigation packet was approved by Ranadhir Ghosh on
2026-10-30, including refinement R1. `validate.py` is green (14/14, exit 0)
on the full code tree. The coverage profile used below (file line counts and
cells-with-≥2-runs counts) contains no outcome statistics; no component
estimate, MDE, or score has been seen at freeze time.

### 1.1 Falsifier (verbatim from the shortlist, via RESEARCH_PACKET.md §5)

> The thesis dies if, on ≥3 benchmarks with genuine repeated runs, run-level
> + grader variance is <10% of task-sampling variance — i.e., single-run
> scores are already as reliable as the field's usage assumes. H-DATA kill:
> if fewer than 3 public benchmarks expose enough repeated runs to estimate
> the components, the area stops at the gate rather than shrinking to one
> benchmark.

### 1.2 Refinement R1 — APPROVED 2026-10-30 (applies to this test)

Where a benchmark's public data cannot separately identify the environment
component from the run-level component, the environment component is counted
within the run-level component for the falsifier test, and the inseparability
is reported as an estimability limit. Threshold (0.10), benchmark count (≥3),
and H-DATA gate are unchanged.

### 1.3 Pilot hypotheses (bounded deep test; one benchmark, B1 = METR)

- **PH1 (falsifier reading, single benchmark):** on the pilot benchmark,
  ρ = (σ²_run + σ²_grader) / σ²_task ≥ 0.10. METR grading is programmatic
  (deterministic), so σ²_grader = 0 by construction and ρ = σ²_run / σ²_task.
- **PH2 (design numbers, SQ1):** the paired MDE at the benchmark's actual
  design (shared tasks, R as recorded) is computed for δ ∈ {0.01, 0.03, 0.05};
  required runs for δ = 0.03 are reported.
- **PH3 (anchor):** the pilot agent's score on its ≥2-run task set recomputed
  three ways over the same records (pooled run mean; equal-task mean;
  METR equal_task_weight-weighted mean) is reported, and the record-count
  cross-check (Σ cell n == filtered records) must hold.

### 1.4 Data subset (frozen)

- File: `flagship_work/data/metr/runs_v1_0.jsonl` (41,629 records; local
  flagship-reused copy — no download, no new data).
- Source rule (deterministic, outcome-free): task_source = the source with
  the most records in that file. Coverage profile (counts only, 2026-10-30):
  HCAST 22,690 / SWAA 17,263 / RE-Bench 1,676 — so the rule selects HCAST
  unless the pilot script's own count differs, in which case the script's
  selection governs and is reported.
- Pilot-agent rule (deterministic, outcome-free): within the chosen source,
  the model with the most tasks having ≥2 runs (ties: most runs in those
  cells, then name order). Only cells with n ≥ 2 enter the estimators;
  single-run cells are excluded, never imputed.
- Paired agent: the other model sharing the most ≥2-run tasks with the
  pilot agent (ties: name order). Paired design table uses the shared
  task set only.
- Endpoints: binary score_binarized primary; score_cont secondary.
  Frozen trajectories are absent, so no grader re-grade estimation is
  attempted on METR (see §1.2 + grader note in the result).

### 1.5 Estimators and uncertainty (frozen)

- Method-of-moments estimators exactly as in `code/components.py` and
  SOLUTION_DESIGN.md §3 (σ²_run = n-weighted mean of unbiased within-cell
  variances; σ²_task = Var(cell means) − mean sampling inflation, truncated
  at 0 with the truncation reported).
- Cluster bootstrap over tasks, B = 2,000, seed 20261030; percentile CIs.
- MDE: normal multiplier 2.8016 (α = 0.05 two-sided, power 0.80); t
  sensitivity with df = T − 1 reported alongside (SOLUTION_DESIGN.md §5).

### 1.6 Decision rules (frozen)

- **ρ ≥ 0.10 on the pilot benchmark:** thesis survives the pilot; the
  recommendation is to proceed to the full Stage 7 census (≥3 benchmarks).
  This is NOT the falsifier verdict — the falsifier requires ≥3 benchmarks.
- **ρ < 0.10 on the pilot benchmark:** kill-direction reading on this
  benchmark, reported as such; the thesis kill still requires the same
  result across ≥3 benchmarks, so full Stage 7 decides — but a pilot
  kill-direction result must be reported prominently and must not be
  diluted by adding favourable benchmarks later.
- **H-DATA:** this pilot verifies B1 (METR) only. B2 (HAL), B3 (τ-bench),
  B4/B5 (census-dependent) are NOT verified by this pass; the H-DATA kill
  is assessed at the full Stage 7 census, not here.
- **Anchor failure:** if the record-count cross-check fails, the pilot is
  VOID and routes back to Stage 6 (coding) for an ingest fix — results are
  not reported as findings.
- **STOP rule:** after the pilot report in §2 below, this pass STOPS. No
  further benchmark is pulled, no audit table is built, no manuscript
  work begins.

---

## 2. PILOT RESULT (appended after the run; pre-registration above untouched)

**Run:** 2026-10-30, `nice -n 10 python3 code/pilot.py` on the frozen slice.
Artefact: `results/pilot_metr_v1_0.json` (includes the input file's SHA-256,
full coverage table, and all numbers below).

### 2.1 Slice as selected by the frozen rules

- Source: **HCAST** (22,690 of 41,629 records in runs_v1_0.jsonl).
- Pilot agent: **grok_4** — 97 tasks with ≥2 runs, 847 runs in those cells
  (mean 8.73 runs/task). Paired agent: **claude_3_5_sonnet**, sharing all
  97 tasks.

### 2.2 Anchor (PH3) — PASSED

Record-count cross-check: **holds** (Σ cell n == filtered records), so the
pilot is not void. Pilot agent's score on its ≥2-run task set, three ways
over the same records: pooled run mean **0.5880**; equal-task mean
**0.6233**; METR equal_task_weight-weighted mean **0.6141**. (The three
differ because they weight tasks/runs differently — exactly the design
sensitivity this area studies; all are computed from the raw records, not
copied from any published table.)

### 2.3 Variance components (PH1) — thesis SURVIVES this benchmark

Binary endpoint, grok_4 on HCAST (97 tasks):

| Component | Estimate | Bootstrap 95% CI (B=2,000) |
|---|---|---|
| σ²_task | 0.1970 | [0.1646, 0.2176] |
| σ²_run (env folded in, R1) | 0.0482 | [0.0283, 0.0703] |
| σ²_grader | 0 by construction (programmatic grading) | — |
| **ρ = (σ²_run + σ²_grader)/σ²_task** | **0.2449** | **[0.1344, 0.3966]** |

**ρ = 0.245 ≥ 0.10, and the entire bootstrap CI lies above the 0.10
threshold.** Run-level variance is about a quarter of task-sampling
variance on this benchmark — the falsifier's kill condition does not fire
here. Continuous endpoint (score_cont) agrees in direction: σ²_task =
0.1608, σ²_run = 0.0501, ρ ≈ 0.31.

Per §1.6 this is a single-benchmark reading, NOT the falsifier verdict:
the thesis kill requires ρ < 0.10 on ≥3 benchmarks. The pilot's
contribution is that B1 clears the bar with margin, so the kill is not
the foregone conclusion a friendly reading might have assumed — and the
machinery (validated Stage 6) detects the kill condition when it is
present (harness checks C1/C2).

### 2.4 Design numbers (PH2) — the task set, not the run count, binds

Paired design, grok_4 vs claude_3_5_sonnet, T = 97 shared tasks,
σ²_task,diff = 0.1112, σ²_run sum (shared-task estimates) as in the
artefact:

| Runs R | MDE (normal) | MDE (t sensitivity) |
|---|---|---|
| 1 | 0.1414 | 0.1429 |
| 2 | 0.1204 | 0.1216 |
| 4 | 0.1084 | 0.1095 |
| 8 | 0.1018 | 0.1029 |

**Required runs: for δ = 0.01, 0.03, and 0.05 the answer is NONE — no
number of runs per task resolves even a 5-point gap on 97 tasks**, because
the paired task term alone exceeds the δ budget. At R = 8, resolving
δ = 0.03 would require **1,118 tasks** (δ = 0.05: 403; δ = 0.01: 10,061)
against HCAST's 97-task slice. On this benchmark, a claimed 3-point gap
between two agents is measurement noise at any feasible run count; only a
larger task set can change that. (Single-benchmark, single-pair reading;
full Stage 7 generalises across benchmarks and pairs.)

### 2.5 Kill-criteria status and STOP

- Thesis kill (ρ < 0.10 on ≥3 benchmarks): **not fired** — pilot
  benchmark reads 0.245, CI wholly above 0.10; benchmarks 2–3 not yet run.
- H-DATA kill (<3 benchmarks with usable repeated runs): **not fired and
  not yet assessable** — B1 (METR) is verified end-to-end locally by this
  pilot; B2 (HAL) and B3 (τ-bench) paths were verified in the packet but
  their repeat censuses belong to full Stage 7.
- **STOP (per §1.6 and the orchestrator's directive): this pass ends
  here.** No further benchmark was pulled, no audit table built, no
  manuscript work begun. Next step, on the parent/Ranadhir's direction:
  full Stage 7 census + estimation across ≥3 benchmarks under a fresh
  frozen pre-registration for that scale.


---

## 3. ADDENDUM 2026-10-31 — P2-A1 anchor replication (Decision 1 (ii), adopted 2026-10-31)

**Decision record.** Ranadhir Ghosh's 2026-10-31 directive ("continue with all
pending tasks unless cost or compromise with quality is at stake") adopts
Decision 1 = option (ii) of
`~/workspace/your_files/Research_Pilots_Decision_Packet_2026-10-31.md`: run the
P2-A1 replication FIRST, then promote the GLMM/Bayesian partial-pooling arm to
co-primary in the full Stage 7 pre-registration. The frozen pilot
pre-registration (§1) and pilot result (§2) above are untouched by this
addendum.

**P2-A1 outcome — KILL, criterion K1 (data-availability).** The target repo
(`github.com/Yongxi-Zhou/leetcode-evaluator-data-output`, HEAD
`e96821c1da5721273e0fb423ddd8207b0c36e9bf`) was cloned and every ref examined
(4 branches, 3 PR heads, releases: none). It contains **no binary outcome
tensor at any ref**: trial records live under `output/`, which `.gitignore`
excludes and which was never committed; the only outcome-shaped file is a
379-byte test fixture (1 problem, 4 toy trials). Ingest verification against
the stated design (16 models × 99 problems × 2 prompts × 5 runs = 15,840
binary outcomes) is therefore impossible. K3 did NOT fire (README licence:
"Research and educational use only" — research reuse permitted; no LICENSE
file, no prohibiting terms). K2 not applicable (no pipeline run was possible;
zero estimator runs). Additional discrepancies: the repo's own artefacts
state 100 problems / 16,000 instances (dataset and `publication/main.tex`),
not 99 / 15,840; and the in-repo paper version contains no variance-ceiling
analysis — the ceiling headlines belong to the later arXiv revision whose
data is not in the repo.

**Artefacts:** `results/p2_a1_replication.json`, `results/P2_A1_REPORT.md`.
**Consequences:** Zhou et al.'s C1 numbers are unverified-by-us in all later
writing; NO full Stage 7 pre-registration addendum was frozen and no census
was started (stop rule on KILL); the GLMM co-primary promotion remains
adopted but unexecuted pending a parent/Ranadhir ruling (dossier §5 fallback
— Bjarnason et al. spread — is gated on census verification of that release).
This finding is recorded for the Stage 7 census / H-DATA ledger: verify
tensor presence at ingest, not repo existence. Harness: no code changed;
`validate.py` re-run 2026-10-31, 14/14 PASS, exit 0.

---

## 4. ADDENDUM 2026-10-31 — P2-A1 FALLBACK (Bjarnason et al. 2026) executed: PASS, anchor ESTABLISHED via fallback

**Scope.** This addendum appends the execution of the dossier §5 fallback
that §3 above left gated on census verification. It was executed as its
own scoped task with the verification performed in-task; **the Stage 7
census was not started**, the frozen pilot pre-registration (§1) and
pilot result (§2) are untouched, and no full Stage 7 pre-registration
addendum was frozen.

**Verification — PASSED.** Bjarnason, Silva & Monperrus (2026), "On
Randomness in Agentic Evals" (arXiv:2602.07150; packet source 4, public
availability marked UNVERIFIED in the packet). The v3 HTML's Data badge
links the Hugging Face dataset `ASSERT-KTH/agentic-evals-artifacts`
(revision `5db0c4b69382d160a313d7ceaded915398c63e13`, last modified
2026-03-20): public, not gated, licence **CC-BY-4.0**. Contents checked
at the artefact (recursive tree + every outcome file parsed): 364
files, 47.9 GB; 12 configurations (3 models × default/temp-0 ×
2 scaffolds) × 10 runs × 500 tasks = 60,000 instance outcomes, with
exactly one SWE-bench harness result JSON per run (resolved IDs per
run; `total_instances = 500` in all 120). One file has 9 incomplete
instances (submitted 491); that run is interior to its configuration's
range and affects no endpoint.

**Reproduction — PASS, two independent runs, byte-identical.**
Pipeline `code/bjarnason_fallback.py` (ingest adapter only; plain
pass@1 aggregation r_j = resolved/total per run; only the 120 eval
JSONs, 5.85 MB, downloaded). Artefacts:
`results/p2_a1_fallback_run1.json`, `results/p2_a1_fallback_run2.json`
(SHA-256 `20bdf1c7…22c` each), report
`results/P2_A1_FALLBACK_REPORT.md`. Measured vs frozen targets:
spread endpoints **2.2 and 6.0 points** (targets 2.2 / 6.0, tolerance
±1.0; deviation 0.0 / 0.0); all 12 per-configuration spreads, minimums
and maximums reproduce exactly; means within 0.04 points; published
SDs identified as sample SDs (ddof=1, max deviation 0.046);
temperature-0 SD maximum **1.76 points**, 3 of 6 temp-0 configurations
> 1.5 — the SD claim reproduces.

**Consequences.** The P2-A1 Gate-8 anchor is **ESTABLISHED via the
fallback**; Zhou et al.'s C1 numbers remain unverified-by-us (the §3
K1 kill stands). The GLMM/Bayesian co-primary promotion remains
adopted but unexecuted, and no census was started — sequencing from
an established-via-fallback anchor returns to the parent/Ranadhir.
Harness: `validate.py` re-run 2026-10-31 with the new adapter,
14/14 PASS, exit 0.
