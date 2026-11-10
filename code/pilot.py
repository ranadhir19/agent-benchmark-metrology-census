"""Bounded deep-test pilot: ONE benchmark end-to-end (METR, B1).

Frozen slice rule (pre-registration, EXPERIMENTS.md): within
runs_v1_0.jsonl, task_source = the source with the most records;
pilot agent = the model with the most tasks having >= 2 runs in that
source (ties: most runs in those cells, then name). The paired agent
for the MDE table = the other model sharing the most >= 2-run tasks
with the pilot agent. All choices are functions of coverage counts
only, never of outcomes.

Outputs results/pilot_metr_v1_0.json and prints a compact summary.
CPU-light; streaming ingest; run under `nice`.
"""
import argparse
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from code import components, ingest, mde  # noqa: E402

DEFAULT_FILE = ("/home/hatch/workspace/goals/10-journal-papers-submitted-to-good-"
                "journals/hidden_files/flagship_work/data/metr/runs_v1_0.jsonl")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT_FILE)
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261030)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    # Pass 1: outcome-free line counts per task_source.
    src_counts = collections.Counter()
    total_lines = 0
    with open(args.file) as f:
        for line in f:
            if not line.strip():
                continue
            total_lines += 1
            src_counts[json.loads(line).get("task_source")] += 1
    source = sorted(src_counts.items(), key=lambda kv: (-kv[1], str(kv[0])))[0][0]

    # Pass 2: cells for the chosen source.
    records = list(ingest.iter_metr_runs([args.file], task_source=source))
    cells = ingest.build_cells(records)
    cov = ingest.coverage_counts(cells)
    pilot_agent = sorted(cov.items(),
                         key=lambda kv: (-kv[1]["tasks_ge2"],
                                         -kv[1]["runs_in_ge2_cells"],
                                         kv[0]))[0][0]

    tasks, n_all, k_all = ingest.agent_task_arrays(cells, pilot_agent)
    ge2 = [(t, nn, kk) for t, nn, kk in zip(tasks, n_all, k_all) if nn >= 2]
    n = [x[1] for x in ge2]; k = [x[2] for x in ge2]

    # Anchor: the pilot agent's score on its >=2-run task set, three ways
    # over the SAME records; plus a record-count cross-check.
    pooled = sum(k) / sum(n)
    equal_task = float(sum(kk / nn for nn, kk in zip(n, k)) / len(n))
    wsum, wtot = 0.0, 0.0
    for t, nn, kk in ge2:
        w = cells[(pilot_agent, t)]["weight"] or 0.0
        wsum += w * (kk / nn); wtot += w
    weighted = wsum / wtot if wtot else None
    count_check = (sum(c["n"] for c in cells.values()) == len(records))

    est = components.estimate_components(n, k)
    cis = components.bootstrap_components(n, k, B=args.bootstrap, seed=args.seed)

    # Paired agent + design table on shared >=2-run tasks.
    pilot_tasks = {t for t, _, _ in ge2}
    shared = {}
    for agent in cov:
        if agent == pilot_agent:
            continue
        at, an, ak = ingest.agent_task_arrays(cells, agent)
        amap = {t: (nn, kk) for t, nn, kk in zip(at, an, ak) if nn >= 2}
        common = pilot_tasks & set(amap)
        shared[agent] = (len(common), amap)
    paired_agent = sorted(shared.items(),
                          key=lambda kv: (-kv[1][0], kv[0]))[0][0]
    n_common, amap = shared[paired_agent]
    pmap = {t: (nn, kk) for t, nn, kk in ge2}
    common_tasks = sorted(pilot_tasks & set(amap))
    pa_n = [pmap[t][0] for t in common_tasks]; pa_k = [pmap[t][1] for t in common_tasks]
    pb_n = [amap[t][0] for t in common_tasks]; pb_k = [amap[t][1] for t in common_tasks]
    est_a = components.estimate_components(pa_n, pa_k)
    est_b = components.estimate_components(pb_n, pb_k)
    task_diff = components.paired_task_diff_variance(pa_n, pa_k, pb_n, pb_k)
    table = mde.design_table(len(common_tasks),
                             est_a["sigma2_run"] + est_b["sigma2_run"],
                             task_diff)

    # Pass 3: continuous-outcome components for the pilot agent (secondary).
    cont_cells = collections.defaultdict(list)
    for rec in ingest.iter_metr_runs([args.file], task_source=source):
        if rec["agent"] == pilot_agent and rec["y_cont"] is not None:
            cont_cells[rec["task"]].append(rec["y_cont"])
    cont_vals = [v for t, v in sorted(cont_cells.items()) if len(v) >= 2]
    est_cont = components.estimate_components_continuous(cont_vals)

    out = {
        "file": args.file, "file_sha256": sha256_of(args.file),
        "total_lines": total_lines, "task_source_counts": dict(src_counts),
        "chosen_source": source, "n_records_in_source": len(records),
        "coverage": {a: cov[a] for a in sorted(cov)},
        "pilot_agent": pilot_agent,
        "pilot_tasks_ge2": len(ge2), "pilot_runs_in_ge2_cells": int(sum(n)),
        "anchor": {"pooled_run_mean": pooled, "equal_task_mean": equal_task,
                   "metr_weighted_mean": weighted,
                   "record_count_crosscheck": count_check},
        "components_binary": est,
        "bootstrap_ci": {kk: list(vv) for kk, vv in cis.items()},
        "falsifier_threshold": 0.10,
        "rho_vs_threshold": ("ABOVE (thesis survives this benchmark)"
                             if est["rho"] >= 0.10 else
                             "BELOW (kill direction on this benchmark)"),
        "paired_agent": paired_agent, "paired_common_tasks": len(common_tasks),
        "paired_sigma2_task_diff": task_diff,
        "paired_components": {"pilot_on_shared": est_a, "paired_on_shared": est_b},
        "design_table_paired": table,
        "components_continuous_secondary": est_cont,
        "grader_component": ("not identified in METR: grading is programmatic "
                             "(deterministic), so sigma2_grader = 0 by "
                             "construction; environment folded into run-level "
                             "per R1 (estimability limit, reported)"),
        "bootstrap_B": args.bootstrap, "bootstrap_seed": args.seed,
    }
    out_path = args.out or os.path.join(
        os.path.dirname(HERE), "results", "pilot_metr_v1_0.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({kk: out[kk] for kk in
                      ("chosen_source", "pilot_agent", "pilot_tasks_ge2",
                       "anchor", "components_binary", "bootstrap_ci",
                       "rho_vs_threshold", "paired_agent",
                       "paired_common_tasks", "paired_sigma2_task_diff",
                       "components_continuous_secondary")}, indent=2))
    print("design table:", json.dumps(table, indent=2))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
