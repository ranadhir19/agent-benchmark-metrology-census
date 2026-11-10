# Stage 7 census — record (Area 1: agent-benchmark metrology)

**Status: COMPLETE** — final chain generation ended rc=0 at
2026-11-02T05:54:49Z with all 297 frozen Arm B fits on disk and the
summary/tables/report stages executed. Final report:
`CENSUS_RESULTS.md` (this directory). Authorised by Ranadhir
2026-11-01 00:02 ET.
Governing documents: `EXPERIMENTS.md` (frozen) Part 3 / §5 and
`EXPERIMENTS_ADDENDUM_STAGE7.md` (frozen 2026-10-31T16:00:07Z);
hash chain re-verified before launch (`PREREGISTRATION.sha256`:
chain OK). $0 spend. All numbers below are quoted from the run's
own artefacts under `results/census/` at the time of writing;
sections marked PENDING fill in as the checkpointed fits land.

## 1. Census set (§5.1 ingest verification — evidence: INGEST_EVIDENCE.md)

- **B1 METR (HCAST + RE-Bench pooled) — IN.** 39,363 run outcomes,
  52 agents, 177 tasks; 97.94% of cells have n ≥ 2; 51 of 52 agents
  estimable (gpt2 has no repeated cells). 108 identical duplicate
  run_ids counted once; 308 conflicting run_id re-listings excluded
  and listed in the ledger. Corpus = the hash-pinned file pair whose
  v1_0 hash matches the pilot artefact's recorded input exactly.
  H-DATA note: §7.1's feasibility count (57,936 records from a
  since-vanished 72 MB file pair) could not be reproduced from the
  surviving corpus; the discrepancy is recorded in the ledger, and
  the pilot-slice anchor (below) is the operative equivalence check.
- **B3 τ-bench — IN.** 1,980 outcomes, 2 agents, 165 tasks, 100% of
  cells n ≥ 2. Official release trajectories (MIT); the official
  leaderboard's pass^1 values equal the corpus's own, confirming
  these are the leaderboard runs.
- **B4 Bjarnason et al. (2026) — IN (fallback-anchor corpus,
  labelled).** 53,212 outcomes, 12 configurations, 500 tasks;
  99.08% of observed cells n ≥ 2 (some runs submitted fewer than
  500 instances; unobserved instances are missing, not failures).
- **B2 HAL generalist — FAIL (H-DATA).** The trace dataset returns
  HTTP 401 at census time (page, tree, and file-resolve probed);
  outcome files can be neither enumerated nor parsed, and §11.1
  forbids the 0.3–3.5 GB downloads in any case.
- **B6 HAL CORE-Bench — FAIL (H-DATA).** Same access failure; its
  frozen "re-verified at census" repeat-structure check is
  therefore impossible.
- **B5 de la Rubia & Pafka — FAIL (selection legs).** Corpus
  verified present and MIT-licensed at the artefact (468 run
  records, 36 pairings × 13 seeds), but the outcome is a continuous
  holdout AUC with no pre-stated binary bar (binarisation would be
  a judgement call), and the corpus contains exactly ONE task, so
  E1/E4 are not estimable from it at any run count.

Set size B = 3 (the §5.2 floor). Grader facet: no corpus in the set
re-grades frozen trajectories; E3 = 0 by construction in all three
(§4.2), stated not estimated.

## 2. Anchors (§3.3)

- B1 pilot-slice reproduction from the census run table:
  **bit-exact** (max abs diff 0.0 on grok_4's components, the
  three-way anchor means, the paired task-diff variance, and the
  continuous components vs `results/pilot_metr_v1_0.json`).
- **Recorded discrepancy:** EXPERIMENTS.md §7.1's printed slice
  table (grok_4 T=162, E1 0.0132, ρ 0.643; pooled ρ 0.305295) is
  NOT reproducible from the pilot artefact (grok_4: T=97, E1
  0.19701, ρ 0.24486). The census anchors on the artefact (§9.4);
  the §7.1 table is treated as an uncorrected reporting error in
  the frozen document. The frozen falsifier thresholds (0.30) are
  design constants and are unaffected.
- B4 per-config mean rates vs the frozen fallback artefact: max
  abs diff 1.4e-14.
- Record-count cross-checks pass for all three benchmarks.

## 3. Headline results — pooled falsifier endpoint (§4.3)

| Benchmark | Arm A ρ (BCa 95%) | Arm A verdict | Arm B ρ (post. 95%) | Arm B verdict |
|---|---|---|---|---|
| B1 METR | 0.3767 [0.3154, 0.4426] | **SUPPORTED** | 0.4709 [0.4537, 0.4886] | **SUPPORTED** † |
| B3 τ-bench | 0.9834 [0.7798, 1.2239] | INDETERMINATE | 1.0823 [0.9200, 1.2741] | INDETERMINATE |
| B4 Bjarnason | 0.7134 [0.6355, 0.7844] | **SUPPORTED** | 0.8237 [0.7960, 0.8526] | INDETERMINATE (fit failure, §6.4) |

† B1 Arm B carries the §6.4 prior-sensitivity flag: widening the
priors moves pooled ρ_B by 0.0748 (> 0.05). The widened-prior pool
covers only 28 of 51 agents (23 of 51 sensitivity fits FAILED §6.4
after the single permitted remediation), so the shift mixes a prior
effect with an agent-set effect; both sensitivity points (0.5457
widened-prior, 0.4709 singletons) remain inside (0, 1) and the Arm B
row verdict is SUPPORTED on the frozen logic. B1 Arm B primary
health: 49/51 PASS (failures: davinci_002, gpt_3_5_turbo_instruct —
neither a headline agent); misfit share 0.0196. B4 Arm B: the
INDETERMINATE is the frozen headline-failure rule — primary fits for
BOTH headline-pair agents (Devstral-2 temp=0 and temp=0.2) and for
Qwen3-32B temp=0 FAILED §6.4 on bulk ESS (zero divergences; recorded,
never dropped); the pooled point over the 9 passing agents is shown
for the record and carries no verdict. Prior-sensitivity shift B4:
0.0015 (no flag). B1 continuous, Arm B: pooled ρ_B 0.4268
[0.4075, 0.4464], corroborating Arm A's 0.4350.

B3's INDETERMINATE on both arms is a precision statement, not a
weak effect: the point estimates sit at/above ρ = 1 (run variance
comparable to or larger than task-sampling variance), and the
frozen SUPPORTED clause requires the interval to lie entirely
inside (0, 1), which intervals crossing 1 fail. Sensitivity values
for B3 (Arm B): widened-prior pooled ρ 1.0324 (shift 0.0499, below
the 0.05 prior-sensitivity flag, reported as borderline);
singleton-admission pooled ρ 1.0823 (no singleton cells exist in
B3). B3 Arm B fit health: 6/6 PASS, misfit share 0.

B1 secondary endpoint (continuous score): pooled ρ_A = 0.4350,
BCa [0.3657, 0.5102] — corroborates the binary primary.

Set summary (per §4.3, disagreements named, not averaged):
**§6.5 DISCORDANT for all three benchmarks on criterion (a)**
(pooled-point differences: B1 0.0942, B3 0.0989, B4 0.1103 — all
> 0.05; criterion (b) triggers nowhere — every interval in both arms
lies entirely above the 0.10 threshold; criterion (c) is not
evaluable because the frozen Arm B pooled artefact carries ρ only).
Both arms are therefore reported side-by-side (see CENSUS_RESULTS.md
§2) and the **formal verdicts are read from Arm A alone: B1
SUPPORTED, B3 INDETERMINATE, B4 SUPPORTED.** The arm verdicts
coincide except B4, where Arm B's INDETERMINATE is a fit-failure
verdict rather than an evidence verdict. No REFUTED verdict occurs
in the set; the falsifier's substance — run-level noise is at least
comparable to task-sampling noise (ρ ≥ ~0.38 wherever readable) —
is supported by the moment arm in two of three benchmarks and is
indeterminate, not contradicted, in the third.

## 4. Design tables (§3.4, Arm A; Arm B analogues in tables artefacts)

Headline pairs by the frozen rule — B1: gpt_4 ‖ o1_preview
(T=163 shared); B3: gpt-4o ‖ sonnet-35-new (T=165); B4:
nano-agent Devstral-2 temp=0 ‖ temp=0.2 (T=500).

- B1: MDE 0.1045 at R=1 → 0.0605 at actual R≈10.9. δ=0.10 needs
  R=2; δ=0.05 cannot be reached by runs at any R (task term binds;
  257 tasks needed at R=8); δ=0.02 needs 1,603 tasks at R=8.
- B3: MDE 0.1243 at R=1 → 0.0758 at actual R=6. δ=0.05 needs 348
  tasks at R=8 — more than double the benchmark.
- B4: MDE 0.0461 at R=1 → 0.0156 at actual R≈9.9. δ=0.02 reachable
  at R=6 (the headline pair's task-diff variance is 0.0020 — same
  model at two temperatures — so runs, not tasks, bind).

## 5. Gap audit (§3.5, Arm A classifications)

- B1: **zero rows** — no pairwise gap could be sourced to METR's
  own publications with both a numeric value and the design's
  (T, R); METR publishes time horizons and bucketed success rates,
  not overall pairwise gaps at a stated design. No gap was
  reconstructed (forbidden).
- B3: both official-leaderboard gaps are **BELOW** the MDE at the
  design actually used — retail 0.088 vs MDE 0.0927 (T=115,
  R = 4/8 asymmetric); airline 0.040 vs MDE 0.1412 (T=50). Arm B
  classifies both BELOW as well (not arm-sensitive).
- B4: 18 of 24 published Table-1 contrasts **ABOVE** MDE at their
  design (T=500, R=10); the 6 BELOW are four near-zero temperature
  contrasts (Qwen3-32B nano 0.000 vs 0.0148, Devstral-2 nano 0.003
  vs 0.0155, Qwen3-32B r2e 0.016 vs 0.0194, Devstral-2 r2e 0.005
  vs 0.0202), the r2e-gym default-temperature DeepSWE‖Devstral
  model pair (0.005 vs 0.0359), and the cross-scaffold DeepSWE
  temp-0 gap (0.012 vs 0.0195).
- B4 Arm B reclassification of the same 24 rows: 15 ABOVE/ABOVE,
  6 BELOW/BELOW, **3 arm-sensitive ABOVE→BELOW** — Qwen3-32B temp=0
  vs DeepSWE-preview temp=0 in nano-agent (gap 0.040) and in
  r2e-gym (gap 0.031), and the cross-scaffold DeepSWE-preview
  default-temperature gap (0.030). Full rows in `tables_B4.json`.

## 6. Execution notes

- Driver `code/census.py` + `code/census_adapters.py`; stages
  checkpointed (per-fit files; per-kind Arm A artefacts). validate.py
  18/18 PASS before launch and **re-run at close 2026-11-02:
  18/18 checks passed, OVERALL PASS** (area venv interpreter).
- Completion generation (2026-11-01 10:51 UTC → 2026-11-02
  05:54:49 UTC; full narrative in CENSUS_RUN.md): 20 of 297 frozen
  fits existed at takeover; 277 were computed (existing fits skipped,
  never recomputed). Final tally: 246 PASS, 12 REMEDIATED_PASS,
  39 FAILED (§6.4 ladder followed exactly; failures recorded in
  their fit files), 0 FLAGGED. Execution rode out five host reboots
  and two transient filesystem write-fault (EPERM) windows via a
  single sequential chain plus a single-instance supervisor
  (relaunched by hand after each reboot; exits on completion). A
  private PyTensor compile cache — an environment choice only, no
  frozen setting changed — prevented recurrence of the
  2026-11-01T07:18:38Z compile-cache file-lock crash that ended the
  earlier generation. An earlier parallel-driver attempt
  (census_b1_parallel.log) had died with the 07:54 UTC reboot; the
  completion generation ran strictly single-chain.
- Two engineering deviations, both recorded in CENSUS_RUN.md and
  neither touching a frozen setting or a validated module: the
  continuous bootstrap/jackknife use the multiplicity-weighted form
  of the validated estimator (equivalence verified to 1.9e-16 on
  240 resamples); a jackknife-SE formula slip (extra √n) in the
  first Arm A write was caught against the bootstrap widths and
  corrected in code and artefacts.
- Host: ~2 h reboot cadence + severe multi-job contention; the
  chain runs at default priority and resumes from checkpoints.


## Deviation addendum — added 2026-11-10 (Stage 8 repair)

The Stage 8 fresh tester (TESTING_REPORT.md) recorded three moderate protocol defects against this census: **D1** the executed stack (PyMC 5.25.1 et al.) differs from the frozen lockfile pins (PyMC 5.16.2 et al.) with no deviation logged — contrary to addendum §6.3/§9.3, and mislabelled "lockfile-pinned" in CENSUS_RESULTS.md (now corrected there); **D2** Arm A reports BCa intervals where the frozen registration specifies percentile bootstrap — BCa labelled in the census documents, change unlogged; verdicts identical under both (tester-verified); **D3** the SUPPORTED/INDETERMINATE row taxonomy (interval inside (0, 1); Arm B point ≥ 0.30) is not in the frozen registration, which defines only the set-level falsifier — applied consistently, disclosed in results, and the set-level falsifier reading is unaffected. Full entries: CENSUS_RESULTS.md, "Deviations and provenance — added 2026-11-10". No verdict, flag, or audit classification changes.
