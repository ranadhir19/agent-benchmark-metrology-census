# EXPERIMENTS ADDENDUM — FULL STAGE 7 PRE-REGISTRATION (FROZEN)

**Area:** agent-benchmark-metrology · **Stage:** 7 (Experimentation), full census
scale · **Companion to:** `EXPERIMENTS.md` (bounded-deep-test pre-registration,
frozen 2026-10-30, and its execution addenda §§3–4)
**Freeze date:** 2026-10-31. **Freeze instant:** the UTC timestamp recorded
alongside this file's SHA-256 in `PREREGISTRATION.sha256` governs — see §12.
**Status at freeze:** NO census data has been touched for this registration:
no census corpus has been downloaded, ingested, or computed on. The census
is NOT started, and this freeze does not authorise starting it (§2.3).

---

## 0. Why this is a separate file (hash-chain choice)

This area's existing practice in `EXPERIMENTS.md` is append-only: the frozen
pilot pre-registration (§1) and pilot result (§2) were never edited, and the
two P2-A1 execution records were appended as §§3–4. This addendum is,
however, a *freeze*, not an execution record, and a freeze needs an object
whose hash cannot change when later execution records are appended elsewhere.
It is therefore frozen as this standalone file, `EXPERIMENTS.md` is left
**byte-untouched** by this task, and a hash record is created for this area
for the first time: `PREREGISTRATION.sha256`, which records (a) the SHA-256
of `EXPERIMENTS.md` as it stood before this addendum (unchanged by it),
(b) the SHA-256 of `SOLUTION_DESIGN.md` (the design this registration
carries, unchanged), and (c) this file's SHA-256 at freeze. Later entries
may be appended to that record; prior entries are never overwritten or
removed. This matches the hash-chain practice used elsewhere in the
programme (a `PREREGISTRATION.sha256` chain beside the frozen text) while
preserving this area's append-only rule for its existing frozen text.

---

## 1. Adoption and anchor preamble

### 1.1 Decision 1 = option (ii), adopted 2026-10-31

Ranadhir Ghosh's 2026-10-31 directive ("continue with all pending tasks
unless cost or compromise with quality is at stake") adopts Decision 1 =
option (ii) of
`~/workspace/your_files/Research_Pilots_Decision_Packet_2026-10-31.md`:
run the P2-A1 replication FIRST, then promote the GLMM/Bayesian
partial-pooling arm to co-primary in the full Stage 7 pre-registration.
Recorded in `STATE.md` (gate ledger, "Decision 1 adoption"). This addendum
executes the second half of that decision; the first half executed as
follows.

### 1.2 Primary anchor target — KILLED under K1

P2-A1's primary target (Zhou et al. 2026, dossier §5) was executed
2026-10-31 and **killed under kill criterion K1**: the public repo
(`github.com/Yongxi-Zhou/leetcode-evaluator-data-output`, HEAD `e96821c`,
all branches / PR heads / releases checked) contains **no binary outcome
tensor at any ref** — the trial records live in a gitignored, never-committed
`output/` tree — so ingest verification against the stated design
(16 × 99 × 2 × 5 = 15,840 outcomes) was impossible. K3 did not fire;
K2 was not applicable. Full record: `results/P2_A1_REPORT.md`,
`results/p2_a1_replication.json`; summary appended as `EXPERIMENTS.md` §3.

**Standing rule (binding on all later writing for this area):** Zhou et
al.'s C1 numbers are **unverified-by-us**. No Stage 9 report, manuscript,
abstract, or summary from this area may cite C1's ceiling numbers (median
1.34; range [1.05, 1.71]; 12 of 15 unresolved pairs; 23% / 14% narrowing)
as verified, reproduced, or confirmed by us. They may be cited only as
their authors' published claims, attributed as such, with the
data-availability finding available alongside.

### 1.3 Anchor — ESTABLISHED via the dossier §5 fallback

The pre-specified fallback (Bjarnason et al. 2026) was then executed as its
own scoped task, 2026-10-31, and **PASSED**:

- Paper: Bjarnason, Silva & Monperrus, "On Randomness in Agentic Evals",
  arXiv:2602.07150 (v3, 2026-03-25).
- Release verified at the artefact: Hugging Face dataset
  `ASSERT-KTH/agentic-evals-artifacts`, revision
  `5db0c4b69382d160a313d7ceaded915398c63e13` — public, not gated, licence
  **CC-BY-4.0**; 364 files / 47.9 GB; 12 configurations × 10 runs ×
  500 tasks = 60,000 instance outcomes, exactly one SWE-bench harness
  result JSON per run (120 files).
- Reproduction (pipeline `code/bjarnason_fallback.py`, plain pass@1
  aggregation): single-run pass@1 spread endpoints measured **2.2 and
  6.0 points** against frozen targets 2.2 / 6.0 ± 1.0 — **deviation
  0.0 / 0.0**; all 12 per-configuration spreads, minimums and maximums
  exact; temperature-0 SD maximum 1.76 points (3 of 6 temp-0
  configurations > 1.5), so the SD claim reproduces. **Two independent
  runs, byte-identical** (artefact SHA-256
  `20bdf1c7f9a3190b7654f817419ef4ff11daf047174497bc50482dcca9ef122c`).
- Artefacts: `results/P2_A1_FALLBACK_REPORT.md`,
  `results/p2_a1_fallback_run1.json`, `results/p2_a1_fallback_run2.json`;
  also recorded in `results/P2_A1_REPORT.md` §8 and `EXPERIMENTS.md` §4.

**The Gate 8 anchor check for full Stage 7 is therefore SATISFIED, via
the fallback.** Harness state at freeze: `validate.py` 14/14 PASS,
exit 0 (re-run 2026-10-31 on the tree including the fallback adapter).

### 1.4 What the anchor does and does not establish

The fallback anchor establishes that this area's own pipeline reproduces
a published, public, licensed repeated-run measurement exactly, on the
field's data. It establishes nothing about Zhou et al.'s numbers (§1.2),
nothing about any census benchmark, and no census result of any kind.
No magnitude from either anchor target is imported into this
registration's hypotheses (INTAKE_MEMO lesson L17): Zhou's ceiling and
Bjarnason's spread are positioning references, never expectations.

---

## 2. Scope of this registration

### 2.1 What is registered

The full Stage 7 census of `SOLUTION_DESIGN.md`: variance-component
estimation (estimands E1–E6) over a ≥3-benchmark set selected by the
frozen rule in §3.2, with the method-of-moments arm and the
GLMM/Bayesian partial-pooling arm as **co-primary** (§6), per-benchmark
MDE / required-runs / required-tasks tables (§3.4), the published-gap
audit (§3.5), and the area falsifier test (§4) read across all three
(or more) benchmarks.

### 2.2 What is NOT registered

- No new agent runs, no API calls, no re-grading with judge models
  (the grader-identification decision is unmade and out of scope —
  §11.2).
- No validity / shortcut analysis; no re-reporting of the flagship
  paper's time-horizon results (overlap discipline, design §8).
- No manuscript work. Stage 9 reporting and Stage 10 paper creation
  follow their own gates after Stage 8.

### 2.3 Authorisation boundary

This document freezes the design **before** any census result exists.
Freezing is not execution. **Census execution is the next step and
requires its own go** (parent / Ranadhir sequencing decision); it is
not authorised by the adoption recorded in §1.1, by the anchor PASS
in §1.3, or by this freeze.

---

## 3. Census design — carried from SOLUTION_DESIGN.md unchanged

`SOLUTION_DESIGN.md` (2026-10-30, Gate-5 deliverable, hash recorded in
`PREREGISTRATION.sha256`) is carried into this registration **without
change**: no estimand, threshold, selection rule, or formula below is
altered, re-weighted, or re-worded in substance. Where this addendum
adds specification the design left open (the model-based arm, §6;
ingest verification, §5), it says so explicitly.

### 3.1 Estimands E1–E6 (design §2, unchanged)

Per benchmark B and agent i, binary outcomes primary (continuous
`score_cont` secondary, same formulas with empirical within-cell
variances replacing p(1−p)):

- **E1 — σ²_task(i):** Var_j(p_ij), the task-population variance of
  per-task propensities.
- **E2 — σ²_run(i):** E_j[p_ij(1−p_ij)], mean within-cell Bernoulli
  variance (environment folded in per R1).
- **E3 — σ²_grader(i):** identified only where the corpus re-grades
  frozen trajectories; otherwise an estimability-limit entry (with the
  deterministic-grader zero stated where grading is programmatic).
  Never imputed, never silently set to zero.
- **E4 — the falsifier statistic:** ρ = (σ²_run + σ²_grader) / σ²_task,
  pooled across agents (equal agent weights) per benchmark. The thesis
  dies on a benchmark set if ρ < 0.10 (§4). Pooled per benchmark first;
  the cross-benchmark verdict requires ≥3 benchmarks (H-DATA gate).
- **E5 — MDE_B(R, T; δ-design):** the smallest two-agent gap detectable
  at 80% power, two-sided α = 0.05, under benchmark B's components, as
  a function of runs R and tasks T; and its inverse,
  R_required(δ) for δ ∈ {1, 3, 5} points (δ ∈ {0.01, 0.03, 0.05}).
- **E6 — audit verdicts:** published pairwise gaps vs E5 at the design
  actually used (§3.5).

The random-effects split and both reporting levels of design §1 stand:
component level (the falsifier's literal terms) and design level,
Var(Ŝ_i) ≈ σ²_task / T + σ²_run / (T·R) (+ grader analogue where
identified).

### 3.2 The ≥3-benchmark set — frozen selection rule (design §4, unchanged)

A benchmark enters the set **iff** (a) genuine repeated runs (n_ij ≥ 2
for a substantial share of agent×task cells) are publicly available at
run level, (b) outcomes are binary or binarisable without judgement
calls, and (c) task identities are stable across runs. Candidate pool
(≥6 candidates for 3 slots), carried unchanged:

| # | Benchmark / corpus | Repeated-run source | Status carried into the census |
|---|---|---|---|
| B1 | METR task suite (HCAST + RE-Bench records) | Local flagship-reused files | Verified end-to-end by the pilot (B1 only) |
| B2 | HAL corpus (`agentevals/hal_traces`, HF) | Per-benchmark subsets only | Path verified in packet; census verifies at ingest (§5) |
| B3 | τ-bench (retail/airline) | pass^k design — repeats public by construction | Path verified in packet; census verifies at ingest |
| B4 | SWE-Bench-Verified via Bjarnason et al. trajectories | 10 runs × configurations | Packet marked availability UNVERIFIED; the fallback verified the release public (CC-BY-4.0, §1.3) — census still verifies at ingest |
| B5 | de la Rubia coding-agent runs | 584 runs, GitHub | Census verifies repo / licence / data presence |
| B6 | CORE-Bench (inside HAL's span) | Public harness + HAL rollouts | Repeat structure re-verified at census |

The set is the first ≥3 candidates that pass the selection rule **and**
ingest verification (§5), taken in an order fixed by the rule's
application, never by any outcome statistic. If more than 3 pass, all
passing benchmarks are estimated and reported (the falsifier verdict
reads on the full passing set, §4); no benchmark is dropped after its
components have been seen.

### 3.3 Per-benchmark anchor check (design §4, unchanged)

Before any variance estimate from a benchmark is trusted, a
published-style score for that benchmark is recomputed from raw
run-level records two independent ways (pooled run mean; the
benchmark's own published weighting where one exists — for METR, the
equal_task_weight-weighted mean) and both are reported, together with
the record-count cross-check (Σ cell n == filtered records). Anchor
failure on a benchmark voids that benchmark's results and routes back
to Stage 6 (coding) for an ingest fix — the pilot's §1.6 rule, applied
per benchmark. A benchmark whose anchor cannot be repaired is recorded
in the H-DATA ledger (§5.3).

### 3.4 Per-benchmark MDE / required-T tables — to be produced

For every benchmark in the set, at its actual design (design §5,
unchanged formulas):

- Paired design (primary; same task set, both agents):
  SE_diff(R) = sqrt( σ²_task,diff / T + (σ²_run,A + σ²_run,B) / (T·R) );
  **MDE(R) = 2.802 · SE_diff(R)** (α = 0.05 two-sided, power 0.80;
  multiplier 1.960 + 0.842). Unpaired variant also computed
  (σ²_task,A + σ²_task,B in place of σ²_task,diff).
- Design table: MDE at R ∈ {1, 2, 4, 8, actual-R-used}; R_required for
  δ ∈ {0.01, 0.03, 0.05}; where the R_required denominator is ≤ 0,
  the table states **no number of runs suffices** and reports
  T_required at the benchmark's actual R instead. This edge case is a
  result, not an error.
- Sensitivity: t-critical values with df = T − 1 alongside the normal
  values; conclusions drawn on the normal values, flagged wherever
  the t variant changes a verdict.
- The headline pair per benchmark is selected by the pilot's
  deterministic, outcome-free rule carried forward: the pair of agents
  sharing the most tasks with ≥2-run cells for both (ties: most runs
  in those cells, then name order). Component inputs to E5 are taken
  from both co-primary arms under the disagreement rule (§6.5): the
  moment-arm table is primary; the model-arm table is reported
  alongside it, in full, for every benchmark.
- Each table sits next to the runs the benchmark's published reporting
  actually used (SQ1 of the packet).

### 3.5 Published-gap audit (E6)

For every benchmark in the set: for each published pairwise gap that
can be sourced to the benchmark's own publication or official
leaderboard (source, gap value, and the T and R of the design actually
used are recorded at census time; no gap is reconstructed, estimated,
or invented where no published value can be sourced), classify the gap
against the moment-arm MDE at that design: **gap ≥ MDE** —
"detectable at the design used"; **gap < MDE** — "below the MDE at
the design used". Where the model-arm MDE (§3.4) reverses a
classification, the row is flagged **arm-sensitive** and both
classifications are shown. Audit rows are reported per benchmark with
their sources; the audit argues depth-over-breadth by design
(dossier §3, T6) and says so.

---

## 4. Falsifier, refinement R1, and kill criteria — binding

### 4.1 The area falsifier, carried VERBATIM

From the shortlist, via `RESEARCH_PACKET.md` §5 and the frozen pilot
pre-registration (`EXPERIMENTS.md` §1.1), unaltered:

> The thesis dies if, on ≥3 benchmarks with genuine repeated runs, run-level
> + grader variance is <10% of task-sampling variance — i.e., single-run
> scores are already as reliable as the field's usage assumes. H-DATA kill:
> if fewer than 3 public benchmarks expose enough repeated runs to estimate
> the components, the area stops at the gate rather than shrinking to one
> benchmark.

### 4.2 Refinement R1 — APPROVED 2026-10-30, carried verbatim in substance

Where a benchmark's public data cannot separately identify the environment
component from the run-level component, the environment component is counted
within the run-level component for the falsifier test, and the inseparability
is reported as an estimability limit. Threshold (0.10), benchmark count (≥3),
and H-DATA gate are unchanged.

The same treatment applies to σ²_grader where no re-grading of frozen
trajectories exists: either 0 by construction (deterministic programmatic
grading, stated as such) or not identified (model-based grading without
re-grades — reported as an estimability limit, never silently set to zero).

### 4.3 Verdict rule

- The falsifier verdict **requires all the benchmarks in the passing
  set, and in any case ≥3**: ρ is computed per benchmark (E4), and the
  thesis dies only on the set-level reading of §4.1. No single-benchmark
  reading — including the pilot's B1 reading (ρ = 0.245, CI [0.134,
  0.397]) — is the verdict.
- The formal verdict is read from the **moment arm** under the
  disagreement rule (§6.5), which is part of this registration.
- If the falsifier fires, the area stops — kill, or reframe only by
  Ranadhir's recorded decision (FRAMEWORK Gate 3). A fired falsifier
  is never negotiated, re-thresholded, or diluted by adding favourable
  benchmarks after the fact; symmetrically, a pilot-direction or
  partial-set kill reading must be reported prominently and may not be
  diluted either (pilot §1.6 rule, carried forward).

### 4.4 Kill criteria for the census (all binding)

1. **Falsifier kill** — §4.1 fires on the passing set (≥3 benchmarks).
2. **H-DATA kill** — fewer than 3 public benchmarks expose enough
   repeated runs to estimate the components, assessed through the
   ingest ledger (§5.3): corpora failing selection, verification, or
   licence count against the census, and if the passing set falls
   below 3 the area stops at the gate rather than shrinking.
3. **Anchor kill (per benchmark)** — §3.3: an unrepairable anchor
   failure removes that benchmark and is recorded in the H-DATA
   ledger; if removals bring the set below 3, criterion 2 governs.
4. **Licence kill (per corpus)** — terms prohibiting research reuse
   kill that corpus on sight, with no workaround; recorded in the
   H-DATA ledger with the same set-size consequence.
5. **Not kills:** a model-arm fit failure (§6.4), a DISCORDANT
   benchmark (§6.5), or a "no R suffices" MDE edge case (§3.4) are
   reportable outcomes under their own rules, never silent exclusions
   and never area kills by themselves.

---

## 5. Census ingest verification — the P2-A1 lesson, as a rule

### 5.1 The rule (frozen)

> **CENSUS INGEST RULE.** For every census corpus, tensor/data presence
> is verified at ingest, at the artefact itself, before any number from
> that corpus is computed or trusted: the outcome-bearing files must be
> enumerated and parsed, their counts reconciled against the corpus's
> stated design (benchmark × agent × task × run structure, including
> the share of cells with n ≥ 2), and the licence permitting research
> reuse confirmed from the artefact or its dataset card. **Repository
> existence is not data presence**: a repo, dataset listing, paper
> badge, or README claim — including this programme's own packet or
> dossier statements — does not count as verification. A corpus whose
> outcome data cannot be found, parsed, and reconciled at ingest FAILS
> ingest verification, whatever its listing says.

### 5.2 Why this rule exists (provenance)

P2-A1, 2026-10-31 (§1.2): a headline 2026 result in this exact field
advertised public data that its public repo does not contain at any
ref — the dossier's statement that the repo held the outcome tensor
was wrong, and only ingest-level verification caught it. The dossier
§5 fallback then passed precisely because its release was verified at
the artefact (§1.3). The census inherits both halves of that lesson.

### 5.3 Consequence — the H-DATA ledger

Every candidate corpus (B1–B6, §3.2) gets an ingest-ledger entry at
census time recording: source and revision/HEAD examined; licence
found; outcome files enumerated and parsed (counts, not outcome
statistics beyond the design reconciliation in §5.1); verdict
(PASS / FAIL with the failing leg named). A corpus failing ingest
verification is recorded in the ledger as an H-DATA finding with the
consequence §4.4 specifies: it does not enter the set, its absence
counts toward the H-DATA assessment, and if the passing set falls
below 3 the H-DATA kill fires. A failed corpus is never quietly
replaced by an unlisted corpus; any substitution beyond the B1–B6
pool requires a pre-registration amendment frozen before that
substitute's outcomes are seen (§9.2).

---

## 6. Co-primary estimation arms (the amendment's substance)

Decision 1 (ii) (§1.1) and dossier §3 (technique class T2) promote the
model-based arm from the design's reserved cross-check (design §7,
approach 2) to **co-primary**. Both arms estimate the **same estimands
E1–E6 on the same cells** (§7.1); neither arm's estimand list differs
from the other's. Co-primary means: both arms are specified here,
before any census data; both are run for every benchmark in the set;
both are reported in full. It does not mean either arm may be picked
after results are seen (§6.5).

### 6.1 Arm A — method of moments (carried from design §3, unchanged)

For cell (i, j) with n_ij ≥ 2 runs and empirical rate p̂_ij:

- Within-cell variance, unbiased for binary Y:
  s²_ij = (n_ij / (n_ij − 1)) · p̂_ij(1 − p̂_ij).
- σ̂²_run(i) = n_ij-weighted mean of s²_ij over tasks (equal-weight
  variant reported as sensitivity).
- σ̂²_task(i) = max(0, Var_j(p̂_ij) − mean_j[ p̂_ij(1 − p̂_ij) / n_ij ]),
  truncation at 0 reported whenever it binds.
- Paired-design components for MDE estimated analogously from paired
  cell means (σ²_task,diff); unpaired variant also computed.
- Pooling: per-agent components averaged with equal weights for the
  benchmark-level ρ; the per-agent table is retained.
- Uncertainty: cluster bootstrap over tasks, **B = 2,000**, fixed seed
  (§7.2), percentile CIs — carried from the pilot unchanged.
- Implementation: `code/components.py` / `code/mde.py` as validated at
  Stage 6 (validate.py 14/14), unchanged for this arm.

### 6.2 Arm B — hierarchical Bayesian / GLMM partial pooling (new specification)

**Model form (binary primary endpoint).** Fitted separately per
benchmark B and per agent i, over exactly the cells Arm A uses
(n_ij ≥ 2; runs nested in tasks within the agent–benchmark):

- Y_ijr ~ Bernoulli(p_ij), r = 1…n_ij.
- logit(p_ij) = μ_i + v_ij, with v_ij ~ Normal(0, τ_i), i.i.d. across
  tasks j. (μ_i is the agent's benchmark-level logit mean; v_ij is
  the task propensity deviation — the facet structure E1–E2 imply.
  Environment is folded into the run level per R1, exactly as in
  Arm A; there is no separate environment term, because no census
  corpus identifies one.)
- **Probability-scale derivation (so Arm B estimates E1–E2, not a
  different quantity):** for each posterior draw, compute the p_ij
  over the agent's observed tasks, then
  E1_B(i) = Var_j(p_ij) and E2_B(i) = mean_j[ p_ij(1 − p_ij) ].
  E4_B per benchmark pools the per-agent draws with equal agent
  weights, exactly as E4 does for Arm A, and ρ_B is computed
  draw-by-draw, so its posterior interval is a derived quantity, not
  a ratio of summaries.
- **Grader facet (E3), only where identified:** where a corpus
  re-grades frozen trajectories (re-grade index g of the same
  trajectory), the model extends to
  logit(p_ijg) = μ_i + v_ij + w_ijg, w_ijg ~ Normal(0, τ_g,i), and
  E3_B(i) = E_j[ Var_g(p_ijg) ] computed draw-by-draw over the
  re-grade distribution. Where no re-grades exist, Arm B records the
  same estimability-limit entry as Arm A (deterministic-grader zero
  stated where grading is programmatic). No grader term is fitted
  where the design cannot identify it.
- **Continuous secondary endpoint:** the same nesting on the original
  scale — Y_ijr = μ_i + v_ij + ε_ijr, v_ij ~ Normal(0, τ_i),
  ε_ijr ~ Normal(0, σ_i) — with E1_B(i) = τ_i² and E2_B(i) = σ_i²
  read from the posterior directly. Reported as secondary, as in
  Arm A.

**Priors (fixed; no tuning after data).**

- μ_i ~ Normal(0, 2.5²) on the logit scale.
- τ_i ~ Half-Normal(0, 1); τ_g,i ~ Half-Normal(0, 1) where fitted.
- Continuous arm: μ_i ~ Normal(0, 2.5²) on the score scale's logit
  where the score is in [0,1] and as Normal(0, 5²) otherwise —
  the choice is determined by the corpus's recorded score range at
  ingest, not by results; τ_i, σ_i ~ Half-Normal(0, 1).
- **Prior sensitivity (pre-specified, always reported):** every fit
  is re-run once with τ priors widened to Half-Normal(0, 2) and
  μ_i ~ Normal(0, 5²). Sensitivity results are reported alongside the
  primary fit; they never replace it, and a verdict is never read
  from a sensitivity fit.

**Sampler settings (fixed).** Hamiltonian Monte Carlo / NUTS:
4 chains, 2,000 warm-up + 2,000 post-warm-up draws per chain,
target_accept = 0.95, max_treedepth = 12, chain seeds derived from
the census seed (§7.2) as seed + chain index. No setting changes
after a fit has been seen, except the single remediation in §6.4.

**Sparse-cell handling (fixed).** The n_ij ≥ 2 inclusion rule is
Arm A's and is unchanged: single-run cells are excluded from both
arms' primary fits, never imputed, and counted in the coverage
report. All-success and all-failure cells are **retained** in both
arms (Arm A: s²_ij = 0 is data; Arm B: partial pooling plus the
stated priors keep such cells finite without dropping them). An
agent with few eligible tasks is fitted and reported with its task
count attached; no agent-level minimum is imposed beyond the frozen
design, and no cell, task, or agent is dropped for the size or
direction of its outcomes. As a labelled sensitivity only, Arm B is
also fitted including n_ij = 1 cells; that fit is never the primary
reading and never enters the verdict.

### 6.3 Software and version pinning

- Reference stack: Python 3.12 (the VM's recorded interpreter),
  PyMC 5-series with ArviZ for sampling and diagnostics, NumPy /
  SciPy as already used by Arm A. (Recorded honestly: PyMC / ArviZ
  are **not yet installed** in the area tree at freeze; no version is
  claimed here that has not been observed.)
- **Pinning approach (binding):** before any census ingest, a
  Stage-6 return builds `code/glmm.py`, adds the model arm to
  `validate.py` — including planted-component recovery for Arm B on
  synthetic data, to a tolerance stated in that harness work before
  it runs — and records the exact installed versions in a lockfile
  under `code/` (pip freeze output with package hashes where
  available). The lockfile's SHA-256 is appended to
  `PREREGISTRATION.sha256` **before** census ingest begins. The model
  arm may not be run on census data until that harness extension is
  green and recorded in `STATE.md`.
- Any version change after the lockfile is frozen is either a
  pre-results amendment (§9.2) or a logged deviation (§9.3) — never
  a silent environment drift.

### 6.4 Convergence / fit diagnostics and their failure consequences

For every Arm B fit, all of the following are computed and reported:

- R-hat ≤ 1.01 for μ_i, τ_i (and τ_g,i where fitted) and for the
  derived per-agent E1_B, E2_B and benchmark ρ_B.
- Bulk- and tail-ESS ≥ 400 for each derived estimand above.
- Divergent transitions: zero tolerated in the reported fit.
- Posterior predictive check on cell success counts, discrepancy =
  variance of cell proportions across tasks; the predictive p-value
  is reported, and p < 0.01 or p > 0.99 flags the fit **model-misfit**.
- Prior-sensitivity comparison (§6.2): if widening the priors moves
  the benchmark ρ_B posterior mean by more than 0.05, the fit is
  flagged **prior-sensitive** and the flag travels with every report
  of that number.

**Failure consequences (fixed, in order).** (1) On a first diagnostic
failure (R-hat, ESS, or divergences), exactly one remediation is
permitted: re-run that fit once with target_accept = 0.99 and
warm-up doubled to 4,000, all else unchanged; both runs are retained
and reported. (2) If the remediated fit still fails, or the fit is
flagged model-misfit, Arm B for that agent–benchmark (or benchmark,
for ρ_B) is recorded as **FAILED / FLAGGED** in the results — it is
not dropped silently, not replaced by a different model, prior, or
estimator, and no third attempt is made. (3) A failed Arm B does not
void Arm A and does not kill the area (§4.4.5); the disagreement
rule's missing-arm clause (§6.5) applies, and the Stage 8 tester is
handed the failure record explicitly.

### 6.5 THE DISAGREEMENT RULE (frozen, verbatim-governing)

**Material disagreement** between the arms on a benchmark is defined,
before any data, as any of: (a) the pooled point estimates of ρ
differ by more than 0.05 in absolute value; (b) the two 95% intervals
(Arm A bootstrap percentile; Arm B posterior credible) lie on
opposite sides of the 0.10 falsifier threshold; or (c) a pooled E1
or E2 point estimate differs between arms by a factor outside
[2/3, 1.5].

> **DISAGREEMENT RULE.** If the moment arm and the model-based arm
> materially disagree on a benchmark, **both arms' estimates are
> reported side-by-side, in full, in every table, summary, and
> later-stage document that reports that benchmark**, and the
> benchmark is flagged **DISCORDANT**. The formal falsifier verdict
> (§4.3) is read from the **moment arm alone** — because the
> falsifier, its 0.10 threshold, and R1 were frozen in
> moment-estimator terms in the approved packet and the pilot
> registration, and re-basing a frozen threshold onto a model-based
> scale would move the bar. The model arm may never override,
> replace, average with, or be selected over the moment arm for the
> verdict; and the moment arm may never be suppressed, softened, or
> re-described because the model arm reads more favourably (or vice
> versa). A DISCORDANT benchmark supports no clean survival claim and
> no clean kill claim beyond the formal verdict: Stage 9 / Stage 10
> writing must state the discordance, its direction, its size, and
> the pre-registered candidate causes (sparse cells; a
> prior-sensitive or model-misfit flag under §6.4; prior influence at
> the §6.2 sensitivity) **without resolving it post hoc**. For MDE
> and the audit, both arms' tables are reported (§3.4–§3.5) and
> arm-sensitive rows are flagged, never resolved by picking an arm.
> If Arm B has FAILED for a benchmark under §6.4, that benchmark is
> reported as **moment-only, model arm failed** — a stated limitation,
> not a disagreement and not a licence to treat the moment reading as
> model-confirmed. Selecting, after results are seen, whichever arm
> gives the preferred verdict — or reporting only one arm anywhere —
> is a protocol violation, recorded as such in `STATE.md`.


---

## 7. Analysis plan, split / seed discipline

### 7.1 Pipeline and cell discipline

The design §6 pipeline shape governs, extended by §5 and §6:
ingest verification + H-DATA ledger (§5) → harmonise to the canonical
run table (benchmark, agent, task, run, y_bin, y_cont, grader_kind,
env fields where present) with a coverage report (cells with n ≥ 2
share, per agent) → per-benchmark anchor check (§3.3) → components,
both arms (E1–E4) → MDE tables (E5, §3.4) → published-gap audit
(E6, §3.5) → falsifier comparison (§4). Every reported number is
traceable to a run-table file hash recorded in the results artefacts.

Cell discipline, carried from the pilot unchanged: only cells with
n_ij ≥ 2 enter the estimators; single-run cells are excluded, never
imputed; no outcome-driven subsetting of tasks, agents, runs, or
benchmarks is permitted at any step.

### 7.2 Splits and seeds

- **No train / test split exists in this study** — it is an estimation
  census, not a prediction exercise: all eligible cells of a passing
  benchmark are used, once, under the rules above. There is no
  held-out set to peek at and no split to re-draw after results.
- **Bootstrap:** cluster bootstrap over tasks (resample tasks with
  replacement within agent, recompute E1 / E2 / E4), **B = 2,000**,
  percentile CIs — carried from the pilot.
- **Seeds (fixed for the census):** the census seed is **20261031**.
  Arm A bootstrap for each agent–benchmark uses that seed through the
  pilot code's existing seed handling; Arm B chain seeds are
  20261031 + chain index (§6.2). Synthetic / harness work keeps its
  existing seeds. Any stochastic procedure added at census time must
  derive its seed from 20261031 by a rule written down before it runs.
- **Exploratory work:** anything computed outside §§3–6 is labelled
  EXPLORATORY in the artefact that contains it, is excluded from the
  falsifier verdict, the MDE tables, and the audit, and may be
  promoted into the confirmatory set only by a §9.2 amendment frozen
  before the relevant outcomes are re-examined — in practice, after
  the census it cannot be promoted for this census at all.

### 7.3 Reporting artefacts

Per benchmark: JSON + markdown tables carrying the coverage report,
anchor values, both arms' E1–E4 with intervals and diagnostic /
sensitivity flags, the §3.4 design tables (both arms), the §3.5 audit
rows, and the ledger references (§5.3). Set level: the falsifier
comparison table across the passing set, with DISCORDANT and
moment-only flags (§6.5) visible in the table itself, not in a
footnote.

---

## 8. Collision annex (INTAKE_MEMO lesson L24)

The novelty claim this registration protects is the re-cut conjunction
of dossier §2 — *first four-component decomposition with per-benchmark
MDE design tables and a published-gap audit, on genuine repeated runs
of interactive agent benchmarks* — not the packet's original wording.
Two post-packet works are entered here so Stage 8 scores novelty
against the claim actually in force:

- **C1 — Zhou et al. (2026)**, two-component generalizability-theory
  decomposition + repetition variance ceiling, one static code
  benchmark. Status for this area: **unverified-by-us** (§1.2);
  its data-availability failure is a census input (§5), not a
  reproduced result.
- **C2 — Messing (2026)**, LLM-pipeline variance decomposition with
  interaction terms (prompt / judge / temperature facets). This area
  does not model facet interactions; that is a stated limitation
  (dossier §3, T7), recorded here so it is never a silent one.

---

## 9. Loop rule, amendments, deviations

### 9.1 One change at a time

Within the census, the Solution Engineering System loop rule governs:
**one change at a time**, measured against the same anchors (the
Bjarnason fallback reproduction, §1.3, and the pilot's B1 slice);
every fix is followed by a re-run of `validate.py` and, where the
changed code touches an anchor path, a re-run of that anchor, before
further work proceeds. A plateau routes back to the stage whose
evidence it questions, with the question written down — it is not
worked around by changing a second thing.

### 9.2 Amendments

Any change to an estimand, the falsifier, R1, a threshold, the
selection rule, the disagreement rule, a prior, or a diagnostic
consequence requires **Ranadhir's recorded decision** (FRAMEWORK
Gate 3) and a new frozen amendment appended to the hash chain
**before** the affected outcomes are examined. Amendments never edit
this file or any prior frozen text.

### 9.3 Deviations

Anything done differently from this registration in execution is
logged as a named deviation in `EXPERIMENTS.md` (append-only) and in
`STATE.md`, with date, reason, and which results it touches, at the
time it happens. An unlogged deviation discovered later is reported
as a protocol defect to the Stage 8 tester, not quietly absorbed.

---

## 10. Stage 8 hand-off (fresh tester)

On census completion, the work passes to **Stage 8: a fresh tester
who did not build the solution and did not author earlier
deliverables for this area** (FRAMEWORK Gate 4), producing
`TESTING_REPORT.md` with **both** Scoring System v2 verdicts:

- **Quality /10**, and
- **Editor Screen /12 at the named venue: JMLR** (the Editor Screen
  target on record in `ORCHESTRATOR.md`; HIGH flag if total ≤ 5/12
  or any of S1 / S2 / S4 = 0). A Quality score below 8/10 or a HIGH
  flag requires Ranadhir's explicit recorded override naming the
  risk before any submission decision. Changing the target venue
  re-opens the screen; scores never transfer between venues.
- Planned branch, recorded now so it is not a post-hoc discovery
  (INTAKE_MEMO, lessons L70/L71): dossier §4 argues TMLR fits a
  measurement-first framing and *Machine Learning* (Springer,
  subscription route) is the safe second home; if the census numbers
  land as a measurement paper rather than a framework paper, the
  venue branch is taken as a planned decision with a fresh Editor
  Screen at that venue — not as a rescue after a rejection. All
  three venues are in the programme's verified zero-fee set.
- The tester brief is written in domain units (INTAKE_MEMO lesson
  L09): *Would METR or HAL change their reporting from these tables?
  Is every design number stated at the design the benchmark actually
  uses? Does the audit classify gaps a reader can check against the
  published record?* A pass on code-derived criteria alone does not
  count as a pass for this area.
- The hand-off explicitly includes: the H-DATA ledger (§5.3), every
  DISCORDANT / moment-only flag (§6.5), every Arm B failure record
  (§6.4), the deviation log (§9.3), and the C1 unverified-by-us rule
  (§1.2) for checking in all draft writing.

No submission occurs at any stage without Ranadhir's verification of
the final paper (FRAMEWORK Gate 5). Sole author; zero-fee venues only.

---

## 11. Compute statement

### 11.1 Base plan — CPU-only

All registered computation — ingest, moment estimation, cluster
bootstrap (B = 2,000), MDE tables, audit, and Arm B sampling on
run-level binary outcomes — is **CPU-only**, per dossier §6 and the
packet §1.4 position: no GPU, no API spend, no money spent under this
registration. Jobs are `nice`-compatible, per-benchmark subsets only,
and **no big download is authorised**: where a corpus's full release
is large (e.g. the Bjarnason release's 47.9 GB of trajectories, of
which the fallback needed 5.85 MB), the census pulls only the
outcome-bearing files its ingest rule (§5.1) requires and logs what
was pulled, with sizes, in the ledger.

### 11.2 The grader-identification flag — UNMADE decision, out of scope

Identifying σ²_grader by **re-grading frozen trajectories with judge
models** would be new model inference (API / GPU-class spend). That
decision is **explicitly unmade** (dossier §6; improvement-plan D4),
is **not** part of this registration, and no result under this
registration may depend on it. Under this registration E3 stands
exactly as §3.1 specifies: estimated where a corpus itself identifies
it, an estimability limit everywhere else. If Ranadhir later makes
that decision, it enters through a §9.2 amendment with its own priced
compute packet — never as an execution-time improvisation.

---

## 12. Freeze statement

This addendum was drafted and frozen on **2026-10-31**, before any
census data was downloaded, ingested, or computed on, and before any
Arm B code existed. At freeze: the pilot's frozen texts stand
untouched (§0; hashes in `PREREGISTRATION.sha256`), the anchor is
established via the fallback (§1.3), `validate.py` is 14/14 PASS, the
census is **not started**, and census execution awaits its own go
(§2.3). Open items that remain before the census can start are listed
in `STATE.md` at the time of this freeze; none of them is resolved
by this document unless it says so above.
