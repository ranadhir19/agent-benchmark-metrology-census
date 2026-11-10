"""P2-A1 FALLBACK replication: Bjarnason et al. (2026) single-run pass@1 spread.

Target (TOP_OF_FIELD_DOSSIER.md S5 fallback, frozen): from the public
trajectory release of Bjarnason, Silva & Monperrus, "On Randomness in
Agentic Evals" (arXiv:2602.07150), reproduce

  * single-run pass@1 spread 2.2-6.0 percentage points across the paper's
    12 configurations (6 model-temperature settings x 2 scaffolds), and
  * SD > 1.5 percentage points at temperature 0,

with tolerance +/-1.0 point on the spread endpoints.

Release (verified 2026-10-31; linked as the "Data" badge in arXiv v3):
  Hugging Face dataset ASSERT-KTH/agentic-evals-artifacts, revision
  5db0c4b69382d160a313d7ceaded915398c63e13, licence CC-BY-4.0,
  public, not gated. 47.9 GB total (full trajectories); this adapter
  downloads ONLY the per-run SWE-bench harness result JSONs
  (120 files, ~5.8 MB total) -- the one small file per run directory
  (< 100 KB, .json) holding resolved_ids / resolved_instances /
  total_instances. Single-run pass@1 for run j is the plain aggregation
  r_j = resolved_instances / total_instances (paper S2.3, eq. 2).
  No estimator is invented or changed here; adaptation is at ingest
  only (release layout -> per-config arrays of r_j).

Per config we report mean / min / max / spread (max-min) and the SD of
the 10 r_j values under both ddof=0 (population) and ddof=1 (sample),
because the paper's Table 1 does not state its SD convention; the
comparison against the published rounded Table 1 values is reported
for both, and the frozen verdict uses the spread endpoints (which do
not depend on the SD convention) plus the temp-0 SD claim checked
under both conventions.

Usage:
  nice -n 10 python3 code/bjarnason_fallback.py --out results/<file>.json
Deterministic: same release revision in -> same numbers out.
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

DATASET = "ASSERT-KTH/agentic-evals-artifacts"
REVISION = "5db0c4b69382d160a313d7ceaded915398c63e13"
TREE_URL = (f"https://huggingface.co/api/datasets/{DATASET}/tree/main"
            f"?recursive=true&expand=false")
RESOLVE_BASE = (f"https://huggingface.co/datasets/{DATASET}"
                f"/resolve/{REVISION}/")

# The paper's 12 configurations: (release top-level directory,
# scaffold, model, temperature). Directory names are copied verbatim
# from the release tree; temperatures are the paper's Table 1 / Table 3
# values (default temperature per model, plus the temp-0 settings).
CONFIGS = [
    ("nano-agent-Qwen_Qwen3-32B", "nano-agent", "Qwen3-32B", 0.6),
    ("nano-agent-agentica-org_DeepSWE-Preview", "nano-agent",
     "DeepSWE-preview", 1.0),
    ("nano-agent-mistral_devstral-2512", "nano-agent", "Devstral-2", 0.2),
    ("nano-agent-Qwen_Qwen3-32B-temp0", "nano-agent", "Qwen3-32B", 0.0),
    ("nano-agent-agentica-org_DeepSWE-Preview__temp0", "nano-agent",
     "DeepSWE-preview", 0.0),
    ("nano-agent-mistral_devstral-2512__temp0", "nano-agent",
     "Devstral-2", 0.0),
    ("r2e-gym-Qwen_Qwen3-32B", "r2e-gym", "Qwen3-32B", 0.6),
    ("r2e-gym-agentica-org__DeepSWE-preview", "r2e-gym",
     "DeepSWE-preview", 1.0),
    ("r2e-gym-mistral_devstral-2512", "r2e-gym", "Devstral-2", 0.2),
    ("r2e-gym-Qwen_Qwen3-32B__temp0", "r2e-gym", "Qwen3-32B", 0.0),
    ("r2e-gym-agentica-org__DeepSWE-preview__temp0", "r2e-gym",
     "DeepSWE-preview", 0.0),
    ("r2e-gym-mistral_devstral-2512__temp0", "r2e-gym", "Devstral-2", 0.0),
]

# Published Table 1 (arXiv:2602.07150v3, identical in v1): per config
# (mean %, SD %, min %, max %), transcribed from the paper.
PUBLISHED = {
    ("nano-agent", "Qwen3-32B", 0.6): (16.4, 0.7, 15.0, 17.2),
    ("nano-agent", "DeepSWE-preview", 1.0): (31.4, 1.0, 28.8, 32.4),
    ("nano-agent", "Devstral-2", 0.2): (63.5, 1.1, 61.8, 65.0),
    ("nano-agent", "Qwen3-32B", 0.0): (16.4, 1.2, 14.4, 18.0),
    ("nano-agent", "DeepSWE-preview", 0.0): (20.4, 1.0, 18.2, 21.4),
    ("nano-agent", "Devstral-2", 0.0): (63.8, 1.6, 60.6, 66.6),
    ("r2e-gym", "Qwen3-32B", 0.6): (23.9, 1.4, 21.4, 26.4),
    ("r2e-gym", "DeepSWE-preview", 1.0): (34.4, 1.5, 31.6, 37.0),
    ("r2e-gym", "Devstral-2", 0.2): (34.9, 1.5, 32.2, 37.0),
    ("r2e-gym", "Qwen3-32B", 0.0): (22.3, 1.8, 19.8, 25.2),
    ("r2e-gym", "DeepSWE-preview", 0.0): (19.2, 1.5, 17.0, 21.6),
    ("r2e-gym", "Devstral-2", 0.0): (35.4, 1.7, 32.0, 37.8),
}

FROZEN = {"spread_min_points": 2.2, "spread_max_points": 6.0,
          "spread_tolerance_points": 1.0, "temp0_sd_claim_points": 1.5}


def fetch(url, dest=None):
    req = urllib.request.Request(
        url, headers={"User-Agent": "p2-a1-fallback-replication"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if dest is not None:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
    return data


def select_eval_files(tree):
    """Ingest rule: per run directory, the eval result is the sole
    .json file under 100 KB (the other .json in r2e-gym run dirs is the
    multi-MB predictions file; trajectories are .jsonl). Returns
    {top_level_dir: [tree entries sorted by path]} and asserts the
    frozen design: 12 configs x 10 runs, exactly one eval file each."""
    by_dir = {}
    for e in tree:
        if e.get("type") != "file":
            continue
        path = e["path"]
        if not path.endswith(".json") or e.get("size", 0) >= 100_000:
            continue
        top = path.split("/")[0]
        by_dir.setdefault(top, []).append(e)
    selected = {}
    for top, _scaffold, _model, _temp in CONFIGS:
        entries = sorted(by_dir.get(top, []), key=lambda e: e["path"])
        if len(entries) != 10:
            raise ValueError(
                f"design mismatch: {top} has {len(entries)} eval files, "
                "expected 10")
        selected[top] = entries
    return selected


def run_rates(eval_json):
    """Validate one SWE-bench harness result and return its r_j (%)."""
    for key in ("resolved_ids", "unresolved_ids", "resolved_instances",
                "total_instances"):
        if key not in eval_json:
            raise ValueError(f"eval JSON missing key {key!r}")
    resolved = eval_json["resolved_ids"]
    unresolved = eval_json["unresolved_ids"]
    if len(resolved) != eval_json["resolved_instances"]:
        raise ValueError("len(resolved_ids) != resolved_instances")
    if set(resolved) & set(unresolved):
        raise ValueError("resolved/unresolved ID sets overlap")
    total = eval_json["total_instances"]
    return 100.0 * eval_json["resolved_instances"] / total, {
        "total_instances": total,
        "resolved_instances": eval_json["resolved_instances"],
        "unresolved_instances": eval_json.get("unresolved_instances"),
        "submitted_instances": eval_json.get("submitted_instances"),
        "completed_instances": eval_json.get("completed_instances"),
        "empty_patch_instances": eval_json.get("empty_patch_instances"),
        "error_instances": eval_json.get("error_instances"),
        "n_resolved_ids": len(resolved),
        "n_unresolved_ids": len(unresolved),
    }


def summarise(rates):
    r = np.asarray(rates, dtype=float)
    return {
        "n_runs": int(len(r)),
        "rates_points": [float(x) for x in r],
        "mean_points": float(np.mean(r)),
        "sd_points_ddof0": float(np.std(r, ddof=0)),
        "sd_points_ddof1": float(np.std(r, ddof=1)),
        "min_points": float(np.min(r)),
        "max_points": float(np.max(r)),
        "spread_points": float(np.max(r) - np.min(r)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="/tmp/bjarnason_fallback_cache")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    tree = json.loads(fetch(TREE_URL))
    selected = select_eval_files(tree)

    configs_out = []
    for top, scaffold, model, temp in CONFIGS:
        rates, file_records = [], []
        for e in selected[top]:
            dest = os.path.join(args.cache, e["path"])
            if os.path.exists(dest) and \
                    os.path.getsize(dest) == e["size"]:
                with open(dest, "rb") as f:
                    data = f.read()
            else:
                data = fetch(RESOLVE_BASE + urllib.parse.quote(e["path"]),
                             dest)
            if len(data) != e["size"]:
                raise ValueError(f"size mismatch for {e['path']}")
            rate, checks = run_rates(json.loads(data))
            rates.append(rate)
            file_records.append({
                "path": e["path"], "size": e["size"],
                "sha256": hashlib.sha256(data).hexdigest(),
                **checks})
        s = summarise(rates)
        pub = PUBLISHED[(scaffold, model, temp)]
        s.update({
            "release_dir": top, "scaffold": scaffold, "model": model,
            "temperature": temp,
            "published_table1": {"mean_points": pub[0], "sd_points": pub[1],
                                 "min_points": pub[2], "max_points": pub[3],
                                 "spread_points": pub[3] - pub[2]},
            "deviation_vs_published": {
                "mean_points": s["mean_points"] - pub[0],
                "sd_points_ddof0": s["sd_points_ddof0"] - pub[1],
                "sd_points_ddof1": s["sd_points_ddof1"] - pub[1],
                "min_points": s["min_points"] - pub[2],
                "max_points": s["max_points"] - pub[3],
                "spread_points": s["spread_points"] - (pub[3] - pub[2]),
            },
            "files": file_records,
        })
        configs_out.append(s)

    spreads = [c["spread_points"] for c in configs_out]
    temp0 = [c for c in configs_out if c["temperature"] == 0.0]
    spread_min, spread_max = min(spreads), max(spreads)
    tol = FROZEN["spread_tolerance_points"]
    spread_pass = (abs(spread_min - FROZEN["spread_min_points"]) <= tol
                   and abs(spread_max - FROZEN["spread_max_points"]) <= tol)
    temp0_sd = {
        "sd_points_ddof0_per_config": [c["sd_points_ddof0"] for c in temp0],
        "sd_points_ddof1_per_config": [c["sd_points_ddof1"] for c in temp0],
        "max_sd_ddof0": max(c["sd_points_ddof0"] for c in temp0),
        "max_sd_ddof1": max(c["sd_points_ddof1"] for c in temp0),
        "n_configs_sd_gt_1.5_ddof0":
            sum(c["sd_points_ddof0"] > 1.5 for c in temp0),
        "n_configs_sd_gt_1.5_ddof1":
            sum(c["sd_points_ddof1"] > 1.5 for c in temp0),
        "published_temp0_sds": [PUBLISHED[(c["scaffold"], c["model"], 0.0)][1]
                                for c in temp0],
    }
    sd_claim_holds = (temp0_sd["max_sd_ddof0"] > FROZEN["temp0_sd_claim_points"]
                      or temp0_sd["max_sd_ddof1"]
                      > FROZEN["temp0_sd_claim_points"])
    verdict = "PASS" if (spread_pass and sd_claim_holds) else "FAIL"

    out = {
        "task": ("P2-A1 FALLBACK: reproduce Bjarnason et al. (2026) "
                 "single-run pass@1 spread from the public trajectory "
                 "release (TOP_OF_FIELD_DOSSIER.md S5 fallback)"),
        "paper": {"authors": "Bjarnason, Silva & Monperrus",
                  "title": "On Randomness in Agentic Evals",
                  "arxiv": "2602.07150", "version_checked": "v3 (2026-03-25); "
                  "Table 1 identical in v1"},
        "release": {"dataset": DATASET, "revision": REVISION,
                    "url": f"https://huggingface.co/datasets/{DATASET}",
                    "licence": "CC-BY-4.0", "public": True, "gated": False,
                    "total_files_tree": sum(1 for e in tree
                                            if e.get("type") == "file"),
                    "total_bytes_tree": sum(e.get("size", 0) for e in tree
                                            if e.get("type") == "file"),
                    "eval_files_used": sum(len(v)
                                           for v in selected.values()),
                    "eval_bytes_used": sum(e["size"] for v in selected.values()
                                           for e in v)},
        "frozen_targets": FROZEN,
        "configs": configs_out,
        "headline": {
            "spread_min_points_measured": spread_min,
            "spread_max_points_measured": spread_max,
            "spread_endpoints_within_tolerance": spread_pass,
            "temp0_sd": temp0_sd,
            "temp0_sd_claim_holds": sd_claim_holds,
        },
        "verdict": verdict,
    }
    out_path = args.out or os.path.join(
        os.path.dirname(HERE), "results", "p2_a1_fallback_replication.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"headline": out["headline"], "verdict": verdict,
                      "per_config_spread": spreads}, indent=2))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
