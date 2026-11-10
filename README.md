# Replication deposit — "What a Benchmark Score Cannot Say"

Replication package for: Ranadhir Ghosh, *What a Benchmark Score Cannot
Say: Variance Components and Detectability Limits on Three Agent
Benchmarks* (manuscript in this folder: `manuscript.tex`; the compiled
PDF is in the programme's submission package).

**Public location:**
https://github.com/ranadhir19/agent-benchmark-metrology-census

**Verify the deposit:** `python3 validate.py` (stdlib only, at this
folder's root) recomputes the headline census numbers — pooled Arm A /
Arm B ρ, intervals, falsifier verdicts under both the BCa and the frozen
percentile intervals, the §6.5 discordance, the 297-fit tally, the
published-gap audit counts, and the pre-registration hash chain — from
the deposited artefacts alone, and exits 0 only if all checks pass.

## Contents

- `PREREGISTRATION.sha256` — the append-only hash chain for the frozen
  pre-registration (verify with `sha256sum -c PREREGISTRATION.sha256`
  against the frozen texts included here).
- `EXPERIMENTS.md` — the bounded-pilot pre-registration (frozen
  2026-10-30) and its execution addenda.
- `EXPERIMENTS_ADDENDUM_STAGE7.md` — the full Stage 7 census
  pre-registration (frozen 2026-10-31T16:00:07Z), including estimands
  E1–E6, the falsifier, the ingest-verification rule, the co-primary
  arm specification, and the §6.5 disagreement rule.
- `SOLUTION_DESIGN.md` — the Stage 5 design the registration carries.
- `code/` — the census pipeline (`components.py`, `mde.py`, `glmm.py`,
  `census.py`, `census_adapters.py`, `ingest.py`, `pilot.py`,
  `synth.py`, `bjarnason_fallback.py`), the model-stack lockfile
  (`requirements-lock.txt`), and `validate.py`, the area harness
  (18/18 PASS at census close, 2026-11-02).
- `results/` — the census artefacts from which every table in the
  manuscript is drawn: pooled/per-agent Arm A and Arm B JSON
  (`arm_a_B{1,3,4}.json`, `arm_b_B{1,3,4}.json`), design and audit
  tables (`tables_B{1,3,4}.json`), the ingest ledger
  (`ingest_ledger.json`, `INGEST_EVIDENCE.md`), the final census report
  (`CENSUS_RESULTS.md`), and the stage record (`STAGE7_RECORD.md`).
- `results/fits/` — all 297 frozen Arm B fit records (status,
  diagnostics, posterior summaries). **Deposit-copy note:** raw
  posterior draw arrays are omitted from these copies to keep the
  deposit small; every reported summary statistic, interval, and
  diagnostic is preserved. The complete records are retained in the
  author's archive and available on request.

## Data

The run-level corpora are public research artefacts and are not
redistributed here: METR's public run-level records; the τ-bench
official release (MIT); Bjarnason et al.'s repeated-run release
(CC-BY-4.0; Hugging Face `ASSERT-KTH/agentic-evals-artifacts`, pinned
revision `5db0c4b69382d160a313d7ceaded915398c63e13`). The HAL corpora
(B2/B6) could not be read at census time (HTTP 401); their exclusion is
documented in the ingest ledger.

## Environment note

The pre-census lockfile pins PyMC 5.16.2; the census executed under
PyMC 5.25.1 / PyTensor 2.31.7 / NumPy 2.0.2 / SciPy 1.15.3 after host
rebuilds. No frozen setting changed; the drift is recorded in
`results/CENSUS_RESULTS.md` and the run record.
