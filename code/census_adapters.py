"""Stage 7 census adapters: build canonical run tables (EXPERIMENTS.md
SS5.1) for the benchmarks that pass ingest verification.

One canonical record per observed run outcome:
  {"benchmark", "agent", "task", "run", "y_bin", "y_cont"}
with "run" a deterministic 0-based index inside the (agent, task) cell.
Adaptation is at ingest only; no estimator lives here.

B1: METR public evaluation data, task_source in {HCAST, RE-Bench},
    from the pinned v1_0 / v1_1 run files (copies under
    results/census/data/metr/, hashes in the ingest ledger). Record
    validation mirrors code/ingest.py exactly; run_id de-duplication:
    an identical re-listing of a run_id counts once, a conflicting
    re-listing (same run_id, different recorded fields) is excluded
    and listed (SS5.1(vi) style provenance, extended to values).
B3: tau-bench historical trajectories (Sierra Research release,
    MIT), files under results/census/data/tau_bench/.
B4: Bjarnason et al. (2026) ASSERT-KTH release (CC-BY-4.0), per-run
    SWE-bench harness eval JSONs selected by the frozen rule in
    code/bjarnason_fallback.py (imported, not re-implemented).
"""
import collections
import hashlib
import json
import os
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
AREA = os.path.dirname(HERE)
CENSUS = os.path.join(AREA, "results", "census")
DATA = os.path.join(CENSUS, "data")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_table(bench, records):
    out = os.path.join(DATA, f"{bench}_run_table.jsonl")
    tmp = out + ".tmp"
    with open(tmp, "w") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    os.replace(tmp, out)
    return out


def _cell_stats(records):
    cells = collections.Counter((r["agent"], r["task"]) for r in records)
    n_hist = collections.Counter(cells.values())
    runs_in_ge2 = sum(n for n in cells.values() if n >= 2)
    return {
        "n_cells": len(cells),
        "cell_n_histogram": {str(k): v for k, v in sorted(n_hist.items())},
        "share_cells_ge2": (sum(1 for n in cells.values() if n >= 2)
                            / len(cells)) if cells else 0.0,
        "share_runs_in_ge2_cells": runs_in_ge2 / len(records) if records else 0.0,
        "n_agents": len({r["agent"] for r in records}),
        "n_tasks": len({r["task"] for r in records}),
        "n_records": len(records),
    }


def _agents_summary(records):
    by_agent = collections.defaultdict(list)
    for r in records:
        by_agent[r["agent"]].append(r)
    out = {}
    for agent, rs in sorted(by_agent.items()):
        cells = collections.Counter(r["task"] for r in rs)
        ge2 = {t: n for t, n in cells.items() if n >= 2}
        out[agent] = {
            "n_records": len(rs),
            "n_tasks": len(cells),
            "n_cells_ge2": len(ge2),
            "runs_in_ge2_cells": sum(ge2.values()),
            "mean_y_bin_ge2": (sum(r["y_bin"] for r in rs
                                   if cells[r["task"]] >= 2)
                               / sum(ge2.values())) if ge2 else None,
        }
    return out


# ---------------------------------------------------------------- B1
def build_b1():
    files = [os.path.join(DATA, "metr", "runs_v1_0.jsonl"),
             os.path.join(DATA, "metr", "runs_v1_1.jsonl")]
    meta = {"benchmark": "B1", "files": [], "violations": []}
    seen = {}          # run_id -> (model, task, y_bin, y_cont, source)
    kept = []          # (run_id, model, task, y_bin, y_cont, source, fname)
    n_dup = 0
    conflicts = []
    conflict_ids = set()
    for path in files:
        fname = os.path.basename(path)
        n_lines = 0
        src_counts = collections.Counter()
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                n_lines += 1
                rec = json.loads(line)
                src = rec.get("task_source")
                src_counts[src] += 1
                if src not in ("HCAST", "RE-Bench"):
                    continue
                yb, yc = rec.get("score_binarized"), rec.get("score_cont")
                if yb not in (0, 1) or not isinstance(yc, (int, float)) \
                        or not (0.0 <= float(yc) <= 1.0):
                    meta["violations"].append(
                        {"file": fname, "run_id": rec.get("run_id"),
                         "score_binarized": yb, "score_cont": yc})
                    continue
                key = (rec["model"], rec["task_id"], int(yb), float(yc), src)
                rid = rec["run_id"]
                if rid in conflict_ids:
                    continue
                if rid in seen:
                    if seen[rid] == key:
                        n_dup += 1
                    else:
                        conflict_ids.add(rid)
                        conflicts.append({"run_id": rid,
                                          "first": seen[rid],
                                          "later": key, "file": fname})
                        kept = [k for k in kept if k[0] != rid]
                        del seen[rid]
                    continue
                seen[rid] = key
                kept.append((rid,) + key + (fname,))
        meta["files"].append({"file": fname, "sha256": _sha256(path),
                              "n_lines": n_lines,
                              "task_source_counts": dict(src_counts)})
    meta["n_identical_duplicate_run_ids"] = n_dup
    meta["conflicting_run_ids"] = conflicts
    meta["n_records_after_filter_dedup"] = len(kept)
    # deterministic per-cell run indices (sorted run_id)
    kept.sort(key=lambda k: (k[1], k[2], k[0]))
    records = []
    cell_counter = collections.Counter()
    for rid, model, task, yb, yc, src, fname in kept:
        idx = cell_counter[(model, task)]
        cell_counter[(model, task)] += 1
        records.append({"benchmark": "B1", "agent": model, "task": task,
                        "run": idx, "y_bin": yb, "y_cont": yc,
                        "task_source": src, "run_id": rid,
                        "source_file": fname})
    _write_table("B1", records)
    meta.update(_cell_stats(records))
    meta["agents"] = _agents_summary(records)
    meta["y_cont_in_unit_share"] = (
        sum(1 for r in records if 0.0 <= r["y_cont"] <= 1.0) / len(records))
    return records, meta


# ---------------------------------------------------------------- B3
B3_FILES = [
    ("trajs-gpt-4o-retail.json", "gpt-4o", "retail"),
    ("trajs-gpt-4o-airline.json", "gpt-4o", "airline"),
    ("trajs-claude-3.5-sonnet-new-retail.json", "sonnet-35-new", "retail"),
    ("trajs-claude-3.5-sonnet-new-airline.json", "sonnet-35-new", "airline"),
]


def build_b3():
    meta = {"benchmark": "B3", "files": []}
    records = []
    for fname, agent, domain in B3_FILES:
        path = os.path.join(DATA, "tau_bench", fname)
        with open(path) as f:
            trajs = json.load(f)
        rewards = collections.Counter()
        trials = collections.defaultdict(set)
        for t in trajs:
            r = t["reward"]
            rewards[r] += 1
            if r not in (0.0, 1.0):
                raise ValueError(f"B3 non-binary reward {r} in {fname}")
            trials[t["task_id"]].add(int(t["trial"]))
            records.append({"benchmark": "B3", "agent": agent,
                            "task": f"{domain}:{t['task_id']}",
                            "run": int(t["trial"]), "y_bin": int(r),
                            "y_cont": None, "domain": domain,
                            "source_file": fname})
        meta["files"].append({
            "file": fname, "sha256": _sha256(path), "agent": agent,
            "domain": domain, "n_trajectories": len(trajs),
            "reward_values": {str(k): v for k, v in rewards.items()},
            "n_tasks": len(trials),
            "trials_per_task": sorted({len(v) for v in trials.values()}),
        })
    records.sort(key=lambda r: (r["agent"], r["task"], r["run"]))
    _write_table("B3", records)
    meta.update(_cell_stats(records))
    meta["agents"] = _agents_summary(records)
    return records, meta


# ---------------------------------------------------------------- B4
def build_b4():
    import sys
    sys.path.insert(0, HERE)
    from code import bjarnason_fallback as fb

    cache = os.path.join(DATA, "bjarnason")
    os.makedirs(cache, exist_ok=True)
    tree = json.loads(fb.fetch(fb.TREE_URL))
    selected = fb.select_eval_files(tree)
    meta = {"benchmark": "B4",
            "dataset": fb.DATASET, "revision": fb.REVISION, "configs": {}}
    records = []
    total_outcomes = 0
    for top, scaffold, model, temp in fb.CONFIGS:
        agent = f"{scaffold}|{model}|temp={temp:g}"
        entries = selected[top]
        cfg_rates = []
        cfg_outcomes = 0
        cfg_hashes = []
        for run_idx, e in enumerate(entries):
            dest = os.path.join(cache, e["path"])
            if os.path.exists(dest) and os.path.getsize(dest) == e["size"]:
                with open(dest, "rb") as f:
                    data = f.read()
            else:
                data = fb.fetch(fb.RESOLVE_BASE
                                + urllib.parse.quote(e["path"]), dest)
            if len(data) != e["size"]:
                raise ValueError(f"B4 size mismatch for {e['path']}")
            cfg_hashes.append(hashlib.sha256(data).hexdigest())
            ev = json.loads(data)
            rate, checks = fb.run_rates(ev)
            cfg_rates.append(rate)
            resolved = set(ev["resolved_ids"])
            unresolved = set(ev["unresolved_ids"])
            cfg_outcomes += len(resolved) + len(unresolved)
            for inst in sorted(resolved | unresolved):
                records.append({"benchmark": "B4", "agent": agent,
                                "task": inst, "run": run_idx,
                                "y_bin": 1 if inst in resolved else 0,
                                "y_cont": None,
                                "source_file": e["path"]})
        meta["configs"][agent] = {
            "release_dir": top, "n_runs": len(entries),
            "run_rates_pct": cfg_rates,
            "mean_rate_pct": sum(cfg_rates) / len(cfg_rates),
            "n_outcomes": cfg_outcomes,
            "file_sha256": cfg_hashes,
        }
        total_outcomes += cfg_outcomes
    records.sort(key=lambda r: (r["agent"], r["task"], r["run"]))
    _write_table("B4", records)
    meta["n_outcomes_crosscheck"] = total_outcomes
    meta.update(_cell_stats(records))
    meta["agents"] = _agents_summary(records)
    return records, meta
