# Stage 7 census — FINAL results (Area 1: agent-benchmark metrology)

**Status: CENSUS COMPLETE, 2026-11-02T05:54:49Z** (final chain generation ended rc=0; all
frozen stages — ingest, anchors, Arm A, Arm B, Arm B summary, tables, report — executed).
This document is the final census report. It supersedes the Arm-A-only interim version
written 2026-11-01 01:43 ET. Every number below is taken from the census artefacts on
disk (`results/census/*.json`, `results/census/fits/`); nothing is rounded from memory.

Frozen basis (hash-verified, unchanged throughout): EXPERIMENTS.md +
EXPERIMENTS_ADDENDUM_STAGE7.md (sha256 in PREREGISTRATION.sha256), SOLUTION_DESIGN.md,
environment as executed (PyMC 5.25.1 / PyTensor 2.31.7 / NumPy 2.0.2 / SciPy 1.15.3) — NOT the frozen lockfile versions (PyMC 5.16.2 / PyTensor 2.25.5 / NumPy 1.26.4 / SciPy 1.11.4); see the deviation entries added 2026-11-10 (D1–D3) at the end of this document.
Sampler per addendum §6.2 (NUTS, 4 chains, 2,000 warm-up + 2,000 draws, target_accept
0.95, max_treedepth 12, seeds = census seed 20261031 + chain index); pass bar §6.4
(R-hat ≤ 1.01, ESS ≥ 400, 0 divergences; at most one remediation at target_accept 0.99 /
tune 4,000; FAILED/FLAGGED recorded, never dropped).

## 1. The census set (§5.1)

- **B1 (METR task suite): IN.** 39,363 run outcomes, 52 agents, 177 tasks; cells with
  n≥2: 0.979; runs in such cells: 0.997.
- **B3 (τ-bench): IN.** 1,980 run outcomes, 2 agents, 165 tasks; cells with n≥2: 1.000.
- **B4 (Bjarnason et al. 2026 fallback-anchor corpus): IN.** 53,212 run outcomes,
  12 agents, 500 tasks; cells with n≥2: 0.991; runs in such cells: 0.999.
- **B2: OUT (ingest verification FAIL).** huggingface.co/datasets/agentevals/hal_traces
  returns HTTP 401 (dataset page, file tree, and file resolve all probed 2026-11-01);
  the outcome-bearing files (encrypted .zip archives, 0.3–3.5 GB each) can neither be
  enumerated nor parsed, and §11.1 forbids downloads of that size in any case.
- **B5: OUT (ingest verification FAIL).** Corpus verified present and MIT-licensed
  (github.com/earino/identical-runs-different-results, 468 per-run artefacts), but it
  fails the §5.1 selection legs: the outcome is a continuous holdout AUC with no
  pre-stated binary bar, and the corpus contains exactly ONE task, so E1/E4 have no
  task population to estimate over.
- **B6: OUT (ingest verification FAIL).** Same HAL access failure as B2 (HTTP 401);
  CORE-Bench's repeat structure, frozen as "re-verified at census", cannot be
  re-verified at the artefact.
- Anchors: B1 estimates reproduce the pilot artefact bit-for-bit on overlapping slices
  (max |Δ pass-rate| = 0.0); B4 config means reproduce the source artefact to 1.4e-14;
  B3's two published contrasts are reproduced by the census corpus itself. E3 = 0 by
  construction in all three benchmarks (§4.2; no corpus re-grades frozen trajectories).
- Recorded discrepancy (unchanged from the run record): the printed slice table in
  the printed pilot table in EXPERIMENTS.md's pilot-result addendum (## 2, 'PILOT RESULT', appended 2026-10-30; grok_4 T=162, ρ 0.643) — cited in earlier records as '§7.1', a section number that does not exist in the hash-verified file (its sections run §§1–4 with numbered pilot subsections 2.1–2.5); the artefact governs is NOT reproducible from the sealed pilot
  artefact (grok_4 T=97, ρ 0.24486); the census anchors on the artefact.

## 2. Verdicts — both arms side-by-side (§6.5 applies to all three benchmarks)

The §6.5 pooled-point criterion (a) triggers for every benchmark (see §6 below), so
both arms are reported side-by-side everywhere and each **formal falsifier verdict is
read from Arm A (the moment arm) alone**, exactly as the frozen rule prescribes.

| Benchmark | Arm A ρ (BCa 95%) | Arm A verdict | Arm B ρ_B (95% CrI) | Arm B verdict | **Formal verdict (Arm A)** |
|---|---|---|---|---|---|
| B1 (METR) | 0.3767 [0.3154, 0.4426] | SUPPORTED | 0.4709 [0.4537, 0.4886] | SUPPORTED † | **SUPPORTED** |
| B3 (τ-bench) | 0.9834 [0.7798, 1.2239] | INDETERMINATE | 1.0823 [0.9200, 1.2741] | INDETERMINATE | **INDETERMINATE** |
| B4 (Bjarnason fallback) | 0.7134 [0.6355, 0.7844] | SUPPORTED | 0.8237 [0.7960, 0.8526] | INDETERMINATE (fit failure, §6.4) | **SUPPORTED** |

† B1 Arm B carries the §6.4 prior-sensitivity flag (see §3).

Reading: in all three benchmarks the two arms agree on the falsifier's substance —
task-sampling variance is a first-order component of benchmark noise (ρ well above
the 0.10 floor wherever the verdict is readable, and never REFUTED). The arms differ
in level (Arm B's model-based ρ runs 0.09–0.11 higher), which is precisely the kind
of estimator disagreement §6.5 was written to surface rather than average away.

## 3. B1 (METR task suite) — detail

- **Arm A (moments, primary binary estimand):** pooled ρ = **0.3767**, BCa 95%
  [0.3154, 0.4426] (2,000 task-bootstraps and jackknife agree: jackknife ρ 0.3767 ±
  0.0333) → **SUPPORTED**. Secondary continuous estimand: ρ = 0.4350, BCa
  [0.3657, 0.5102]. Headline pair gpt_4 ‖ o1_preview on T=163 shared tasks.
- **Arm B (GLMM):** pooled ρ_B = **0.4709**, 95% [0.4537, 0.4886] over 49 of 51
  eligible agents → **SUPPORTED** on the frozen row logic (point ≥ 0.30; interval
  inside (0, 1); both sensitivity points — widened-prior 0.5457, singletons 0.4709 —
  inside (0, 1)). Continuous pooled ρ_B = 0.4268 [0.4075, 0.4464] (51 agents), close
  to Arm A's continuous 0.4350.
- **§6.4 flags (Arm B):** **prior-sensitivity flag TRUE** — widening the priors moves
  pooled ρ_B by 0.0748 (> 0.05). Caveat carried with the flag: the widened-prior pool
  covers only 28 of 51 agents because **23 of 51 binary sensitivity-prior fits FAILED**
  §6.4 even after the single permitted remediation (plus 1 continuous sensitivity
  failure, deepseek_v3); the shift therefore mixes a prior effect with an agent-set
  effect, and the frozen pooled construction does not decompose the two. Primary fits:
  49 PASS, 2 FAILED (davinci_002, gpt_3_5_turbo_instruct — neither is a headline
  agent, and 2/51 = 3.9% < 25%, so the Arm B verdict stands). Misfit share of primary
  fits (PPC p outside [0.01, 0.99]): 1/51 = 0.0196.
- **Design table (MDE in score points, t variant; headline pair, T=163):** Arm A —
  R=1: 0.1051, R=2: 0.0837, R=4: 0.0706, R=8: 0.0631, R=actual (10.92): 0.0609.
  Arm B (unpaired construction) — R=1: 0.1364, R=2: 0.1213, R=4: 0.1130, R=8: 0.1087.
  Even at R=8 the paired Arm A design cannot resolve a 0.05 gap at T=163 (needs
  T=257 tasks at R=8; a 0.10 gap needs R=2). Full rows: `tables_B1.json`.

## 4. B3 (τ-bench) — detail

- **Arm A:** pooled ρ = **0.9834**, BCa 95% [0.7798, 1.2239] → **INDETERMINATE**
  (interval exits the (0, 1) definitional range; with 2 agents the pooled claim
  rests on a cross-fitted pair ratio and is intrinsically fragile — the frozen rules
  record it as indeterminate rather than supported).
- **Arm B:** pooled ρ_B = **1.0823**, 95% [0.9200, 1.2741] → **INDETERMINATE** (same
  range rule). All 6 frozen fits PASS; no fit failures; misfit share 0.0. Prior
  sensitivity: widened-prior pooled 1.0324, shift 0.0499 — below the 0.05 flag by
  0.0001 (recorded as borderline, not flagged). Singletons pooled identical to
  primary (1.0823): B3 contains no singleton cells.
- **Design table (headline pair gpt-4o ‖ sonnet-35-new, T=165):** Arm A MDE —
  R=1: 0.1251, R=2: 0.0987, R=4: 0.0825, R=8: 0.0730, R=actual (6.00): 0.0763.
  Arm B (unpaired) — R=1: 0.1526, R=2: 0.1313, R=4: 0.1193, R=8: 0.1128.
- **Published-contrast audit (2 rows):** both contrasts classify BELOW the Arm A MDE
  at the designs actually used, and identically under Arm B (not arm-sensitive):
  tau-retail gap 0.088 vs MDE_A 0.0927 / MDE_B 0.1383; tau-airline gap 0.040 vs
  MDE_A 0.1412 / MDE_B 0.2097. Full rows: `tables_B3.json`.

## 5. B4 (Bjarnason et al. fallback corpus) — detail

- **Arm A:** pooled ρ = **0.7134**, BCa 95% [0.6355, 0.7844] → **SUPPORTED**.
  Headline pair nano-agent|Devstral-2|temp=0 ‖ temp=0.2 on T=500 shared tasks.
- **Arm B:** pooled ρ_B = **0.8237**, 95% [0.7960, 0.8526] over the 9 agents whose
  primary fits passed — but the Arm B verdict is **INDETERMINATE (fit failure,
  §6.4)**: the frozen tables rule fires because primary fits for BOTH headline-pair
  agents (nano-agent|Devstral-2|temp=0 and temp=0.2) FAILED §6.4, as did
  nano-agent|Qwen3-32B|temp=0 (3/12 = 25% of primaries failed in total; the failed
  fits are bulk-ESS shortfalls — e.g. Devstral-2 temp=0 primary ESS 359.6 → 277.7
  after remediation, R-hat ≈ 1.005–1.007, zero divergences throughout — recorded,
  never dropped, no third attempt per §6.4). The pooled point over the surviving
  agents is shown for the record; it does not carry a verdict. Prior sensitivity:
  shift 0.0015 (no flag; sens pool 8 agents, 0.8251). Singletons pooled 0.8428
  (8 agents). Misfit share 0.0.
- **Design table (headline pair, T=500):** Arm A MDE — R=1: 0.0462, R=2: 0.0329,
  R=4: 0.0236, R=8: 0.0172, R=actual (9.92): 0.0156. Arm B (unpaired) — R=1: 0.0853,
  R=2: 0.0787, R=4: 0.0752, R=8: 0.0734.
- **Published-contrast audit (24 rows):** 15 ABOVE/ABOVE, 6 BELOW/BELOW, and
  **3 arm-sensitive (ABOVE under Arm A, BELOW under Arm B)**: "nano-agent: model
  pair at temp0 temps" (Qwen3-32B temp=0 vs DeepSWE-preview temp=0, gap 0.040),
  "r2e-gym: model pair at temp0 temps" (same pair, gap 0.031), and "cross-scaffold:
  DeepSWE-preview at default temp" (gap 0.030). Full rows: `tables_B4.json`.

## 6. §6.5 disagreement evaluation (computed from the artefacts above)

Material disagreement = (a) pooled ρ points differ by > 0.05; (b) the two 95%
intervals lie on opposite sides of the 0.10 falsifier threshold; or (c) a pooled
E1/E2 point estimate differs by a factor outside [2/3, 1.5].

| Benchmark | (a) |Δρ| | (b) opposite sides of 0.10? | (c) pooled E1/E2 factor | §6.5 status |
|---|---|---|---|---|
| B1 | 0.0942 — **triggers** | No (both intervals entirely above 0.10) | Not evaluable: the frozen Arm B pooled artefact carries ρ only (no pooled E1/E2), so no factor is computed rather than estimated post hoc | **DISCORDANT** → side-by-side; formal verdict from Arm A |
| B3 | 0.0989 — **triggers** | No | Same as B1 | **DISCORDANT** → side-by-side; formal verdict from Arm A |
| B4 | 0.1103 — **triggers** | No | Same as B1 | **DISCORDANT** → side-by-side; formal verdict from Arm A |

In all three benchmarks the arms' verdicts coincide except B4, where Arm B's
INDETERMINATE is a fit-failure verdict (not an evidence verdict) and Arm A's
SUPPORTED stands as the formal verdict. No arm was picked over the other and no
average was taken, per §6.5. The contrast-level analogue (frozen audit rows) is
reported in §§4–5: 3 of 24 B4 contrasts are arm-sensitive; both B3 contrasts are not.

## 7. Fit inventory and §6.4 accounting

Frozen Arm B fit list (§6.2–6.3, from the driver): **297 fits** — B1 255 (51 eligible
agents × {binary, continuous} × {primary, sensitivity-prior} + binary singletons;
gpt2 excluded with 0 repeated cells), B3 6 (2 agents × 3 binary kinds), B4 36
(12 agents × 3 binary kinds; no continuous cells).

- Existed and valid at the completion generation's takeover (2026-11-01 10:51 UTC):
  **20** (B1 11, B3 6, B4 3).
- Computed by the completion generation (2026-11-01 10:51 UTC → 2026-11-02
  05:54:49 UTC), existing fits skipped, never recomputed: **277** (B1 244, B4 33).
- Final status tally over all 297: **246 PASS, 12 REMEDIATED_PASS, 39 FAILED,
  0 FLAGGED.** By kind — B1: binary primary 49 PASS / 2 FAILED; binary sensitivity
  26 PASS / 2 REMEDIATED_PASS / 23 FAILED; binary singletons 49 PASS / 2 FAILED;
  continuous primary 46 PASS / 5 REMEDIATED_PASS; continuous sensitivity 45 PASS /
  5 REMEDIATED_PASS / 1 FAILED. B3: 6 PASS. B4: primary 9 PASS / 3 FAILED;
  sensitivity 8 PASS / 4 FAILED; singletons 8 PASS / 4 FAILED.
- Every FAILED fit followed the frozen ladder exactly (one remediation at
  target_accept 0.99 / tune 4,000; status recorded in its fit file with first-attempt
  and remediation diagnostics; no fit deleted, retried beyond the ladder, or dropped
  from the summaries — failed agents are listed in `arm_b_B1.json` / `arm_b_B4.json`).

## 8. Execution record (completion generation)

The census ran unattended through five host reboots (2026-11-01 11:33, 15:56, 17:57,
19:57, 22:10 UTC) and two transient filesystem write-fault windows (EPERM on atomic
writes, ~03:45–03:47 and ~05:16–05:19 UTC on 2026-11-02), via a single sequential
driver chain (`results/census/run_census.sh`) kept alive by a single-instance
supervisor (`results/census/supervise_census.sh`, relaunched by hand after each
reboot — it does not survive reboots). Per-fit checkpoint files made every restart
lossless except the one in-flight fit. A private PyTensor compile cache (environment
choice only) prevented recurrence of the 2026-11-01T07:18:38Z file-lock crash that
ended the earlier generation; no frozen setting was changed at any point. Full log:
`results/census/census.log`; run narrative: `CENSUS_RUN.md` (area root).

## 9. Artefact index (all under `results/census/`)

- Pooled/paired Arm A: `arm_a_B1.json`, `arm_a_B3.json`, `arm_a_B4.json`
- Arm B per-agent fits: `fits/` (297 files); pooled summaries: `arm_b_B1.json`,
  `arm_b_B3.json`, `arm_b_B4.json`
- Tables (falsifier rows, design tables, audit rows): `tables_B1.json`,
  `tables_B3.json`, `tables_B4.json`
- Run tables: `data/B1_run_table.jsonl`, `data/B3_run_table.jsonl`,
  `data/B4_run_table.jsonl`; progress: `progress.json`
- Stage record: `STAGE7_RECORD.md` (same directory; §3 final state, §5 deviations)

**Stage 7 stops here.** Per the frozen packet, the census result set feeds the
Stage 6/8 gates only on Ranadhir's instruction; no Stage 8 work was performed.


---

## Deviations and provenance — added 2026-11-10 (Stage 8 fresh-tester repair; frozen census text above unchanged except the two flagged corrections)

The Stage 8 fresh tester (TESTING_REPORT.md, 2026-11-10) found three protocol-layer defects in this record. They are repaired here, on the record, without re-running the census; the tester verified none of them overturns any verdict, flag, or audit classification.

- **D1 — environment deviation (moderate).** The census executed under PyMC 5.25.1 / PyTensor 2.31.7 / NumPy 2.0.2 / SciPy 1.15.3, not the frozen lockfile pins (PyMC 5.16.2 / PyTensor 2.25.5 / NumPy 1.26.4 / SciPy 1.11.4), after host rebuilds. Addendum §6.3/§9.3 required a pre-results amendment or a logged deviation; neither was made, and this document's header originally mislabelled the executed stack "lockfile-pinned" (corrected in place above, 2026-11-10). Mitigations verified by the tester: formal verdicts are read from Arm A (deterministic moments + seeded bootstrap over deposited run tables — stack-insensitive in substance), anchors reproduce bit-exactly / to 1.4e-14, and validate.py passes 18/18 in the current tree. Exact bit-reproduction of the 297 Arm B fits from the deposited record is therefore not guaranteed.
- **D2 — interval-method deviation (moderate).** The frozen registration specifies percentile bootstrap intervals for Arm A (addendum §6.1, §6.5(b), §7.2); the census reports BCa intervals throughout. BCa is the better method and is labelled as BCa in this document, but the change was never logged. Both interval types are deposited in arm_a_*.json; the tester verified the percentile intervals ([0.3183, 0.4480] B1; [0.7938, 1.2379] B3; [0.6440, 0.7921] B4) yield identical verdicts and identical §6.5(b) outcomes.
- **D3 — verdict-taxonomy provenance (moderate).** The SUPPORTED / INDETERMINATE / REFUTED row logic applied in §3–§5 (interval must lie entirely inside (0, 1); Arm B row additionally citing a point ≥ 0.30 condition) appears nowhere in the frozen registration, which defines only the set-level falsifier (ρ < 0.10 on ≥ 3 benchmarks ⇒ thesis dies). The taxonomy was applied consistently across all six arm–benchmark rows and is disclosed in the results; B3's INDETERMINATE rests on it. The formal set-level falsifier reading (no REFUTED; thesis not killed) is unaffected under any reading of the taxonomy.
- **D4 — MDE variant labelling (minor).** §§4–5 of this document print t-critical MDE values without a variant label; STAGE7_RECORD.md §4 prints the normal values, also unlabelled. The frozen rule (§3.4) draws conclusions on the normal values; the manuscript uses the normal values and labels them.
- **D5 — jackknife SE (minor, corrected in place above).** This document originally quoted the B1 jackknife SE as 0.0362; the artefact value is 0.0333 (arm_a_B1.json, jackknife_binary.rho_se = 0.033295). Corrected 2026-11-10.
- **D6 — pilot-table citation (minor).** Earlier records cite the irreproducible printed pilot table as "EXPERIMENTS.md §7.1"; no such section exists in the hash-verified file. The table lives in EXPERIMENTS.md's pilot-result addendum (## 2, appended 2026-10-30). The census anchors on the artefact (results/pilot_metr_v1_0.json), and the frozen file is byte-untouched (hash chain verifies).
