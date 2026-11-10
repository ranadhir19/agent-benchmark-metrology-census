"""Stage 7 census driver — Area 1 (agent-benchmark metrology).

Implements the frozen design: EXPERIMENTS.md Part 3 / SS5 and
EXPERIMENTS_ADDENDUM_STAGE7.md SS6 (co-primary Arm B). Stages are
idempotent and checkpointed under results/census/:

  ingest  canonical run tables + SS5.1 verification + SS3.3 anchors
  arm-a   moment components, pooled endpoints, bootstrap/jackknife
  arm-b   GLMM fits (one checkpoint file per fit), pooled endpoints
  tables  SS3.4 design tables, SS3.5 gap audit, SS4.3 falsifier rows
  report  CENSUS_RESULTS.md assembled from the artefacts

Frozen sampler/estimator settings are imported from code/glmm.py and
code/components.py unchanged. Census RNG: numpy SeedSequence(20261031)
spawned per benchmark/statistic (SS6.1); seeds recorded in artefacts.
"""
import collections
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
from scipy import stats as _stats

HERE = os.path.dirname(os.path.abspath(__file__))
AREA = os.path.dirname(HERE)
sys.path.insert(0, AREA)
CENSUS = os.path.join(AREA, "results", "census")
DATA = os.path.join(CENSUS, "data")
FITS = os.path.join(CENSUS, "fits")
CENSUS_SEED = 20261031
BENCHES = ("B1", "B3", "B4")


def _atomic_json(obj, path):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def _progress(stage, **kw):
    p = os.path.join(CENSUS, "progress.json")
    cur = {}
    if os.path.exists(p):
        with open(p) as f:
            cur = json.load(f)
    cur[stage] = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  **kw}
    _atomic_json(cur, p)
    print(f"[progress] {stage}: {kw}", flush=True)


def load_table(bench):
    path = os.path.join(DATA, f"{bench}_run_table.jsonl")
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def agent_cells(records, agent):
    """Return (tasks, n, k, x) for one agent: tasks sorted; n/k int
    arrays over ALL cells; x = per-cell list of y_cont values (or None
    entries) aligned with tasks."""
    mine = [r for r in records if r["agent"] == agent]
    tasks = sorted({r["task"] for r in mine})
    by_task = {t: [] for t in tasks}
    for r in mine:
        by_task[r["task"]].append(r)
    n = np.array([len(by_task[t]) for t in tasks], dtype=int)
    k = np.array([sum(r["y_bin"] for r in by_task[t]) for t in tasks],
                 dtype=int)
    x = []
    for t in tasks:
        vals = [r["y_cont"] for r in by_task[t]]
        x.append(None if any(v is None for v in vals)
                 else np.array(vals, dtype=float))
    return tasks, n, k, x


def _ge2(n, *arrs):
    m = n >= 2
    return (a[m] for a in arrs)


# ------------------------------------------------------------ ingest
def stage_ingest():
    from code import census_adapters as ad
    from code import components

    ledger = {"census_seed": CENSUS_SEED, "benchmarks": {}}
    builders = {"B1": ad.build_b1, "B3": ad.build_b3, "B4": ad.build_b4}
    tables = {}
    for bench, build in builders.items():
        records, meta = build()
        tables[bench] = records
        ledger["benchmarks"][bench] = meta
        print(f"[ingest] {bench}: {meta['n_records']} records, "
              f"{meta['n_agents']} agents, {meta['n_tasks']} tasks, "
              f"share cells>=2 {meta['share_cells_ge2']:.4f}", flush=True)

    anchors = {}

    # SS3.3 anchor, B1: pilot-artefact reproduction. The machine-
    # generated pilot artefact (results/pilot_metr_v1_0.json) is the
    # ground truth of the pilot computation: grok_4 components on the
    # HCAST v1_0 slice, three-way anchor means, the paired-agent
    # components and task-diff variance, continuous components.
    # NOTE (recorded discrepancy): EXPERIMENTS.md SS7.1's printed
    # slice table (13 agents, grok_4 T=162, pooled rho 0.305295) is
    # NOT reproducible from that artefact (grok_4: T=97,
    # sigma2_task 0.19701, rho 0.24486); the census anchors on the
    # artefact and reports the discrepancy, per SS9.4.
    with open(os.path.join(AREA, "results", "pilot_metr_v1_0.json")) as f:
        pilot_art = json.load(f)
    slice_records = [r for r in tables["B1"]
                     if r["task_source"] == "HCAST"
                     and r["source_file"] == "runs_v1_0.jsonl"]
    pa = pilot_art["pilot_agent"]
    _t, n, k, x = agent_cells(slice_records, pa)
    m2 = n >= 2
    est_slice = components.estimate_components(n[m2], k[m2])
    cells_pa = collections.Counter(r["task"] for r in slice_records
                                   if r["agent"] == pa)
    ge2_recs = [r for r in slice_records
                if r["agent"] == pa and cells_pa[r["task"]] >= 2]
    pooled_mean = float(np.mean([r["y_bin"] for r in ge2_recs]))
    per_task = {}
    for r in ge2_recs:
        per_task.setdefault(r["task"], []).append(r["y_bin"])
    eq_task_mean = float(np.mean([np.mean(v)
                                  for v in per_task.values()]))
    xc = [x[i] for i in range(len(n)) if m2[i] and x[i] is not None]
    est_cont = components.estimate_components_continuous(xc)
    pb = pilot_art["paired_agent"]
    _t1, n1, k1, _x1 = agent_cells(slice_records, pa)
    _t2, n2v, k2v, _x2 = agent_cells(slice_records, pb)
    shared = sorted(set(_t1) & set(_t2))
    i1 = {t: j for j, t in enumerate(_t1)}
    i2 = {t: j for j, t in enumerate(_t2)}
    nn1 = np.array([n1[i1[t]] for t in shared])
    kk1 = np.array([k1[i1[t]] for t in shared])
    nn2 = np.array([n2v[i2[t]] for t in shared])
    kk2 = np.array([k2v[i2[t]] for t in shared])
    both = (nn1 >= 2) & (nn2 >= 2)
    pair_est = _paired_est(nn1[both], kk1[both], nn2[both], kk2[both])
    exp_c = pilot_art["components_binary"]
    anchors["B1_pilot_slice"] = {
        "pilot_agent": pa,
        "components": est_slice,
        "expected_components": exp_c,
        "abs_diff_components": {
            kk: abs(est_slice[kk] - exp_c[kk])
            for kk in ("sigma2_task", "sigma2_run", "rho")},
        "anchor_means": {"pooled_run_mean": pooled_mean,
                         "equal_task_mean": eq_task_mean},
        "expected_anchor_means": pilot_art["anchor"],
        "abs_diff_means": {
            "pooled_run_mean": abs(pooled_mean
                                   - pilot_art["anchor"]["pooled_run_mean"]),
            "equal_task_mean": abs(eq_task_mean
                                   - pilot_art["anchor"]["equal_task_mean"])},
        "continuous": est_cont,
        "expected_continuous": pilot_art["components_continuous_secondary"],
        "paired": {"agent": pb, "task_diff_var": pair_est["task_diff_var"],
                   "expected_task_diff_var":
                       pilot_art["paired_sigma2_task_diff"],
                   "abs_diff": abs(pair_est["task_diff_var"]
                                   - pilot_art["paired_sigma2_task_diff"])},
        "registration_table_discrepancy": (
            "EXPERIMENTS.md SS7.1's printed slice table is not "
            "reproducible from results/pilot_metr_v1_0.json "
            "(grok_4 T=162/E1 0.0132/rho 0.643 there vs T=97/E1 "
            "0.19701/rho 0.24486 in the artefact). The census anchors "
            "on the artefact (SS9.4)."),
    }
    print(f"[anchor] B1 pilot slice: max component abs diff = "
          f"{max(anchors['B1_pilot_slice']['abs_diff_components'].values()):.3e}; "
          f"paired diff abs diff = "
          f"{anchors['B1_pilot_slice']['paired']['abs_diff']:.3e}", flush=True)

    # SS3.3 two-way means + count cross-checks, every benchmark.
    for bench, records in tables.items():
        two_way = {}
        by_agent = collections.defaultdict(list)
        for r in records:
            by_agent[r["agent"]].append(r)
        for a, rs in sorted(by_agent.items()):
            cells = collections.Counter(r["task"] for r in rs)
            pooled_mean = float(np.mean([r["y_bin"] for r in rs]))
            ge2 = [r for r in rs if cells[r["task"]] >= 2]
            if ge2:
                per_task = {}
                for r in ge2:
                    per_task.setdefault(r["task"], []).append(r["y_bin"])
                eq_task_mean = float(np.mean(
                    [np.mean(v) for v in per_task.values()]))
            else:
                eq_task_mean = None
            two_way[a] = {"pooled_run_mean_all_cells": pooled_mean,
                          "equal_task_mean_ge2_cells": eq_task_mean,
                          "n_records": len(rs)}
        anchors[f"{bench}_two_way"] = two_way
        # independent count: sum over cells of cell size
        cells = collections.Counter((r["agent"], r["task"]) for r in records)
        assert sum(cells.values()) == len(records)
        anchors[f"{bench}_count_crosscheck"] = {
            "sum_cell_n": int(sum(cells.values())),
            "n_records": len(records), "match": True}
    # B4: per-config means vs the frozen fallback anchor artefact.
    fb_path = os.path.join(AREA, "results", "p2_a1_fallback_run2.json")
    with open(fb_path) as f:
        fb = json.load(f)
    b4_meta = ledger["benchmarks"]["B4"]
    b4_check = {}
    for cfg in fb["configs"]:
        key = (f"{cfg['scaffold']}|{cfg['model']}|temp={cfg['temperature']:g}")
        mine = b4_meta["configs"][key]["mean_rate_pct"]
        b4_check[key] = {"census_mean_pct": mine,
                         "fallback_mean_pct": cfg["mean_points"],
                         "abs_diff": abs(mine - cfg["mean_points"])}
    anchors["B4_fallback_anchor"] = b4_check
    print(f"[anchor] B4 max mean diff vs fallback artefact: "
          f"{max(v['abs_diff'] for v in b4_check.values()):.3e}", flush=True)

    ledger["anchors"] = anchors
    # Provenance note (H-DATA): EXPERIMENTS.md SS7.1 records a
    # census-feasibility count of 57,936 HCAST+RE-Bench records from
    # "the two local data files" (72 MB) at code/ingest.py paths.
    # Those files no longer exist on disk. The census corpus is the
    # surviving hash-pinned pair (39 MB) whose v1_0 hash matches the
    # pilot artefact's recorded input exactly; the pilot-slice anchor
    # above is the operative equivalence check. The count difference
    # is recorded, not reconciled away.
    ledger["benchmarks"]["B1"]["provenance_note"] = (
        "Census corpus = flagship-workspace copies of runs_v1_0.jsonl "
        "+ runs_v1_1.jsonl (hashes in files[]), NOT the vanished "
        "code/ingest.py data tree behind the SS7.1 count of 57,936. "
        "Post-dedup census records: see n_records_after_filter_dedup.")
    # Ingest-verification FAILs (SS5.1), verified at the artefacts on
    # 2026-11-01 (evidence in results/census/INGEST_EVIDENCE.md):
    ledger["benchmarks"]["B2"] = {
        "verdict": "FAIL",
        "fail_reason": "data presence cannot be verified at the "
                       "artefact: huggingface.co/datasets/agentevals/"
                       "hal_traces returns HTTP 401 (dataset page, "
                       "file tree, and file resolve all probed "
                       "2026-11-01); the frozen outcome-bearing files "
                       "(encrypted .zip archives, 0.3-3.5 GB each per "
                       "the flagship's frozen listing) can neither be "
                       "enumerated nor parsed, and SS11.1 forbids "
                       "downloads of that size in any case."}
    ledger["benchmarks"]["B6"] = {
        "verdict": "FAIL",
        "fail_reason": "same HAL access failure as B2 (HTTP 401 on "
                       "the agentevals/hal_traces dataset at census "
                       "time): CORE-Bench's repeat structure, frozen "
                       "as 're-verified at census' (PACKET_INTAKE "
                       "S3.11), cannot be re-verified at the artefact; "
                       "the benchmark therefore cannot pass SS5.1 "
                       "ingest verification in this census."}
    ledger["benchmarks"]["B5"] = {
        "verdict": "FAIL",
        "fail_reason": "corpus verified present and MIT-licensed at "
                       "github.com/earino/identical-runs-different-"
                       "results (468 per-run eval.json artefacts, 36 "
                       "pairings x 13 seeds), but it fails the SS5.1 "
                       "selection legs: (b) the outcome is a "
                       "continuous holdout AUC with no pre-stated "
                       "binary bar, so binarisation would require a "
                       "judgement call; and estimability: the corpus "
                       "contains exactly ONE task (task/airline), so "
                       "the task-sampling component E1 and the "
                       "falsifier ratio E4 have no task population to "
                       "estimate over."}
    _atomic_json(ledger, os.path.join(CENSUS, "ingest_ledger.json"))
    _progress("ingest", benchmarks=list(tables))
    return ledger


# ------------------------------------------------------------- arm-a
def _pooled_from_agent_estimates(per_agent):
    """SS3.1 E4 pooled construction, via the validated
    code/components.py pooled_rho (equal-weight means over agents;
    rho = ratio of pooled means). Keys normalised to sigma2_*/rho."""
    from code import components
    p = components.pooled_rho(list(per_agent.values()))
    return {"sigma2_task": p["sigma2_task_pooled"],
            "sigma2_run": p["sigma2_run_pooled"],
            "rho": p["rho_pooled"],
            "n_agents": len(per_agent)}


def _paired_est(n1, k1, n2, k2):
    """Paired task-difference components on shared >=2 cells, built
    from the validated primitives (pilot.py's construction)."""
    from code import components
    ea = components.estimate_components(n1, k1)
    eb = components.estimate_components(n2, k2)
    tdv = components.paired_task_diff_variance(n1, k1, n2, k2)
    return {"task_diff_var": float(tdv),
            "run_var_1": ea["sigma2_run"], "run_var_2": eb["sigma2_run"],
            "task_term_paired": float(tdv)}


def _kind_cells(agents_data, kind):
    """Per agent: list of (task, n, k, x) restricted to >=2 cells (and,
    for the continuous kind, to cells with a recorded y_cont)."""
    out = {}
    for agent, (tasks, n, k, x) in agents_data.items():
        cells = []
        for i, t in enumerate(tasks):
            if n[i] < 2:
                continue
            if kind == "continuous" and x[i] is None:
                continue
            cells.append((t, int(n[i]), int(k[i]), x[i]))
        out[agent] = cells
    return out


def _estimate_from_cells(cells, kind):
    from code import components
    if kind == "binary":
        nn = np.array([c[1] for c in cells], dtype=int)
        kk = np.array([c[2] for c in cells], dtype=int)
        return components.estimate_components(nn, kk)
    xx = [c[3] for c in cells]
    return components.estimate_components_continuous(xx)


def _fast_cont_estimate(m, w, n, counts):
    """Multiplicity-weighted form of
    code/components.estimate_components_continuous, for bootstrap /
    jackknife resamples: cells enter with integer multiplicities.
    Equivalence verified 2026-11-01 on 240 random resamples x 6 B1
    agents: max abs diff 1.9e-16 (float rounding only). The observed
    (non-resample) estimates always use the validated estimator."""
    c = counts.astype(float)
    C = c.sum()
    if C < 2:
        return None
    s2r = float(np.sum(c * n * w) / np.sum(c * n))
    mm = np.sum(c * m) / C
    var_means = float((np.sum(c * m * m) - C * mm * mm) / (C - 1))
    s2t = max(0.0, var_means - float(np.sum(c * (w / n)) / C))
    return {"sigma2_task": s2t, "sigma2_run": s2r,
            "rho": s2r / s2t if s2t > 0 else float("nan")}


def _cont_agent_arrays(agents_data):
    """Per agent: (cell_tasks, m, w, n) over >=2 cells with y_cont."""
    out = {}
    for agent, (tasks, n, k, x) in agents_data.items():
        ct, mm, ww, nn = [], [], [], []
        for i, t in enumerate(tasks):
            if n[i] >= 2 and x[i] is not None:
                v = np.asarray(x[i], dtype=float)
                ct.append(t)
                mm.append(float(np.mean(v)))
                ww.append(float(np.var(v, ddof=1)))
                nn.append(float(len(v)))
        if len(ct) >= 2:
            out[agent] = (ct, np.array(mm), np.array(ww), np.array(nn))
    return out


def _bootstrap_pooled(records, agents_data, kind, seed, B=2000):
    """Cluster bootstrap over tasks (SS6.1: tasks resampled with their
    cells; the same task resample applies to every agent). Returns the
    replicate arrays for the pooled statistic of the given kind
    ('binary' or 'continuous')."""
    rng = np.random.default_rng(seed)
    reps = {"sigma2_task": [], "sigma2_run": [], "rho": []}
    n_dropped_agents = []
    if kind == "continuous":
        carr = _cont_agent_arrays(agents_data)
        union_tasks = sorted({t for (ct, _m, _w, _n) in carr.values()
                              for t in ct})
        t_index = {t: i for i, t in enumerate(union_tasks)}
        idx = {a: np.array([t_index[t] for t in ct])
               for a, (ct, _m, _w, _n) in carr.items()}
        for _ in range(B):
            draw = rng.integers(0, len(union_tasks),
                                size=len(union_tasks))
            counts = np.bincount(draw, minlength=len(union_tasks))
            per_agent = {}
            dropped = 0
            for a, (ct, m, w, n) in carr.items():
                est = _fast_cont_estimate(m, w, n, counts[idx[a]])
                if est is None:
                    dropped += 1
                else:
                    per_agent[a] = est
            if not per_agent:
                continue
            pooled = _pooled_from_agent_estimates(per_agent)
            reps["sigma2_task"].append(pooled["sigma2_task"])
            reps["sigma2_run"].append(pooled["sigma2_run"])
            reps["rho"].append(pooled["rho"])
            n_dropped_agents.append(dropped)
        return {kk: np.array(v) for kk, v in reps.items()}, \
            n_dropped_agents
    per_agent_cells = _kind_cells(agents_data, kind)
    union_tasks = sorted({c[0] for cells in per_agent_cells.values()
                          for c in cells})
    t_index = {t: i for i, t in enumerate(union_tasks)}
    for _ in range(B):
        draw = rng.integers(0, len(union_tasks), size=len(union_tasks))
        counts = np.bincount(draw, minlength=len(union_tasks))
        per_agent = {}
        dropped = 0
        for agent, cells in per_agent_cells.items():
            resampled = []
            for c in cells:
                resampled.extend([c] * int(counts[t_index[c[0]]]))
            if len(resampled) >= 2:
                per_agent[agent] = _estimate_from_cells(resampled, kind)
            else:
                dropped += 1
        if not per_agent:
            continue
        pooled = _pooled_from_agent_estimates(per_agent)
        reps["sigma2_task"].append(pooled["sigma2_task"])
        reps["sigma2_run"].append(pooled["sigma2_run"])
        reps["rho"].append(pooled["rho"])
        n_dropped_agents.append(dropped)
    return {kk: np.array(v) for kk, v in reps.items()}, n_dropped_agents


def _jackknife_pooled(records, agents_data, kind):
    """Leave-one-task-out values of the pooled statistic over the
    union task set (tasks removed from every agent at once)."""
    out = {"sigma2_task": [], "sigma2_run": [], "rho": []}
    if kind == "continuous":
        carr = _cont_agent_arrays(agents_data)
        union_tasks = sorted({t for (ct, _m, _w, _n) in carr.values()
                              for t in ct})
        out["tasks"] = union_tasks
        pos = {a: {t: j for j, t in enumerate(ct)}
               for a, (ct, _m, _w, _n) in carr.items()}
        for drop in union_tasks:
            per_agent = {}
            for a, (ct, m, w, n) in carr.items():
                counts = np.ones(len(ct))
                if drop in pos[a]:
                    counts[pos[a][drop]] = 0.0
                est = _fast_cont_estimate(m, w, n, counts)
                if est is not None:
                    per_agent[a] = est
            if per_agent:
                pooled = _pooled_from_agent_estimates(per_agent)
                out["sigma2_task"].append(pooled["sigma2_task"])
                out["sigma2_run"].append(pooled["sigma2_run"])
                out["rho"].append(pooled["rho"])
            else:
                out["sigma2_task"].append(float("nan"))
                out["sigma2_run"].append(float("nan"))
                out["rho"].append(float("nan"))
        return out
    per_agent_cells = _kind_cells(agents_data, kind)
    union_tasks = sorted({c[0] for cells in per_agent_cells.values()
                          for c in cells})
    out["tasks"] = union_tasks
    for drop in union_tasks:
        per_agent = {}
        for agent, cells in per_agent_cells.items():
            kept = [c for c in cells if c[0] != drop]
            if len(kept) >= 2:
                per_agent[agent] = _estimate_from_cells(kept, kind)
        if per_agent:
            pooled = _pooled_from_agent_estimates(per_agent)
            out["sigma2_task"].append(pooled["sigma2_task"])
            out["sigma2_run"].append(pooled["sigma2_run"])
            out["rho"].append(pooled["rho"])
        else:
            out["sigma2_task"].append(float("nan"))
            out["sigma2_run"].append(float("nan"))
            out["rho"].append(float("nan"))
    return out


def _bca_interval(theta_hat, boot, jack_vals):
    boot = np.asarray(boot, dtype=float)
    boot = boot[np.isfinite(boot)]
    jack = np.asarray([v for v in jack_vals if np.isfinite(v)], dtype=float)
    pct = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))
    if len(boot) < 100 or len(jack) < 10 or np.all(boot == boot[0]):
        return {"percentile": pct, "bca": pct, "note": "degenerate; "
                "percentile reported for both"}
    z0 = _stats.norm.ppf(np.mean(boot < theta_hat))
    jm = np.mean(jack)
    num = np.sum((jm - jack) ** 3)
    den = 6.0 * (np.sum((jm - jack) ** 2) ** 1.5)
    a = num / den if den != 0 else 0.0
    z = _stats.norm.ppf(0.975)
    a1 = _stats.norm.cdf(z0 + (z0 - z) / (1 - a * (z0 - z)))
    a2 = _stats.norm.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
    bca = (float(np.percentile(boot, 100 * a1)),
           float(np.percentile(boot, 100 * a2)))
    return {"percentile": pct, "bca": bca,
            "z0": float(z0), "accel": float(a), "n_boot": int(len(boot))}


def stage_arm_a():
    from code import components
    ss = np.random.SeedSequence(CENSUS_SEED)
    bench_seeds = {b: int(s.generate_state(1)[0])
                   for b, s in zip(BENCHES, ss.spawn(len(BENCHES)))}
    for bench in BENCHES:
        out_path = os.path.join(CENSUS, f"arm_a_{bench}.json")
        prior_art = {}
        if os.path.exists(out_path):
            with open(out_path) as f:
                prior_art = json.load(f)
            if "bootstrap_binary" in prior_art and (
                    prior_art.get("pooled_continuous") is None
                    or "bootstrap_continuous" in prior_art):
                print(f"[arm-a] {bench}: artefact complete, skipping",
                      flush=True)
                continue
            print(f"[arm-a] {bench}: resuming from partial artefact",
                  flush=True)
        records = load_table(bench)
        agents = sorted({r["agent"] for r in records})
        agents_data = {a: agent_cells(records, a) for a in agents}
        per_agent_bin, per_agent_cont = {}, {}
        excluded = {}
        for a in agents:
            tasks, n, k, x = agents_data[a]
            m = n >= 2
            if m.sum() >= 2:
                per_agent_bin[a] = components.estimate_components(
                    n[m], k[m])
            else:
                excluded[a] = int(m.sum())
            xc = [(n[i], x[i]) for i in range(len(tasks))
                  if m[i] and x[i] is not None]
            if len(xc) >= 2:
                per_agent_cont[a] = \
                    components.estimate_components_continuous(
                        [c[1] for c in xc])
        pooled_bin = _pooled_from_agent_estimates(per_agent_bin)
        pooled_cont = (_pooled_from_agent_estimates(per_agent_cont)
                       if per_agent_cont else None)

        # paired task-difference components, all unordered pairs
        pairs = {}
        est_by_agent = {}
        for a in agents:
            tasks, n, k, _x = agents_data[a]
            est_by_agent[a] = (tasks, n, k)
        for i, a1 in enumerate(agents):
            for a2 in agents[i + 1:]:
                t1, n1, k1 = est_by_agent[a1]
                t2, n2, k2 = est_by_agent[a2]
                shared = sorted(set(t1) & set(t2))
                if len(shared) < 2:
                    continue
                i1 = {t: j for j, t in enumerate(t1)}
                i2 = {t: j for j, t in enumerate(t2)}
                nn1 = np.array([n1[i1[t]] for t in shared])
                kk1 = np.array([k1[i1[t]] for t in shared])
                nn2 = np.array([n2[i2[t]] for t in shared])
                kk2 = np.array([k2[i2[t]] for t in shared])
                both = (nn1 >= 2) & (nn2 >= 2)
                if both.sum() < 2:
                    continue
                est = _paired_est(nn1[both], kk1[both],
                                  nn2[both], kk2[both])
                est["n_shared_tasks_ge2"] = int(both.sum())
                est["runs_in_shared_cells"] = int(nn1[both].sum()
                                                  + nn2[both].sum())
                pairs[f"{a1} || {a2}"] = est
        # headline pair: most shared >=2 tasks; ties: most runs; name order
        headline = None
        for key in sorted(pairs):
            e = pairs[key]
            score = (e["n_shared_tasks_ge2"], e["runs_in_shared_cells"])
            if headline is None or score > headline[1]:
                headline = (key, score)
        art = {
            "benchmark": bench,
            "per_agent_binary": per_agent_bin,
            "per_agent_continuous": per_agent_cont,
            "pooled_binary": pooled_bin,
            "pooled_continuous": pooled_cont,
            "pairs": pairs,
            "headline_pair": ({"pair": headline[0],
                               "n_shared_tasks_ge2": headline[1][0],
                               "runs_in_shared_cells": headline[1][1]}
                              if headline else None),
            "bootstrap_seed": bench_seeds[bench],
            "agents_excluded_fewer_than_2_repeated_cells": excluded,
        }
        # bootstrap + jackknife for pooled endpoints (binary; cont if
        # any). Each kind is checkpointed to disk as it completes, so
        # a host kill loses at most the in-flight kind.
        for kind, pooled, store in (
                ("binary", pooled_bin, "binary"),
                ("continuous", pooled_cont, "continuous")):
            if pooled is None:
                continue
            if f"bootstrap_{store}" in prior_art:
                art[f"bootstrap_{store}"] = prior_art[f"bootstrap_{store}"]
                art[f"jackknife_{store}"] = prior_art[f"jackknife_{store}"]
                print(f"[arm-a] {bench} {store}: carried over from "
                      f"partial artefact", flush=True)
                continue
            boot, dropped = _bootstrap_pooled(
                records, agents_data, kind, bench_seeds[bench])
            jack = _jackknife_pooled(records, agents_data, kind)
            iv = {}
            for comp in ("sigma2_task", "sigma2_run", "rho"):
                iv[comp] = _bca_interval(pooled[comp], boot[comp],
                                         jack[comp])
            art[f"bootstrap_{store}"] = {
                "n_replicates": int(len(boot["rho"])),
                "mean_dropped_agents_per_replicate":
                    float(np.mean(dropped)) if dropped else 0.0,
                "intervals": iv,
                "replicate_quantiles": {
                    c: [float(np.percentile(boot[c], q))
                        for q in (2.5, 50, 97.5)]
                    for c in ("sigma2_task", "sigma2_run", "rho")},
            }
            jv = np.array(jack["rho"], dtype=float)
            jv = jv[np.isfinite(jv)]
            n_j = len(jv)
            art[f"jackknife_{store}"] = {
                "n_tasks": n_j,
                "rho_mean": float(np.mean(jv)),
                "rho_se": float(np.sqrt((n_j - 1)
                                        * np.var(jv, ddof=0)))
                if n_j > 1 else None,
                "values_rho": [float(v) for v in jack["rho"]],
            }
            print(f"[arm-a] {bench} {store}: bootstrap done "
                  f"({len(boot['rho'])} reps)", flush=True)
            _atomic_json(art, out_path)
            _progress(f"arm_a_{bench}_{store}", done=True)
        _progress(f"arm_a_{bench}", pooled_rho_binary=pooled_bin["rho"],
                  headline_pair=art["headline_pair"])
    _progress("arm_a", done=True)


# ------------------------------------------------------------- arm-b
def _slug(agent):
    return "".join(c if c.isalnum() else "_" for c in agent)


def _jsonable(obj):
    """Deep-convert numpy types for JSON; tuples become lists."""
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return [_jsonable(v) for v in obj.tolist()]
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def _sanitise_fit(fit):
    """Strip per-draw arrays too large to checkpoint: keep summary
    mean/ci95 everywhere; keep draws_flat ONLY for E1_B / E2_B (the
    pooled-rho construction needs them)."""
    out = {}
    for key, val in fit.items():
        if isinstance(val, dict) and "mean" in val and "ci95" in val:
            s = {"mean": val["mean"], "ci95": list(val["ci95"])}
            if key in ("E1_B", "E2_B") and "draws_flat" in val:
                s["draws_flat"] = [float(v) for v in
                                   np.asarray(val["draws_flat"]).reshape(-1)]
            out[key] = s
        else:
            out[key] = _jsonable(val)
    return out


def _ladder_status(fit):
    """SS6.4 status vocabulary for a single fit dict."""
    if not fit["diagnostics"]["diagnostic_pass"]:
        return "FAILED"
    if fit.get("model_misfit_flag"):
        return "FLAGGED"
    return "PASS"


def _binary_fit_record(n, k, prior, singletons):
    """Run one binary fit under the SS6.4 ladder; returns the census
    record. Uses glmm.fit_binary_agent_checked where its signature
    reaches (no singletons); the singleton sensitivity mirrors the
    same ladder by hand (one remediation, identical settings)."""
    from code import glmm
    if not singletons:
        w = glmm.fit_binary_agent_checked(n, k, prior=prior)
        used = w[w["fit_used"]]
        return {"status": w["status"], "fit": _sanitise_fit(used),
                "remediation_used": w["fit_used"] == "remediation",
                "first_attempt_diagnostics":
                    _jsonable(w["primary"]["diagnostics"])
                    if w["fit_used"] == "remediation" else None}
    f1 = glmm.fit_binary_agent(n, k, prior=prior,
                               include_singletons=True)
    if f1["diagnostics"]["diagnostic_pass"]:
        return {"status": _ladder_status(f1), "fit": _sanitise_fit(f1),
                "remediation_used": False,
                "first_attempt_diagnostics": None}
    f2 = glmm.fit_binary_agent(
        n, k, prior=prior, include_singletons=True,
        target_accept=glmm.REMEDIATION_TARGET_ACCEPT,
        tune=glmm.REMEDIATION_TUNE)
    st = _ladder_status(f2)
    if st != "FAILED":
        st = "REMEDIATED_PASS" if st == "PASS" else st
    return {"status": st, "fit": _sanitise_fit(f2),
            "remediation_used": True,
            "first_attempt_diagnostics": _jsonable(f1["diagnostics"])}


def _continuous_fit_record(xx, score_range, prior):
    """Continuous fit under the same SS6.4 ladder (diagnostics only;
    the continuous model carries no PPC misfit flag in glmm)."""
    from code import glmm
    f1 = glmm.fit_continuous_agent(xx, score_range=score_range,
                                   prior=prior)
    if f1["diagnostics"]["diagnostic_pass"]:
        return {"status": "PASS", "fit": _sanitise_fit(f1),
                "remediation_used": False,
                "first_attempt_diagnostics": None}
    f2 = glmm.fit_continuous_agent(
        xx, score_range=score_range, prior=prior,
        target_accept=glmm.REMEDIATION_TARGET_ACCEPT,
        tune=glmm.REMEDIATION_TUNE)
    st = "REMEDIATED_PASS" if f2["diagnostics"]["diagnostic_pass"] \
        else "FAILED"
    return {"status": st, "fit": _sanitise_fit(f2),
            "remediation_used": True,
            "first_attempt_diagnostics": _jsonable(f1["diagnostics"])}


def stage_arm_b(only_bench=None):
    for bench in BENCHES:
        if only_bench and bench != only_bench:
            continue
        records = load_table(bench)
        agents = sorted({r["agent"] for r in records})
        n_fits = 0
        for a in agents:
            tasks, n, k, x = agent_cells(records, a)
            m = n >= 2
            if m.sum() < 2:
                continue
            jobs = [("binary_primary", "bin_primary"),
                    ("binary_sens_prior", "bin_sens"),
                    ("binary_singletons", "bin_singletons")]
            xc = [x[i] for i in range(len(tasks))
                  if m[i] and x[i] is not None]
            if len(xc) >= 2:
                jobs.append(("continuous_primary", "cont_primary"))
                jobs.append(("continuous_sens_prior", "cont_sens"))
            for kind, typ in jobs:
                fp = os.path.join(FITS, f"{bench}__{_slug(a)}__{kind}.json")
                if os.path.exists(fp):
                    continue
                t0 = time.time()
                if typ == "bin_primary":
                    rec = _binary_fit_record(n[m], k[m], "primary", False)
                elif typ == "bin_sens":
                    rec = _binary_fit_record(n[m], k[m], "sensitivity",
                                             False)
                elif typ == "bin_singletons":
                    rec = _binary_fit_record(n, k, "primary", True)
                elif typ == "cont_primary":
                    rec = _continuous_fit_record(xc, (0.0, 1.0), "primary")
                else:
                    rec = _continuous_fit_record(xc, (0.0, 1.0),
                                                 "sensitivity")
                rec["benchmark"] = bench
                rec["agent"] = a
                rec["fit_kind"] = kind
                rec["wall_seconds"] = time.time() - t0
                _atomic_json(rec, fp)
                n_fits += 1
                print(f"[arm-b] {bench} {a} {kind}: {rec['status']} "
                      f"({rec['wall_seconds']:.0f}s)", flush=True)
        _progress(f"arm_b_{bench}", new_fits=n_fits)
    _progress("arm_b", done=True)


def _load_fits(bench, kind):
    out = {}
    for fn in sorted(os.listdir(FITS)):
        if fn.startswith(f"{bench}__") and fn.endswith(f"__{kind}.json"):
            with open(os.path.join(FITS, fn)) as f:
                fit = json.load(f)
            out[fit["agent"]] = fit
    return out


def stage_arm_b_summary():
    from code import glmm

    def pooled_from_records(recs):
        """Pooled rho_B over non-FAILED fits (SS6.4: failed fits are
        reported, not pooled); returns (pooled_dict, failed_agents)."""
        ok = {a: r for a, r in recs.items() if r["status"] != "FAILED"}
        failed = sorted(a for a, r in recs.items()
                        if r["status"] == "FAILED")
        if not ok:
            return None, failed
        p = glmm.pooled_rho_binary([ok[a]["fit"] for a in sorted(ok)])
        return {"rho_B_mean": p["rho_B_mean"],
                "rho_B_ci95": [float(p["rho_B_ci95"][0]),
                               float(p["rho_B_ci95"][1])],
                "n_agents": p["n_agents"]}, failed

    for bench in BENCHES:
        out_path = os.path.join(CENSUS, f"arm_b_{bench}.json")
        prim = _load_fits(bench, "binary_primary")
        if not prim:
            print(f"[arm-b-summary] {bench}: no primary fits", flush=True)
            continue
        sens = _load_fits(bench, "binary_sens_prior")
        sing = _load_fits(bench, "binary_singletons")
        cprim = _load_fits(bench, "continuous_primary")
        pooled, failed = pooled_from_records(prim)
        art = {"benchmark": bench,
               "per_agent": {
                   a: {"E1_B": {"mean": r["fit"]["E1_B"]["mean"],
                                "ci95": r["fit"]["E1_B"]["ci95"]},
                       "E2_B": {"mean": r["fit"]["E2_B"]["mean"],
                                "ci95": r["fit"]["E2_B"]["ci95"]},
                       "status": r["status"],
                       "diagnostics": r["fit"]["diagnostics"],
                       "misfit": r["fit"].get("model_misfit_flag")}
                   for a, r in sorted(prim.items())},
               "pooled_binary": pooled,
               "failed_agents_primary": failed,
               "statuses": dict(collections.Counter(
                   r["status"] for r in prim.values())),
               "misfit_share_primary": float(np.mean(
                   [bool(r["fit"].get("model_misfit_flag"))
                    for r in prim.values()])),
               }
        if sens:
            ps, fs = pooled_from_records(sens)
            art["pooled_binary_sens_prior"] = ps
            art["failed_agents_sens_prior"] = fs
            if pooled and ps:
                art["prior_sensitivity"] = _jsonable(
                    glmm.prior_sensitivity_flag(pooled, ps))
        if sing:
            pg, fg = pooled_from_records(sing)
            art["pooled_binary_singletons"] = pg
            art["failed_agents_singletons"] = fg
        if cprim:
            art["per_agent_continuous"] = {
                a: {"E1_B": {"mean": r["fit"]["E1_B"]["mean"],
                             "ci95": r["fit"]["E1_B"]["ci95"]},
                    "E2_B": {"mean": r["fit"]["E2_B"]["mean"],
                             "ci95": r["fit"]["E2_B"]["ci95"]},
                    "status": r["status"]}
                for a, r in sorted(cprim.items())}
            ok = {a: r for a, r in cprim.items()
                  if r["status"] != "FAILED"}
            if ok:
                e1 = [ok[a]["fit"]["E1_B"]["draws_flat"]
                      for a in sorted(ok)]
                e2 = [ok[a]["fit"]["E2_B"]["draws_flat"]
                      for a in sorted(ok)]
                e1m = np.mean(np.vstack(e1), axis=0)
                e2m = np.mean(np.vstack(e2), axis=0)
                with np.errstate(divide="ignore", invalid="ignore"):
                    rho = np.where(e1m > 0, e2m / e1m, np.nan)
                art["pooled_continuous"] = {
                    "rho_B_mean": float(np.nanmean(rho)),
                    "rho_B_ci95": [float(np.nanpercentile(rho, 2.5)),
                                   float(np.nanpercentile(rho, 97.5))],
                    "n_agents": len(ok),
                    "note": "draw-by-draw pooled construction mirroring "
                            "glmm.pooled_rho_binary (no separate "
                            "continuous pooling helper exists in "
                            "code/glmm.py)."}
        _atomic_json(art, out_path)
        _progress(f"arm_b_summary_{bench}",
                  pooled_rho_B=(pooled or {}).get("rho_B_mean"))
    _progress("arm_b_summary", done=True)


# ------------------------------------------------------------ tables
def _design_rows(T, pair_est, pooled, arm_label):
    from code import mde as mde_mod
    from scipy import stats as _st
    run_sum = pair_est["run_var_sum"]
    task_term = pair_est["task_term_paired"]
    mult_t = float(_st.t.ppf(0.975, T - 1) + _st.t.ppf(0.80, T - 1))
    rows = {}
    for R in (1, 2, 4, 8):
        rows[f"R={R}"] = {
            "mde_normal": mde_mod.mde(T, R, run_sum, task_term),
            "mde_t": mde_mod.mde(T, R, run_sum, task_term, df=T - 1),
        }
    for delta in (0.10, 0.05, 0.02):
        rr_n = mde_mod.required_runs(delta, T, run_sum, task_term)
        rr_t = mde_mod.required_runs(delta, T, run_sum, task_term,
                                     mult=mult_t)
        entry = {"normal": rr_n, "t": rr_t}
        if rr_n is None:
            entry["required_tasks_at_R8_normal"] = \
                mde_mod.required_tasks(delta, 8, run_sum, task_term)
        if rr_t is None:
            entry["required_tasks_at_R8_t"] = \
                mde_mod.required_tasks(delta, 8, run_sum, task_term,
                                       mult=mult_t)
        rows[f"required_runs_delta={delta}"] = entry
    rows["pair_components"] = pair_est
    rows["arm"] = arm_label
    return rows


def _falsifier_row(point, interval, sens_values):
    """SS4.3 decision logic for one arm. interval = (lo, hi)."""
    lo, hi = interval
    sens_exit = any(not (0.0 < v < 1.0) for v in sens_values)
    if point < 0.30 or hi < 0.30:
        return "REFUTED"
    if point >= 0.30 and lo > 0.0 and hi < 1.0 and not sens_exit:
        return "SUPPORTED"
    return "INDETERMINATE"


def stage_tables():
    from code import mde as mde_mod
    audit_sources = None
    asrc = os.path.join(CENSUS, "audit_sources.json")
    if os.path.exists(asrc):
        with open(asrc) as f:
            audit_sources = json.load(f)
    for bench in BENCHES:
        with open(os.path.join(CENSUS, f"arm_a_{bench}.json")) as f:
            aa = json.load(f)
        ab = None
        ab_path = os.path.join(CENSUS, f"arm_b_{bench}.json")
        if os.path.exists(ab_path):
            with open(ab_path) as f:
                ab = json.load(f)
        art = {"benchmark": bench}
        hp = aa["headline_pair"]
        if hp:
            a1, a2 = hp["pair"].split(" || ")
            pe = aa["pairs"][hp["pair"]]
            T = pe["n_shared_tasks_ge2"]
            pair_est = {"task_diff_var": pe["task_diff_var"],
                        "run_var_sum": pe["run_var_1"] + pe["run_var_2"],
                        "task_term_paired": pe["task_diff_var"]}
            rows = _design_rows(T, pair_est, aa["pooled_binary"], "A")
            # actual-R row: mean runs per shared cell of the pair
            records = load_table(bench)
            cells = collections.Counter(
                (r["agent"], r["task"]) for r in records
                if r["agent"] in (a1, a2))
            shared_tasks = {t for (ag, t), n in cells.items()
                            if ag == a1 and cells.get((a2, t), 0) >= 2
                            and n >= 2}
            actual_R = float(np.mean(
                [cells[(a1, t)] for t in shared_tasks]
                + [cells[(a2, t)] for t in shared_tasks]))
            rows[f"R=actual({actual_R:.2f})"] = {
                "mde_normal": mde_mod.mde(T, actual_R,
                                          pair_est["run_var_sum"],
                                          pair_est["task_term_paired"]),
                "mde_t": mde_mod.mde(T, actual_R,
                                     pair_est["run_var_sum"],
                                     pair_est["task_term_paired"],
                                     df=T - 1),
            }
            art["design_table_arm_a"] = {
                "headline_pair": hp, "T_shared": T, "rows": rows}
            if ab:
                ea = ab["per_agent"][a1]
                eb = ab["per_agent"][a2]
                unb = {"task_diff_var": None,
                       "run_var_sum": ea["E2_B"]["mean"] + eb["E2_B"]["mean"],
                       "task_term_paired":
                           (ea["E1_B"]["mean"] + eb["E1_B"]["mean"])}
                rows_b = _design_rows(T, unb, None, "B-unpaired")
                art["design_table_arm_b"] = {
                    "headline_pair": hp, "T_shared": T, "rows": rows_b,
                    "note": "Arm B has no cross-agent paired estimand in "
                            "the frozen model (agents fitted "
                            "independently); its MDE uses the unpaired "
                            "construction with Arm B components "
                            "(SS3.4 unpaired variant)."}
            art["pooled_rho"] = {
                "arm_a": aa["pooled_binary"]["rho"],
                "arm_b": (ab["pooled_binary"]["rho_B_mean"] if ab
                          else None),
                "arm_b_interval": (
                    ab["pooled_binary"]["rho_B_ci95"] if ab else None),
            }
        # falsifier rows (SS4.3)
        rows_f = {}
        pa = aa["pooled_binary"]
        iv_a = aa["bootstrap_binary"]["intervals"]["rho"]["bca"]
        sens_a = []
        rows_f["arm_a"] = {
            "rho": pa["rho"], "interval_bca": list(iv_a),
            "verdict": _falsifier_row(pa["rho"], tuple(iv_a), sens_a)}
        if ab:
            pb = ab["pooled_binary"]
            sens_b = []
            if ab.get("pooled_binary_sens_prior"):
                sens_b.append(ab["pooled_binary_sens_prior"]["rho_B_mean"])
            if ab.get("pooled_binary_singletons"):
                sens_b.append(ab["pooled_binary_singletons"]["rho_B_mean"])
            verdict_b = _falsifier_row(
                pb["rho_B_mean"],
                (pb["rho_B_ci95"][0], pb["rho_B_ci95"][1]), sens_b)
            # SS6.4: a FAILED fit for a headline-pair agent, or for
            # more than a quarter of the benchmark's agents, makes
            # the Arm B verdict INDETERMINATE regardless of rho.
            failed = set(ab.get("failed_agents_primary", []))
            n_agents_b = len(ab["per_agent"])
            headline_agents = set()
            if hp:
                headline_agents = set(hp["pair"].split(" || "))
            if (failed & headline_agents) or \
                    len(failed) / max(n_agents_b, 1) > 0.25:
                verdict_b = "INDETERMINATE (fit failure, SS6.4)"
            rows_f["arm_b"] = {
                "rho": pb["rho_B_mean"],
                "interval": pb["rho_B_ci95"],
                "sensitivity_values": sens_b,
                "verdict": verdict_b,
                "failed_agents": sorted(failed),
                "misfit_share_primary": ab.get("misfit_share_primary"),
                "prior_sensitivity": ab.get("prior_sensitivity")}
        art["falsifier"] = rows_f
        # audit (SS3.5): rows sourced in audit_sources.json; the pair
        # estimate is recomputed on the row's task subset when a
        # task_prefix is given; asymmetric designs (R1 != R2) use the
        # per-agent run variances directly.
        audit_rows = []
        if audit_sources:
            records_for_audit = None
            for row in audit_sources.get(bench, []):
                a1, a2 = row["agent_1"], row["agent_2"]
                prefix = row.get("task_prefix")
                if prefix:
                    if records_for_audit is None:
                        records_for_audit = load_table(bench)
                    sub = [r for r in records_for_audit
                           if r["task"].startswith(prefix)]
                    _ta, n1, k1, _xa = agent_cells(sub, a1)
                    _tb, n2, k2, _xb = agent_cells(sub, a2)
                    shr = sorted(set(_ta) & set(_tb))
                    ia = {t: j for j, t in enumerate(_ta)}
                    ib = {t: j for j, t in enumerate(_tb)}
                    nn1 = np.array([n1[ia[t]] for t in shr])
                    kk1 = np.array([k1[ia[t]] for t in shr])
                    nn2 = np.array([n2[ib[t]] for t in shr])
                    kk2 = np.array([k2[ib[t]] for t in shr])
                    both = (nn1 >= 2) & (nn2 >= 2)
                    if both.sum() < 2:
                        audit_rows.append({**row, "status":
                                           "pair has <2 shared tasks "
                                           "in subset"})
                        continue
                    pe = _paired_est(nn1[both], kk1[both],
                                     nn2[both], kk2[both])
                    pe["n_shared_tasks_ge2"] = int(both.sum())
                else:
                    key = f"{a1} || {a2}"
                    key_r = f"{a2} || {a1}"
                    pe = aa["pairs"].get(key) or aa["pairs"].get(key_r)
                    if pe is None:
                        audit_rows.append({**row, "status":
                                           "pair not in census run "
                                           "table"})
                        continue
                T_d = row["T"]
                if "R1" in row:
                    R1, R2 = row["R1"], row["R2"]
                    var = (pe["task_diff_var"] + pe["run_var_1"] / R1
                           + pe["run_var_2"] / R2) / T_d
                    m = mde_mod.Z_MULT * math.sqrt(var)
                    design_note = (f"asymmetric design R1={R1}, "
                                   f"R2={R2} (per-agent run "
                                   f"variances)")
                else:
                    m = mde_mod.mde(T_d, row["R"],
                                    pe["run_var_1"] + pe["run_var_2"],
                                    pe["task_diff_var"])
                    design_note = f"symmetric design R={row['R']}"
                gap = row["gap"]
                cls = ("ABOVE" if gap > m else
                       "BELOW" if gap < m else "AT")
                out_row = {**row, "mde_arm_a_at_design": m,
                           "classification": cls,
                           "design_note": design_note,
                           "pair_T_in_census": pe["n_shared_tasks_ge2"],
                           "pair_components": {
                               "task_diff_var": pe["task_diff_var"],
                               "run_var_1": pe["run_var_1"],
                               "run_var_2": pe["run_var_2"]}}
                if ab and a1 in ab["per_agent"] and a2 in ab["per_agent"]:
                    ea, eb = ab["per_agent"][a1], ab["per_agent"][a2]
                    if "R1" in row:
                        var_b = ((ea["E1_B"]["mean"] + eb["E1_B"]["mean"])
                                 + ea["E2_B"]["mean"] / R1
                                 + eb["E2_B"]["mean"] / R2) / T_d
                    else:
                        var_b = ((ea["E1_B"]["mean"] + eb["E1_B"]["mean"])
                                 + (ea["E2_B"]["mean"]
                                    + eb["E2_B"]["mean"]) / row["R"]) / T_d
                    m_b = mde_mod.Z_MULT * math.sqrt(var_b)
                    cls_b = ("ABOVE" if gap > m_b else
                             "BELOW" if gap < m_b else "AT")
                    out_row["mde_arm_b_unpaired_at_design"] = m_b
                    out_row["classification_arm_b"] = cls_b
                    out_row["arm_sensitive"] = cls_b != cls
                    out_row["arm_b_note"] = (
                        "Arm B MDE uses the benchmark-level per-agent "
                        "components (unpaired construction); Arm B has "
                        "no per-subset paired estimand in the frozen "
                        "model.")
                audit_rows.append(out_row)
        art["audit"] = audit_rows
        _atomic_json(art, os.path.join(CENSUS, f"tables_{bench}.json"))
        _progress(f"tables_{bench}", falsifier=rows_f)
    _progress("tables", done=True)


# ------------------------------------------------------------ report
def stage_report():
    lines = ["# Stage 7 census — results (Area 1: agent-benchmark "
             "metrology)", ""]
    with open(os.path.join(CENSUS, "ingest_ledger.json")) as f:
        ledger = json.load(f)
    lines.append("## Ingest (SS5.1)")
    for bench in BENCHES:
        m = ledger["benchmarks"][bench]
        lines.append(f"- {bench}: {m['n_records']} run outcomes, "
                     f"{m['n_agents']} agents, {m['n_tasks']} tasks; "
                     f"cells with n>=2: {m['share_cells_ge2']:.3f}; "
                     f"runs in such cells: "
                     f"{m['share_runs_in_ge2_cells']:.3f}.")
    for bench in ("B2", "B5", "B6"):
        m = ledger["benchmarks"].get(bench)
        if m:
            lines.append(f"- {bench}: FAIL at ingest verification — "
                         f"{m.get('fail_reason', '')}")
    lines.append("")
    for bench in BENCHES:
        with open(os.path.join(CENSUS, f"tables_{bench}.json")) as f:
            tb = json.load(f)
        lines.append(f"## {bench}")
        pr = tb.get("pooled_rho", {})
        lines.append(f"- Pooled rho: Arm A {pr.get('arm_a')}, "
                     f"Arm B {pr.get('arm_b')} "
                     f"(interval {pr.get('arm_b_interval')}).")
        for arm, row in tb.get("falsifier", {}).items():
            lines.append(f"- Falsifier ({arm}): rho={row['rho']:.4f} -> "
                         f"**{row['verdict']}**")
        lines.append("")
    path = os.path.join(CENSUS, "CENSUS_RESULTS.md")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    _progress("report", path=path)


STAGES = {"ingest": stage_ingest, "arm-a": stage_arm_a,
          "arm-b": stage_arm_b, "arm-b-summary": stage_arm_b_summary,
          "tables": stage_tables, "report": stage_report}

if __name__ == "__main__":
    stage = sys.argv[1]
    kw = {}
    if len(sys.argv) > 2:
        kw["only_bench"] = sys.argv[2]
    STAGES[stage](**kw) if kw else STAGES[stage]()
