"""Ingest adapters -> canonical run table.

Canonical run record: dict with keys
  benchmark (str), agent (str), task (str), run (str),
  y_bin (int 0/1), y_cont (float or None), task_weight (float or None)

Adapters isolate source quirks. The METR adapter is built against the real
flagship-reused files (flagship_work/data/metr/runs_v*.jsonl), whose records
carry: task_id, task_family, run_id, model, score_cont, score_binarized,
task_source, task_version, equal_task_weight, ...
"""
import json


def iter_metr_runs(paths, task_source=None):
    """Stream METR run-level JSONL files, yielding canonical records.

    Only the fields the pipeline needs are read; memory stays O(1) in rows.
    """
    for path in paths:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if task_source is not None and r.get("task_source") != task_source:
                    continue
                yb = r.get("score_binarized")
                if yb is None:
                    continue
                yield {
                    "benchmark": "METR",
                    "agent": r["model"],
                    "task": r["task_id"],
                    "run": r["run_id"],
                    "y_bin": int(yb),
                    "y_cont": r.get("score_cont"),
                    "task_weight": r.get("equal_task_weight"),
                }


def build_cells(records):
    """Aggregate canonical records into a cell table.

    Returns dict[(agent, task)] -> {"n": int, "k": int (binary successes),
    "cont_sum": float, "weight": float or None}.
    """
    cells = {}
    for rec in records:
        key = (rec["agent"], rec["task"])
        c = cells.get(key)
        if c is None:
            c = cells[key] = {"n": 0, "k": 0, "cont_sum": 0.0,
                              "weight": rec.get("task_weight")}
        c["n"] += 1
        c["k"] += rec["y_bin"]
        if rec.get("y_cont") is not None:
            c["cont_sum"] += rec["y_cont"]
    return cells


def coverage_counts(cells):
    """Outcome-free coverage profile (used by frozen slice-selection rules).

    Returns dict[agent] -> {"tasks_ge2": int, "tasks_total": int,
    "runs_in_ge2_cells": int}.
    """
    cov = {}
    for (agent, _task), c in cells.items():
        a = cov.setdefault(agent, {"tasks_ge2": 0, "tasks_total": 0,
                                   "runs_in_ge2_cells": 0})
        a["tasks_total"] += 1
        if c["n"] >= 2:
            a["tasks_ge2"] += 1
            a["runs_in_ge2_cells"] += c["n"]
    return cov


def agent_task_arrays(cells, agent):
    """Per-task (n_runs, successes) arrays for one agent, tasks sorted."""
    items = sorted((task, c) for (a, task), c in cells.items() if a == agent)
    tasks = [t for t, _ in items]
    n = [c["n"] for _, c in items]
    k = [c["k"] for _, c in items]
    return tasks, n, k
