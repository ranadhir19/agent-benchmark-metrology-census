# Census ingest evidence — Area 1, Stage 7 (2026-11-01)

Ingest-verification evidence gathered at the artefacts on 2026-11-01
(§5.1: a candidate enters the census set only after its data is
enumerated and parsed at the artefact — paper, catalogue, or README
claims excluded). Times UTC.

## B1 — METR public evaluation data — PASS

- The pilot's input files were located via the pilot artefact's own
  provenance (`results/pilot_metr_v1_0.json` records the exact path
  and hash): the flagship workspace copies
  `goals/10-journal-papers-submitted-to-good-journals/hidden_files/flagship_work/data/metr/runs_v1_0.jsonl`
  (sha256 f489d11728909937dad99ba1ed2d7c40efe12a766891e67dbc7c2486a3311236,
  41,629 lines — hash matches the pilot artefact exactly) and
  `runs_v1_1.jsonl` (sha256 609f904f4b6ae32129388da89d036e00bac511ad94223d2be1e58fc2b45b55cd,
  24,008 lines). Both copied byte-identical into
  `results/census/data/metr/` (post-copy hashes verified equal).
  Note: the paths named in `code/ingest.py` (area `data/` tree) no
  longer exist on disk; the census adapter reads the census copies
  and the pilot-slice anchor (below) verifies equivalence on the
  pilot's own slice.
- Scope per EXPERIMENTS §7.1: task_source ∈ {HCAST, RE-Bench}, both
  files pooled; run_id de-duplication (identical re-listing counts
  once; conflicting re-listing excluded and listed in the ledger).
- **Count discrepancy, recorded plainly:** §7.1's feasibility count
  was 57,936 records from files totalling 72 MB at the
  `code/ingest.py` paths. Those files no longer exist. The surviving
  hash-pinned pair totals 39 MB and yields 39,363 post-dedup
  HCAST+RE-Bench records over the same 52 agents. The census
  proceeds on the surviving corpus (its v1_0 hash is the pilot's
  own recorded input hash, and the pilot-slice anchor below is the
  operative equivalence check); the difference is an H-DATA note,
  not silently absorbed.
- Pilot-slice anchor (§3.3): the census run table, restricted to
  the HCAST v1_0 slice, must reproduce the machine-generated pilot
  artefact `results/pilot_metr_v1_0.json` (grok_4 components, the
  three-way anchor means, the paired-agent task-diff variance,
  continuous components) — result in `ingest_ledger.json`.
  **Recorded discrepancy:** EXPERIMENTS.md §7.1's printed slice
  table (13 agents; grok_4 T=162, E1 0.0132, ρ 0.643; pooled
  ρ 0.305295) is NOT reproducible from that artefact (grok_4:
  T=97, E1 0.19701, ρ 0.24486). The census anchors on the artefact,
  per §9.4's rule that numbers come from the run's own output; the
  §7.1 table is treated as an uncorrected reporting error in the
  frozen document and is flagged here and in the census results,
  not silently used.

## B3 — τ-bench — PASS

- Source: the official release `github.com/sierra-research/tau-bench`,
  `historical_trajectories/` (MIT licence, verified from the repo
  LICENSE file). Four trajectory files downloaded 2026-11-01
  (~04:0x UTC) and copied into `results/census/data/tau_bench/`
  (sha256 in the ingest ledger):
  gpt-4o retail 460 runs (115 tasks × 4 trials), gpt-4o airline 200
  (50 × 4), claude-3.5-sonnet ("sonnet-35-new") retail 920 (115 × 8),
  airline 400 (50 × 8); 1,980 outcomes total. Rewards are binary
  (0.0/1.0 only); trial indices consistent per task; every cell has
  n ≥ 2 (100% of cells and runs). These are the runs behind the
  τ-bench paper's pass^k reporting. Grading is the benchmark's
  programmatic state check → E3 = 0 by construction (§4.2), stated
  not estimated.

## B4 — Bjarnason et al. (2026) — PASS (fallback anchor corpus)

- Established at the Stage 5 return (STATE.md): reproduced
  byte-identical, deviation 0.0; 12 configurations × 10 runs ×
  SWE-bench Verified (500 tasks/config), CC-BY-4.0. The census
  adapter re-downloads the same 120 per-run harness eval JSONs
  (selection rule imported from `code/bjarnason_fallback.py`,
  revision 5db0c4b69382d160a313d7ceaded915398c63e13) into
  `results/census/data/bjarnason/` and cross-checks per-config mean
  rates against `results/p2_a1_fallback_run2.json` (ledger).

## B2 — HAL (generalist + CORE-Bench hard) — FAIL at ingest verification

- `huggingface.co/datasets/agentevals/hal_traces` probed 2026-11-01:
  dataset page HTTP 401; file-tree API
  (`/api/datasets/agentevals/hal_traces/tree/main`) HTTP 401 with
  body "Invalid username or password."; a file-resolve HEAD request
  for a frozen-listing archive
  (`corebench_hard_hal_generalist_agent_1747201030_UPLOAD.zip`)
  HTTP 401. The HAL website itself (hal.cs.princeton.edu) loads and
  describes the same download route.
- Consequence: the outcome-bearing files can be neither enumerated
  nor parsed at the artefact from this environment, so §5.1 data
  presence fails. Independently, the frozen files are encrypted .zip
  archives of 0.3–3.5 GB each (flagship population, EXPERIMENTS
  §7.2), which §11.1's no-large-download rule forbids fetching in
  any case. No account was created (the programme creates none).
- Recorded as an H-DATA finding: B2 does not enter the census set.

## B6 — HAL (CORE-Bench) — FAIL at ingest verification

- Same access failure as B2 (the CORE-Bench traces live in the same
  401-returning dataset). §7.2 froze B6's status as "Repeat
  structure: unverified — re-verified at census": that
  re-verification is impossible at the artefact at census time, so
  B6 cannot pass §5.1 and does not enter the census set.

## B5 — de la Rubia & Pafka (2026) — FAIL (selection legs)

- Corpus verified AT the artefact: `github.com/earino/identical-runs-different-results`
  (MIT licence). Tree enumerated via the GitHub API: 468 per-run
  `eval.json` artefacts under `code/study2|study3/<variant>/airline/<scaffold>/<model>/seed<k>/`
  = 36 pairings × 13 seeds; one sampled eval.json parsed (full run
  record with holdout scores). Data presence and licensing PASS.
- Failing legs (§5.1): (b) the recorded outcome is a continuous
  holdout AUC (`holdout_auc`, ≈0.72) — no binary outcome and no
  pre-stated pass/fail bar in the artefact, so any binarisation
  would be a judgement call; and estimability: `task/` contains
  exactly one task (`airline` — "the same machine-learning task",
  per the repo README), so the task population T = 1 and E1/E4 are
  not estimable from this corpus at any sample size of runs.
- B5 does not enter the census set.

## Census set

**{B1 (METR HCAST + RE-Bench), B3 (τ-bench), B4 (Bjarnason et al.
SWE-bench Verified configurations)}** — B = 3 independent benchmarks
(§5.2 minimum: 3). B4 is the fallback-anchor corpus, labelled as
such wherever the set is described (§7.2). Grader facet: no corpus
in the set re-grades frozen trajectories; E3 = 0 by construction
in all three, stated per §4.2.
